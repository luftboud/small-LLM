# models/

`models/*.joblib` is gitignored — model weights don't belong in git. This file explains
where they go instead, and how the code finds them either way.

## Why not just commit the model file?

| Threshold | What happens |
|---|---|
| > 10 MB | Not committed — this template's `.pre-commit-config.yaml` fails the `check-added-large-files` hook at 1000 KB / 10 MB |
| > 100 MB | GitHub rejects the push outright |
| Any size, after the fact | `git rm large_file.joblib` does **not** remove it from git history — the object stays in every clone forever unless someone rewrites history (`git filter-repo`, BFG), which is painful for a whole team to coordinate. Decide *before* the first commit, not after. |

This project's model (`models/model.joblib`, a scikit-learn pipeline) happens to be under a
megabyte, so in this specific case the 10 MB rule wouldn't even bite — but the pattern
below is what to use once a model doesn't fit that comfortably, and it costs nothing to
use it from day one.

## How to publish a model (Hugging Face Hub)

```python
from huggingface_hub import HfApi

HfApi().upload_file(
    path_or_fileobj="models/model.joblib",
    path_in_repo="model.joblib",
    repo_id="<your-username>/wine-origin-classifier",
    repo_type="model",
    token=os.environ["HF_TOKEN"],  # see .env.example
)
```

Then set `huggingface.repo_id` in `config/default.yaml` to `"<your-username>/wine-origin-classifier"`.

## How the code loads it

`wine_origin.models.load_model()` tries the local path first, and only falls back to
the Hub if nothing is there locally:

```python
def load_model(path, hf_repo_id=""):
    if Path(path).exists():
        return joblib.load(path)
    if hf_repo_id:
        from huggingface_hub import hf_hub_download
        return joblib.load(hf_hub_download(repo_id=hf_repo_id, filename="model.joblib"))
    raise FileNotFoundError(...)  # tells the caller to run `python -m wine_origin train`
```

This is what lets `python -m wine_origin predict` and the Streamlit app work on a
clean machine that has never run `python -m wine_origin train`, as long as
`huggingface.repo_id` is configured — no manual download step required.

## Model card checklist (fill in on the Hub, not just here)

When you create the Hub repo, its model card (`README.md` on the Hub) should cover:

- **Task** — e.g. "3-class wine cultivar classification from 13 chemical measurements"
- **Training data** — link back to this repo's `data/README.md`, don't restate the license there, just point to it
- **Metrics** — pull straight from `results/metrics.json`, don't hand-type numbers that can drift out of sync
- **Limitations** — dataset size, any known class imbalance, anything the model hasn't seen
- **License** — usually inherits the more restrictive of your data's license and your code's license
- **How to cite** — point back to this repo's `CITATION.cff`

## Alternatives to Hugging Face Hub

| Option | Good for |
|---|---|
| Hugging Face Hub | Models *and* datasets, free hosting, versioning, the pattern used above |
| GitHub Releases | A one-off artifact up to ~2 GB, no need for model-specific tooling |
| Git LFS | If you want the file to still feel like "part of the repo" via git commands |
| DVC + cloud storage | Multiple large artifacts across a project's lifetime, with pipeline tracking |
| Zenodo | You need a DOI (e.g. citing a specific model version in a paper) |
