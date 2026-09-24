
# data/ — Ukrainian language datasets

## Datasets and sources

| Dataset | Purpose | Source |
|---|---|---|
| mmlu_ukr | Multiple-choice questions across academic subjects | [INSAIT-Institute/mmlu_ukr](https://huggingface.co/datasets/INSAIT-Institute/mmlu_ukr) |
| ifeval_ukr | Instruction following with explicit constraints | [INSAIT-Institute/ifeval_ukr](https://huggingface.co/datasets/INSAIT-Institute/ifeval_ukr) |
| XL-Sum, Ukrainian v2.0 | News article summarization | [Official XL-Sum repository](https://github.com/csebuetnlp/xl-sum) |
| wiki-instruction-dialogs | Wikipedia-based text transformation and extraction tasks | [lapa-llm/wiki-instruction-dialogs](https://huggingface.co/datasets/lapa-llm/wiki-instruction-dialogs) |

## Size and splits

| Dataset | Loaded splits | Size documented in the notebook                                                                     |
|---|---|-----------------------------------------------------------------------------------------------------|
| mmlu_ukr | `dev`, `validation`, `test` | `dev`: 285 examples across 57 subjects, 5 per subject; validation/test counts require a clean rerun |
| ifeval_ukr | `train` | 541 unique prompts                                                                                  |
| XL-Sum Ukrainian | `train`, `validation`, `test` | 43,201 / 5,399 / 5,399 examples                                                                     |
| wiki-instruction-dialogs | `train` | 30,684 examples                                                                                     |

The saved MMLU shape output reports five columns and 5,399 rows for both test
and validation, matching the XL-Sum shapes later in the notebook. These outputs
appear stale; rerun the MMLU loading and shape cells together before reporting
those split sizes.


The notebook preserves the source splits and creates no additional train/test
partition. A split named `train` describes the upstream dataset; loading it here
does not mean that it is used to train a model.

## Schema and prompt preparation

### mmlu_ukr

- `question`: question text.
- `subject`: academic subject.
- `choices`: sequence of answer options.
- `answer`: zero-based index of the correct option; cast to `uint8` in the development dataframe.

`mmlu_prompt_formation(record)` includes the subject, question, and numbered
options, then requests only the correct option number. It returns the prompt
and an integer answer index. Options use `0`, `1`, `2`, and `3`.
Repeated spaces in the question are collapsed.

### ifeval_ukr

- `key`: record identifier.
- `prompt`: instruction-following prompt.
- `instruction_id_list`: identifiers of the constraints to verify.
- `kwargs`: parameter dictionaries corresponding to those constraints.

`ifeval_prompt_formation(record)` returns the prompt and a list of instruction
IDs paired with their non-null parameters. It collapses repeated spaces in the
prompt. The returned metadata supports later verification; the notebook does
not implement the instruction checkers or provide a reference answer.


### XL-Sum Ukrainian

- `id`: article identifier.
- `url`: source article URL.
- `title`: article title.
- `summary`: reference summary.
- `text`: article body.

`xlsum_prompt_formation(record)` asks for a summary and includes the title,
URL, and article text. It returns the prompt and the original reference summary.
Repeated spaces in the title and article text are collapsed.

### wiki-instruction-dialogs

- `task`: task category.
- `instruction`: requested operation.
- `input`: source text.
- `output`: reference response.
- `conversations`: conversation representation of the example.

`wiki_prompt_formation(record)` combines the task, input, and instruction and
returns the prompt with the reference output. It collapses repeated spaces in
the input and instruction. The `conversations` field is inspected but is not
used by this prompt function.

## How to load the data

Run the notebook with `notebooks/` as the working directory. Its imports use
`pandas`, `numpy`, and Hugging Face `datasets`; remote Parquet loading also needs
a Parquet engine and Hugging Face filesystem support.

MMLU and IFEval are read directly from Hugging Face Parquet files:

```python
import pandas as pd

mmlu_dev = pd.read_parquet(
    "hf://datasets/INSAIT-Institute/mmlu_ukr/data/dev-00000-of-00001.parquet"
)
ifeval = pd.read_parquet(
    "hf://datasets/INSAIT-Institute/ifeval_ukr/data/train-00000-of-00001.parquet"
)
```

The MMLU validation and test files follow the same naming pattern with
`validation` and `test` in place of `dev`.

For XL-Sum, download the Ukrainian Parquet files from Hugging Face by running this command from the project root:


```bash
hf download csebuetnlp/xlsum \
  --repo-type dataset \
  --revision refs/convert/parquet \
  --include "ukrainian/**" \
  --local-dir data/raw/xlsum
```

The notebook loads the local training, validation, and test splits as follows:

```python
from pathlib import Path
from datasets import load_dataset

cwd = Path.cwd()
PROJECT_ROOT = cwd.parent if cwd.name == "notebooks" else cwd
data_dir = PROJECT_ROOT / "data" / "raw" / "xlsum" / "ukrainian"

xlsum = load_dataset("parquet", data_files={
    "train": str(data_dir / "train" / "0000.parquet"),
    "validation": str(data_dir / "validation" / "0000.parquet"),
    "test": str(data_dir / "test" / "0000.parquet"),
})
train_df = xlsum["train"].to_pandas()
val_df = xlsum["validation"].to_pandas()
test_df = xlsum["test"].to_pandas()
```

The Wikipedia dataset is loaded directly from Hugging Face:

```python
wiki = load_dataset("lapa-llm/wiki-instruction-dialogs")
```

## Licenses and attribution

The source pages list the following licenses:

| Dataset | Published license |
|---|---|
| [mmlu_ukr](https://huggingface.co/datasets/INSAIT-Institute/mmlu_ukr) | Apache-2.0 |
| [ifeval_ukr](https://huggingface.co/datasets/INSAIT-Institute/ifeval_ukr) | Apache-2.0 |
| [XL-Sum](https://github.com/csebuetnlp/xl-sum#license) | CC BY-NC-SA 4.0; the repository restricts use to non-commercial research |
| [wiki-instruction-dialogs](https://huggingface.co/datasets/lapa-llm/wiki-instruction-dialogs) | CC BY 4.0 |

Retain source attribution and consult the linked dataset cards for the applicable
terms and citations. XL-Sum states that the original copyright holders retain
copyright in its contents. Its requested citation is Hasan et al. (2021),
[XL-Sum: Large-Scale Multilingual Abstractive Summarization for 44 Languages](https://aclanthology.org/2021.findings-acl.413/).

## Limitations and ethical considerations

These datasets cover academic questions, constrained instructions, news, and
encyclopedic text. They provide a limited view of Ukrainian language performance;
results may depend on task distribution, translation quality, and prompt format.
Wikipedia task counts are imbalanced, particularly for `masked_sentence`.

News and Wikipedia passages can mention real people and sensitive events. The
notebook performs no personal-data filtering, factual verification, or bias audit.
It loads existing datasets and performs no new web scraping. Public benchmark
content may also overlap with model pretraining data; 
