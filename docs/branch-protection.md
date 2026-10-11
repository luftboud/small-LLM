# Branch protection on `main`

`main` is protected by a GitHub repository ruleset, not only by agreement.
The ruleset payload and the repository merge settings live in
[`.github/rulesets/main.json`](../.github/rulesets/main.json). Applying that
file requires admin on the repository. A fork or a repository created from a
template does not inherit it; reapply the file there.

## What is enforced

- Commits land on `main` only through a pull request. This includes admins:
  the ruleset has no bypass actors.
- At least one approving review. A push after that review dismisses it.
- The pull request branch is up to date with `main`.
- Required checks: `lint` and `conventions`.
- `main` cannot be deleted and cannot be force-pushed.
- History on `main` is linear.
- The repository accepts rebase merges only. Squash and merge commits are off,
  both in the repository settings and in the ruleset's `allowed_merge_methods`.
  The repository settings are in the same JSON file, beside the ruleset.

## Reapply

From a checkout of this repository, with `gh` logged in as an admin:

```bash
# Create the ruleset. If "Protect main" already exists, use the PUT below
# with its id instead of POST.
jq '.ruleset' .github/rulesets/main.json \
  | gh api --method POST repos/luftboud/small-LLM/rulesets --input -

# Rebase merges only.
jq '.repo_settings' .github/rulesets/main.json \
  | gh api --method PATCH repos/luftboud/small-LLM --input -
```

To update an existing ruleset, replace `RULESET_ID`:

```bash
gh api repos/luftboud/small-LLM/rulesets --jq '.[] | {id, name}'

jq '.ruleset' .github/rulesets/main.json \
  | gh api --method PUT repos/luftboud/small-LLM/rulesets/RULESET_ID --input -
```

The `context` values under `required_status_checks` must match the check names
GitHub reports (`gh pr checks`). `integration_id` 15368 is GitHub Actions.
