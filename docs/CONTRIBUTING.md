# Contributing

This document is what makes the methodology's "your work should be visible in your
commit history" requirement concrete, instead of something you find out you violated
after the fact.

## Branches

- `main` is always in a working state — anyone should be able to clone it and run
  `make reproduce` successfully at any point in time.
- All work happens on a branch: `feat/<short-name>` for new functionality,
  `fix/<short-name>` for bug fixes, `exp/<short-name>` for experiments that might not
  pan out. No direct pushes to `main` (see `docs/branch-protection.md` to enforce this
  on GitHub, not just by agreement).

## Pull requests

Every change to `main` goes through a PR, and every PR gets at least one review from a
teammate before merging. This isn't bureaucracy for its own sake: review is the main
way the rest of the team finds out what you actually built, in enough detail to
maintain it later — a standup update ("I finished the eval script") doesn't give
anyone else the ability to debug that script next week; reading the diff does.

## Commits — Conventional Commits

Prefixes: `feat:`, `fix:`, `docs:`, `exp:`, `refactor:`, `test:`, `chore:`.

**The commit body explains *why*, not *what*** — the diff already shows what changed;
the body is where you write down the reasoning that isn't visible from the code
itself (why this approach, what you ruled out, what tradeoff you made).

For `exp:` commits specifically, put the result in the body — that's what turns the
git log into a second, lightweight experiment record alongside `results/experiments.md`:

```
exp: try RandomForest with 200 trees

macro-F1 0.94 -> 0.96, CV std 0.02. Details: results/experiments.md
```

### Before / after

| Before | After |
|---|---|
| `update` | `fix: handle empty test split when a class has <5 samples` |
| `fix bug` | `fix: stratify train/test split so rare classes aren't dropped entirely` |
| `asdf` | `chore: remove unused import in evaluate.py` |
| `final version FINAL` | `docs: fill in results table with run_experiment.py output` |
| `changes` | `refactor: move confusion-matrix plotting out of cli.py into evaluate.py` |

## Authorship

- **Pair programming / shared work**: credit both people with a `Co-authored-by:`
  trailer at the bottom of the commit message (GitHub adds both as authors on the
  commit):

  ```
  Co-authored-by: Name <email@example.com>
  ```
- **AI-assisted commits**: the commit is made by a **human**, under their own name,
  and that person should be able to explain every line in it — "the AI wrote it" is
  not an explanation a reviewer will accept. If AI tooling produced a substantial part
  of a change, add an `Assisted-by: <tool>` trailer to say so. Don't add the AI tool as
  a `Co-authored-by:` — that implies an accountable collaborator, which a tool isn't;
  the human who ran it and reviewed the output is the author.
- **Even contribution is a pattern across the whole semester, not a last-week fix.**
  Rewriting history to look evenly distributed right before submission is visible
  (timestamps, force-push history if the remote allows it) and defeats the actual
  point, which is that everyone was meaningfully involved throughout.

## Rhythm

- Commit at least once a week, per person. A single commit the night before a defense
  is a flagged pattern in the methodology, not just a stylistic preference — it reads
  as work that wasn't actually spread across the semester.
- Use GitHub Issues + a Project board to plan work, with milestones matching the
  course's dates (proposal, camera-ready, midterm, poster, final defense). For
  experiment issues specifically, structure them as hypothesis → setup → result →
  conclusion — the same shape as an `exp:` commit body above.

## Access

Add your instructor(s) and mentor as repo collaborators early (see the root README's
setup checklist) — reviews and issue assignments don't work for people who aren't
collaborators on the repo yet.
