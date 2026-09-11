# data/ — data card

> **Why this matters:** deciding a dataset's license and provenance *before* you start
> building is a lot cheaper than discovering after your final report is written that
> you're not actually allowed to redistribute it, or that you can't say where it came
> from. Fill this file in as one of the first things you do, not the last.

## Name and source

**UCI Wine Recognition Data**, accessed via `sklearn.datasets.load_wine`. Originally
donated to the UCI Machine Learning Repository in 1991 by Forina, M. et al.,
Institute of Pharmaceutical and Food Analysis and Technologies (Genoa, Italy). Results
of a chemical analysis of wines grown in the same region of Italy, from three
different cultivars.

- UCI page: <https://archive.ics.uci.edu/dataset/109/wine>
- Bundled directly in scikit-learn — no external download needed, see "How to get it" below.

## License and terms of use

No explicit license file accompanies the original 1991 UCI submission (it predates
standard dataset-licensing practice). scikit-learn redistributes it as one of its
built-in "toy datasets" for examples and teaching. Treat it as free to use for
research and educational purposes; if you use it in a report or publication, cite
the original source (see below) rather than just "scikit-learn". There are no known
commercial-use restrictions, but because there's no formal license grant, avoid
presenting it as your own collected data in anything beyond a course project context.

**Citation**, if you need one:

> Forina, M. et al. (1991). *PARVUS — An Extendible Package for Data Exploration,
> Classification and Correlation*. Institute of Pharmaceutical and Food Analysis and
> Technologies, Via Brigata Salerno, 16147 Genoa, Italy.

## Size and format

- 178 samples, 13 numeric features, 3 classes (cultivars)
- One CSV file, `data/raw/wine.csv`, ~11 KB
- No train/test files on disk — the split is generated at runtime from a fixed seed (see "Splits" below), so there's only ever one raw file to keep in sync

## Schema

| Column | Type | Description | Units |
|---|---|---|---|
| `alcohol` | float | Alcohol content | % vol |
| `malic_acid` | float | Malic acid | g/L |
| `ash` | float | Ash | g/L |
| `alcalinity_of_ash` | float | Alkalinity of ash | — |
| `magnesium` | float | Magnesium | mg/L |
| `total_phenols` | float | Total phenols | — |
| `flavanoids` | float | Flavanoids | — |
| `nonflavanoid_phenols` | float | Non-flavanoid phenols | — |
| `proanthocyanins` | float | Proanthocyanins | g/L |
| `color_intensity` | float | Color intensity | — |
| `hue` | float | Hue | — |
| `od280/od315_of_diluted_wines` | float | OD280/OD315 of diluted wines (protein content proxy) | — |
| `proline` | float | Proline | mg/L |
| `target` | int | Cultivar: `0`, `1`, or `2` | — |

## `data/raw/` vs. `data/interim/` vs. `data/processed/`

This project's pipeline is simple enough to go straight from `data/raw/wine.csv` to
features in memory (see `src/wine_origin/features.py`) — so `data/interim/` and
`data/processed/` are currently empty (just a `.gitkeep` each, so the folders exist
after a fresh clone). If your project adds a real multi-step pipeline — e.g.
cleaning/joining raw sources into an intermediate form, then engineering features from
that — `data/interim/` is where the intermediate, not-yet-final form goes, and
`data/processed/` is where the model-ready output goes. Same rule as `data/raw/`:
never commit the files themselves, only document what's in them here.

## How to get it

```bash
python scripts/download_data.py
```

This materializes `sklearn`'s built-in dataset to
`data/raw/wine.csv` and writes its sha256 to `data/raw/CHECKSUMS.txt`. It's idempotent
— if the checksum already matches, it does nothing on a re-run.

## Splits

Stratified 80/20 train/test split, `random_state=42` (see `config/default.yaml`'s
`seed` and `split` keys), computed at runtime in `wine_origin.data.train_test_split_stratified`
— not stored as separate files, so there's exactly one raw file to keep an eye on. No
overlap between train and test is verified by `tests/test_data.py`.

## Personal data

None. This is chemical measurement data with no connection to individuals.

## Scraping

Not applicable — this dataset was not scraped; it comes from a 1991 laboratory
chemical analysis, redistributed via scikit-learn.

## Known limitations and biases

- Small (178 samples) — expect wide confidence intervals on any metric, and treat
  single-run numbers with caution (see the "why one seed isn't enough" note in the
  root README).
- Mild class imbalance: 59 / 71 / 48 samples across the three cultivars.
- All samples are from one region of Italy — a model trained on this data has not
  seen wines from other regions, and nothing in the data or the model should be
  assumed to generalize beyond similar cultivars.

## Ethical risks

Low: this is chemical composition data with no personal, demographic, or otherwise
sensitive information. The main risk is over-generalizing a model trained on 178
samples from one region as if it said something universal about wine chemistry.

## Version and checksum

`data/raw/CHECKSUMS.txt` (committed to git, unlike the data itself) records the
sha256 of the exact file this project was built and tested against. Regenerate and
compare with `python scripts/download_data.py`.

---

## If your project's data is too large or private for this pattern

The pattern above — a small dataset, materialized on demand, checksum committed
instead of the data — doesn't fit every project. If yours doesn't:

- **Large but shareable**: Git LFS, DVC + cloud storage (S3/GCS/etc.), or Hugging Face
  Datasets are all reasonable; pick based on whether your team already uses one of them.
- **Already hosted elsewhere**: if the data already lives on Kaggle, just document the
  dataset URL and the `kaggle datasets download <owner>/<dataset>` command (via the
  `kaggle` CLI) instead of re-hosting it yourself.
- **You need a DOI** (e.g. citing a specific dataset version in a paper or proposal):
  Zenodo — same idea as the models/README.md Hugging Face pattern, but for data.
- **Private (can't be public at all)**: keep it out of git entirely, document exactly
  how to request access in this file, and note that CI/graders will need a documented
  path to get it too.

> [!warning]
> `git rm big_or_private_file.csv` does **not** remove it from git history — the file
> is still sitting in every commit before that removal, downloadable by anyone with
> repo access. If a data file with real access restrictions is ever committed by
> mistake, don't just delete it in a new commit: treat it like a leaked secret (see the
> root README's note on that) and either rewrite history properly (`git filter-repo`)
> before anyone else pulls, or accept it needs to be revoked/rotated at the source.
> Deciding your storage approach *before* the first commit is much cheaper than fixing
> this after the fact.
