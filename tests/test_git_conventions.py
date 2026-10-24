"""Branch names and Conventional Commit subjects accepted by the hooks and CI."""

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


def test_commit_subjects_that_match():
    for line in (
        "feat: add a tokenizer",
        "fix(data): handle an empty split",
        "docs: describe the branch rules",
        "exp: try int4 quantization",
        "refactor(cli): move plotting into evaluate",
        "test: cover the loader",
        "chore: remove an unused import",
        "ci: check commit subjects",
        "feat: x",
    ):
        assert git_conventions.header_errors(line) == [], line


def test_commit_subjects_that_do_not_match():
    for line in (
        "",
        "update",
        "Feat: add a tokenizer",
        "feat: ",
        "feat:add a tokenizer",
        "feat(Data): add a loader",
        "feat(data_loader): add a loader",
        "feat: додати токенізатор",
        "wip: still working",
    ):
        assert git_conventions.header_errors(line), line


def test_subject_length_limit_is_the_whole_first_line():
    prefix = "feat: "
    allowed = prefix + ("a" * (git_conventions.MAX_HEADER_LENGTH - len(prefix)))
    assert len(allowed) == git_conventions.MAX_HEADER_LENGTH
    assert git_conventions.header_errors(allowed) == []
    assert git_conventions.header_errors(allowed + "a")


def test_subject_line_ignores_git_comment_lines():
    message = "\n".join(
        [
            "feat: add a tokenizer",
            "",
            "Keeps the vocabulary next to the training script.",
            "# Please enter the commit message for your changes.",
        ]
    )
    assert git_conventions.subject_line(message) == "feat: add a tokenizer"
    assert git_conventions.header_errors(git_conventions.subject_line(message)) == []
