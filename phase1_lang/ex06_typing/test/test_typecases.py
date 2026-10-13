"""typecases/ の各ファイルを mypy --strict にかけて、型ヒントの正しさを確かめる。

ok_*.py は、エラーなしで通らなければならない。
ng_*.py は、「# NG」と書いた行だけがエラーにならなければならない。
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

EXERCISE = Path(__file__).resolve().parent.parent
CASES = sorted((EXERCISE / "typecases").glob("*.py"))
OK_CASES = [p for p in CASES if p.name.startswith("ok_")]
NG_CASES = [p for p in CASES if p.name.startswith("ng_")]
ERROR_LINE = re.compile(r"^(?P<path>.+?):(?P<line>\d+): error: (?P<message>.*)$")


@pytest.fixture(scope="module")
def mypy_errors() -> dict[str, dict[int, str]]:
    """src/typed.py と typecases/ をまとめて mypy にかけ、{ファイル名: {行番号: メッセージ}} を返す。"""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--no-error-summary",
            "--no-color-output",
            str(EXERCISE / "src" / "typed.py"),
            *(str(p) for p in CASES),
        ],
        capture_output=True,
        text=True,
        cwd=EXERCISE,
        env=env,
        check=False,
    )
    # 0 はエラーなし、1 は型エラーあり。それ以外は mypy 自体が動いていない。
    assert result.returncode in (0, 1), result.stderr
    errors: dict[str, dict[int, str]] = {}
    for raw in result.stdout.splitlines():
        match = ERROR_LINE.match(raw)
        if match:
            errors.setdefault(Path(match["path"]).name, {})[int(match["line"])] = match["message"]
    return errors


def marked_lines(path: Path) -> set[int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {number for number, line in enumerate(lines, start=1) if line.rstrip().endswith("# NG")}


def require_clean_module(errors: dict[str, dict[int, str]]) -> None:
    # typed.py 自体に型エラーがあると、使う側のエラーが「型ヒントがないから」なのか
    # 「使い方が間違っているから」なのか区別できない。先にそちらをなくす。
    assert errors.get("typed.py", {}) == {}, "先に src/typed.py 自体の型エラーをなくす"


def test_cases_exist() -> None:
    # typecases/ が見つからないと、下のテストが 0 件になって素通りしてしまう。
    assert len(OK_CASES) == 3
    assert len(NG_CASES) == 3


def test_typed_module_has_no_type_errors(mypy_errors: dict[str, dict[int, str]]) -> None:
    require_clean_module(mypy_errors)


@pytest.mark.parametrize("case", OK_CASES, ids=lambda p: p.name)
def test_ok_case_passes(case: Path, mypy_errors: dict[str, dict[int, str]]) -> None:
    require_clean_module(mypy_errors)
    assert mypy_errors.get(case.name, {}) == {}


@pytest.mark.parametrize("case", NG_CASES, ids=lambda p: p.name)
def test_ng_case_is_rejected_only_on_marked_lines(
    case: Path, mypy_errors: dict[str, dict[int, str]]
) -> None:
    require_clean_module(mypy_errors)
    assert set(mypy_errors.get(case.name, {})) == marked_lines(case)
