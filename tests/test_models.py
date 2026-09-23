"""Smoke tests for the model pipeline. These are deliberately shallow — they exist to
catch "the pipeline doesn't even run" (a broken import, a shape mismatch, a typo in a
param name), which is responsible for most broken ML code in practice. Deeper
correctness (does the model actually generalize well) is what results/experiments.md
and the notebooks are for.
"""
