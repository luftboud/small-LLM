# Using this repo as a template

Keep this layout. Replace the wine-classifier example with your project. Paths, seeds, and hyperparameters live in `config/` — not hardcoded in `src/`.

**First clone**

```bash
make setup                          # .venv + deps + editable install + pre-commit
source .venv/bin/activate
make reproduce                      # data → train → evaluate (optional smoke test)
```

Rename the package (`src/wine_origin` → `src/<your_package>`), update `pyproject.toml` `[project].name`, and search-replace `wine_origin` / `wine-origin`. Then rewrite `README.md`, `CITATION.cff`, and the per-folder READMEs.

---

## Directories

### `src/<package>/`

Importable library and the CLI (`python -m wine_origin train|evaluate|predict`).

- Put reusable logic here, not in notebooks or Streamlit.
- After rename: `pip install -e .` again so the new package name imports.

### `scripts/`

One-off jobs: download data, run the full experiment table.

```bash
python scripts/download_data.py
python scripts/run_experiment.py
```

Do not put library code here — import from `src/`.

### `app/`

Streamlit demo.

```bash
python -m model_origin train          # once, if models/ is empty
streamlit run app/streamlit_app.py   # http://localhost:8501
```

Replace widgets and prediction UI; keep loading the model via the package.

### `notebooks/`

EDA and narrative (`01-…`, `02-…`). Drafts only — production code goes in `src/`.

- One notebook, one author at a time (JSON merges badly).
- `Restart & Run All` before commit. See `notebooks/README.md`.

### `tests/`

Pytest. Mirror `src/` as you add modules.

```bash
pytest
```

### `config/`

`default.yaml`: seed, paths, split, model choice, Hugging Face repo id.

```bash
python -m model_origin train --override model.active=random_forest
```

### `data/`

Raw / interim / processed files are **gitignored**. Commit only `README.md` (data card: source, license, schema) and `data/raw/CHECKSUMS.txt`.

```bash
python scripts/download_data.py      # regenerates files locally; checksums must match
```

Never commit datasets.

### `models/`

Trained weights are **gitignored**. Publish large files to Hugging Face (see `models/README.md`). Local `models/model.joblib` is used first if present.

### `results/`

Committed metrics, experiment notes, and small figures. After a real run, update `metrics.json` / `experiments.md` so the root README stays honest.

### `docs/`

Proposal, poster, slides, contributing. Replace placeholders; keep course artifacts here, not in `src/`.

### `examples/`

Tiny sample inputs for `predict` (e.g. `examples/sample.json`). Swap for your schema.

### `.github/workflows/`

CI example: lint. Add a `test.yml` that runs `pytest` if you want that on every push.

---

## Important files (root)

| File | What to do |
|---|---|
| `Makefile` | `setup` and `reproduce` only. Add targets only if the team will actually use them. Override Python: `make setup PYTHON=python3.11`. |
| `requirements.txt` | Runtime pins. `requirements-dev.txt` = lint/test/pre-commit. |
| `pyproject.toml` | Package name, Python version, black/isort/pytest. |
| `setup.cfg` | flake8. |
| `.pre-commit-config.yaml` | Installed by `make setup`. Blocks large files (~10 MB). |
| `.env.example` | Copy to `.env` (gitignored) for tokens (`HF_TOKEN`, etc.). |
| `LICENSE` / `CITATION.cff` | Code license ≠ data license. Update citation for your project. |
| `README.md` | Project story, results table, team. This file is the **template map**. |

---

## Daily loop

```bash
source .venv/bin/activate
# edit src/, config/, tests/
pytest
flake8 src/ scripts/ tests/ app/ && black src/ scripts/ tests/ app/ && isort src/ scripts/ tests/ app/
python -m model_origin train && python -m model_origin evaluate
```

Do not commit `.venv`, `.env`, `data/raw/*.csv`, or `models/*.joblib`.
