# Setting up branch protection on `main`

Template repos don't carry branch-protection settings over to repos created from them
via "Use this template" — this is a one-time setup step each team does for their own
repository, early (ideally in your first week, not after someone accidentally pushes
straight to `main`).

## Steps

1. On GitHub, go to your repo → **Settings → Branches**.
2. Under **Branch protection rules**, click **Add rule** (or **Add branch ruleset**,
   depending on which GitHub is currently showing you).
3. Branch name pattern: `main`.
4. Enable:
   - **Require a pull request before merging**
   - **Require approvals** — set to `1` (see `docs/CONTRIBUTING.md` for why review
     matters beyond just gatekeeping: it's the main way teammates learn what the rest
     of the team is doing)
   - **Require status checks to pass before merging** — select the `lint` job from
     `.github/workflows/lint.yml` (and any other workflow jobs you've since added)
     once it's run at least once (GitHub only lists checks that have executed on this
     repo before)
5. Save.

## Why bother for a 2-person team

It's tempting to skip this when the team is small and everyone trusts each other. The
value isn't distrust — it's that review is where you find out what your teammate
actually built, before it's merged and you're both depending on it. A rule that's
"recommended, but easy to skip under deadline pressure" tends to get skipped exactly
when it would have caught something. Turning it on costs five minutes once.
