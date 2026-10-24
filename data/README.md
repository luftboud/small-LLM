
# data/ — data card

## Name and source

**XL-Sum (Ukrainian subset)** is a multilingual news summarization dataset built from
BBC articles. This project uses the Ukrainian subset to evaluate how well a language
model retains its ability to model Ukrainian text after compression.

- Hugging Face: <https://huggingface.co/datasets/csebuetnlp/xlsum>
- Paper: <https://aclanthology.org/2021.findings-acl.413/>
- Dataset repository: `csebuetnlp/xlsum`
- Configuration: `ukrainian`

## License and terms of use

XL-Sum is distributed under the
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license. It may
be used and adapted for non-commercial purposes with attribution. Adapted material
must be shared under the same license.

**Citation:**

> Hasan, T., Bhattacharjee, A., Islam, M. S., Mubasshir, K., Li, Y.-F., Kang, Y.-B.,
> Rahman, M. S., and Shahriyar, R. (2021). *XL-Sum: Large-Scale Multilingual
> Abstractive Summarization for 44 Languages*. Findings of ACL-IJCNLP 2021.

## Size and format

Only the Ukrainian Parquet export is required:

| Split | Rows | Approximate size |
|---|---:|---:|
| Train | 43,201 | 125 MB |
| Validation | 5,399 | 14 MB |
| Test | 5,399 | 14 MB |

The files are stored under `data/raw/xlsum/ukrainian/`. Raw data is ignored by Git
and must be downloaded locally.

## Schema

| Column | Type | Description |
|---|---|---|
| `id` | string | Unique article identifier |
| `url` | string | Original BBC article URL |
| `title` | string | Article title |
| `summary` | string | Reference summary |
| `text` | string | Full article text |

The pruning experiments use `text` for language-model loss. The `summary` field is
reserved for summarization evaluation such as ROUGE-L.

## `data/raw/` vs. `data/interim/` vs. `data/processed/`

- `data/raw/` contains the downloaded XL-Sum Parquet files.
- `data/interim/` is reserved for cleaned text, for example text with invisible
  direction-control characters removed.
- `data/processed/` is reserved for model-ready subsets or tokenized data.

Do not commit dataset files. Commit only documentation, code, and small metadata
needed to reproduce the download and preprocessing steps.

## How to get it

Install the Hugging Face CLI and Datasets library:

```bash
pip install -U huggingface_hub datasets
```

From the repository root, download only the Ukrainian Parquet export:

```bash
hf download csebuetnlp/xlsum \
  --repo-type dataset \
  --revision refs/convert/parquet \
  --include "ukrainian/**" \
  --local-dir data/raw/xlsum
```

The resulting structure should be:

```text
data/raw/xlsum/ukrainian/
├── train/0000.parquet
├── validation/0000.parquet
└── test/0000.parquet
```

Load a local split with Hugging Face Datasets:

```python
from datasets import load_dataset

validation_dataset = load_dataset(
    "parquet",
    data_files={
        "validation": "data/raw/xlsum/ukrainian/validation/0000.parquet",
    },
    split="validation",
)
```

The direct Parquet download is intentional. Recent `datasets` versions no longer run
the legacy `xlsum.py` dataset script from the main repository revision.

## Splits

Use the original XL-Sum splits:

- `train` for optional calibration data;
- `validation` for selecting pruning or compression settings;
- `test` only for final evaluation.

Use a fixed seed when sampling a smaller subset, and evaluate every model on exactly
the same examples.

## Personal data

The dataset consists of public news articles and may mention real people,
organizations, locations, and events. It does not intentionally provide private user
records, but generated examples should still be reviewed before publication.

## Scraping

This project does not scrape BBC pages directly. It uses the dataset published by the
XL-Sum authors through Hugging Face. The `url` field is retained for provenance.

## Known limitations and biases

- The Ukrainian subset comes from one news source, so its style and topic distribution
  are not representative of all Ukrainian text.
- News data can contain social, political, geographic, and editorial biases.
- Articles may include invisible Unicode direction-control characters such as
  `\u200e`; remove them consistently before evaluation if needed.
- Language-model loss on `text` measures next-token prediction, not factual accuracy,
  instruction following, or summarization quality.
- ROUGE-L measures overlap with one reference summary and does not fully capture
  factual correctness or summary quality.

## Ethical risks

Models may reproduce bias, sensitive claims, names, or outdated information found in
the source articles. Dataset examples and generated outputs should not be treated as
verified facts without checking the original source.

## Version and reproducibility

The download command pins the Hugging Face Parquet export revision
`refs/convert/parquet`. Keep the sampling seed, split name, number of examples, and
tokenization length in experiment logs. The raw files remain outside Git.
