# Notebook conventions

Naming: `NN-kebab-case-name.ipynb`, numbered in the order you'd actually read them (`NN` is two digits: `01`, `02`, ...).

1. **A notebook is a draft and a narrative, not the source of truth.** Working code that's used more than once belongs in `src/wine_origin/`, and the notebook imports it — the rule of thumb is: if a function is needed twice, it belongs in `src/`, not copy-pasted between notebooks.
2. **Every notebook opens with a markdown cell**: Goal, Input, Conclusion. The Conclusion is written **after** the analysis, once you know what the results actually say — not drafted in advance and left unchanged.
3. **`Restart & Run All` before committing.** A notebook that doesn't run cleanly top to bottom doesn't get committed — a notebook full of out-of-order cell numbers is a common source of "works on my machine, mysteriously not on yours."
4. **Outputs are committed.** This course's convention is to keep cell outputs in the `.ipynb` file (not strip them), so plots and tables are visible directly on GitHub without anyone having to re-run the notebook first. The tradeoff is merge conflicts (see rule 5) and file size — keep figures reasonably sized, don't `df.head(10000)` into a cell.
   - `.pre-commit-config.yaml` ships an `nbstripout` hook that would strip outputs on commit — it's **disabled by default** to match this convention. If your team decides the conflict pain outweighs the benefit, there are instructions in that file for turning it on.
5. **Notebooks and git merges don't mix well.** The underlying JSON makes conflicts nearly unreadable, and git can't meaningfully merge two people's changes to the same notebook. Practical rule: one notebook, one author, at a time. If two people need to work on the same analysis, split it into two notebooks or hand it off explicitly rather than editing in parallel.
6. **Colab compatibility.** Each notebook carries an "Open in Colab" badge and a guarded first code cell (`if "google.colab" in sys.modules: ...`) that clones the repo and installs dependencies — safe to leave in when running locally, since the block is a no-op outside Colab.

The four notebooks in this folder (`01-data-exploration`, `02-baseline-model`, `03-model-comparison`, `04-error-analysis`) are fully executed, in that order, and are meant to be read as the actual analysis behind `results/experiments.md` — not sample content to delete.
