"""Branch names accepted by the hook and CI."""

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "scripts" / "git_conventions.py"
_SPEC = importlib.util.spec_from_file_location("git_conventions", _PATH)
git_conventions = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(git_conventions)


def test_branch_names_that_match_the_pattern():
    for name in (
        "feature/add-tokenizer",
        "fix/empty-test-split",
        "docs/contribution-rules",
        "exp/int4-quantization",
        "refactor/split-evaluate",
        "test/cover-loader",
        "chore/drop-unused-import",
        "ci/contribution-checks",
        "feature/a",
        "feature/123",
    ):
        assert git_conventions.branch_errors(name) == []


def test_branch_names_that_do_not_match():
    for name in (
        "main",
        "data-exploration",
        "feat/add-tokenizer",
        "feature/Add-Tokenizer",
        "feature/",
        "feature/add_tokenizer",
        "feature/add--tokenizer",
        "Feature/add-tokenizer",
    ):
        assert git_conventions.branch_errors(name)
