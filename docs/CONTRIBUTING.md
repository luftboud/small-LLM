# Contributing

`main` stays releasable. Changes reach it through a branch and a rebase pull request.
GitHub shows this file when a pull request is opened.

## Branches

Name every branch `type/short-kebab-case`.

Allowed types: `feature`, `fix`, `docs`, `exp`, `refactor`, `test`, `chore`, `ci`.

```
feature/add-tokenizer
fix/empty-test-split
exp/int4-quantization
ci/contribution-checks
```

The segment after `/` is lowercase words and digits joined by single hyphens.
`main` is the protected branch. A local hook rejects commits made while it is
checked out, and GitHub rejects a direct push, including from admins.
Force-pushes and deleting `main` are rejected too.

## Pull requests

Every change is a pull request into `main`.

- At least one teammate approves before merge. A new commit dismisses that approval.
- The branch is up to date with `main` before merge.
- Merge method is rebase, so `main` stays a straight line of the branch's commits.
- Two checks must pass: `lint` (flake8, black, isort) and `conventions`
  (this file's branch and commit rules).

The author of a pull request cannot approve it. Ask another collaborator.

## Commits

The first line is a [Conventional Commit](https://www.conventionalcommits.org/):

```
type: subject
type(scope): subject
```

Types match the branch types above, except a `feature/…` branch uses the commit
type `feat`. `scope` is optional and uses the same
lowercase kebab-case as a branch name. The whole first line is ASCII and at most
72 characters. Write the subject in English.

The checker enforces that first line only. Use the body for the reasoning the
diff cannot show: why this approach, what was ruled out, what tradeoff was made.
Leave a blank line between the subject and the body.

For `exp:` commits, put the result in the body so the git log stays a short
experiment record:

```
exp: try int4 quantization on the student model

macro-F1 0.81 -> 0.78 at about 4x smaller weights. Notes: results/experiments.md
```

### Before / after

| Before | After |
|---|---|
| `update` | `fix: handle an empty test split when a class has under 5 samples` |
| `fix bug` | `fix: stratify the split so a rare class is not dropped` |
| `asdf` | `chore: remove an unused import in evaluate.py` |
| `final version FINAL` | `docs: fill the results table from the latest run` |
| `changes` | `refactor: move plotting out of cli.py into evaluate.py` |

## Authorship

- **Pair programming / shared work.** Credit the other person with a trailer at
  the bottom of the message. GitHub records both people as authors:

  ```
  Co-authored-by: Name <email@example.com>
  ```

- **AI-assisted commits.** A human makes the commit under their own name and can
  explain every line. If a tool produced a substantial part of the change, add
  `Assisted-by: <tool>`. Do not list the tool as `Co-authored-by:`; that trailer
  is for an accountable collaborator. The person who ran the tool and reviewed
  the output is the author.

## Local hooks

The same rules run before a commit, once the hooks are installed:

```bash
pip install pre-commit
pre-commit install
```

`pre-commit install` reads `default_install_hook_types` in
`.pre-commit-config.yaml` and installs both the `pre-commit` and `commit-msg`
hooks. Run it again if the hooks were installed before the commit-message hook
existed. `--no-verify` skips the local hooks; the `conventions` check on the
pull request still applies.

Enforcement on GitHub is described in [`docs/branch-protection.md`](branch-protection.md).
