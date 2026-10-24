#!/usr/bin/env python
"""Check branch names.

The local hook and `.github/workflows/conventions.yml` both call this script.
Commit subjects are not checked. See `docs/CONTRIBUTING.md`.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

BRANCH_TYPES = ("feature", "fix", "docs", "exp", "refactor", "test", "chore", "ci")

_KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
BRANCH_PATTERN = rf"^(?:{'|'.join(BRANCH_TYPES)})/{_KEBAB}$"

BRANCH_EXAMPLE = "feature/add-tokenizer"


def branch_errors(name: str) -> list[str]:
    """Return why `name` is not a valid branch, or an empty list."""
    if name == "main":
        return [
            "Refusing to commit on main. "
            f"Create a branch such as {BRANCH_EXAMPLE} and commit there."
        ]
    if re.fullmatch(BRANCH_PATTERN, name) is None:
        allowed = ", ".join(BRANCH_TYPES)
        return [
            f"Branch {name!r} does not match type/short-kebab-case. "
            f"Allowed types: {allowed}. Example: {BRANCH_EXAMPLE}."
        ]
    return []


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def current_branch_name() -> str:
    """Branch under check: the PR head on Actions, otherwise the checkout."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        name = os.environ.get("GITHUB_HEAD_REF", "").strip()
        if not name:
            raise SystemExit(
                "GITHUB_HEAD_REF is empty. The conventions workflow runs on pull_request."
            )
        return name

    result = _git("symbolic-ref", "--short", "HEAD")
    if result.returncode != 0:
        raise SystemExit(
            f"Detached HEAD. Check out a branch such as {BRANCH_EXAMPLE} before committing."
        )
    return result.stdout.strip()


def check_branch() -> int:
    errors = branch_errors(current_branch_name())
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(check_branch())
