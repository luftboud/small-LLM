#!/usr/bin/env python
"""Check branch names and Conventional Commit subjects.

The local hooks and `.github/workflows/conventions.yml` both call this script.
Only the first line of a commit message is checked. The body stays a written
convention; see `docs/CONTRIBUTING.md`.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

TYPES = ("feat", "fix", "docs", "exp", "refactor", "test", "chore", "ci")
MAX_HEADER_LENGTH = 72

_TYPE = "|".join(TYPES)
_KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
BRANCH_PATTERN = rf"^(?:{_TYPE})/{_KEBAB}$"
HEADER_PATTERN = rf"^(?:{_TYPE})(?:\({_KEBAB}\))?: \S(?:.*\S)?$"

BRANCH_EXAMPLE = "feat/add-tokenizer"
HEADER_EXAMPLE = "feat: add a tokenizer"


def branch_errors(name: str) -> list[str]:
    """Return why `name` is not a valid branch, or an empty list."""
    if name == "main":
        return [
            "Refusing to commit on main. "
            f"Create a branch such as {BRANCH_EXAMPLE} and commit there."
        ]
    if not _fullmatch(BRANCH_PATTERN, name):
        allowed = ", ".join(TYPES)
        return [
            f"Branch {name!r} does not match type/short-kebab-case. "
            f"Allowed types: {allowed}. Example: {BRANCH_EXAMPLE}."
        ]
    return []


def header_errors(line: str) -> list[str]:
    """Return why a commit subject line is invalid, or an empty list."""
    errors: list[str] = []
    if line == "":
        errors.append(f"Commit subject is empty. Example: {HEADER_EXAMPLE}.")
        return errors
    if not line.isascii():
        errors.append(f"Commit subject must be ASCII English. Example: {HEADER_EXAMPLE}.")
    if len(line) > MAX_HEADER_LENGTH:
        errors.append(
            f"Commit subject is {len(line)} characters; the maximum is {MAX_HEADER_LENGTH}."
        )
    if not _fullmatch(HEADER_PATTERN, line):
        allowed = ", ".join(TYPES)
        errors.append(
            "Commit subject must look like 'type: subject' or 'type(scope): subject'. "
            f"Allowed types: {allowed}. Scope is lowercase kebab-case. "
            f"Example: {HEADER_EXAMPLE}."
        )
    return errors


def subject_line(message: str) -> str:
    """First line of a commit message, ignoring git's `#` comment lines."""
    for line in message.splitlines():
        if line.startswith("#"):
            continue
        return line
    return ""


def _fullmatch(pattern: str, text: str) -> bool:
    return re.fullmatch(pattern, text) is not None


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


def resolve_base() -> str:
    """Commit-ish that begins the range of commits to check (`base..HEAD`)."""
    base_sha = os.environ.get("BASE_SHA", "").strip()
    if base_sha:
        return base_sha

    base_ref = (
        os.environ.get("BASE_REF", "").strip()
        or os.environ.get("GITHUB_BASE_REF", "").strip()
        or "main"
    )
    for candidate in (f"origin/{base_ref}", base_ref):
        result = _git("rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}")
        if result.returncode == 0:
            return candidate
    raise SystemExit(
        f"Cannot resolve base ref {base_ref!r}. Fetch it, or set BASE_SHA to the base commit."
    )


def commits_since(base: str) -> list[tuple[str, str]]:
    """`(sha, subject)` for each commit reachable from HEAD and not from `base`."""
    result = _git("log", "--format=%H%x1f%s", f"{base}..HEAD")
    if result.returncode != 0:
        detail = result.stderr.strip() or f"git log {base}..HEAD failed"
        raise SystemExit(detail)
    commits: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        sha, subject = line.split("\x1f", 1)
        commits.append((sha, subject))
    return commits


def check_branch() -> int:
    errors = branch_errors(current_branch_name())
    return _report(errors)


def check_message(path: str) -> int:
    with open(path, encoding="utf-8") as handle:
        message = handle.read()
    return _report(header_errors(subject_line(message)))


def check_commits() -> int:
    base = resolve_base()
    commits = commits_since(base)
    if not commits:
        return _report([f"No commits in range {base}..HEAD."])
    errors: list[str] = []
    for sha, subject in commits:
        for error in header_errors(subject):
            errors.append(f"{sha[:7]} {subject!r}: {error}")
    return _report(errors)


def _report(errors: list[str]) -> int:
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=("branch", "message", "commits"),
        help="branch: current branch; message: a commit-message file; commits: base..HEAD",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="commit message file (message mode; pre-commit appends this)",
    )
    args = parser.parse_args(argv)
    if args.mode == "branch":
        return check_branch()
    if args.mode == "message":
        if not args.path:
            parser.error("message mode requires the commit message file")
        return check_message(args.path)
    return check_commits()


if __name__ == "__main__":
    sys.exit(main())
