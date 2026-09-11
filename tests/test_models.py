"""Smoke tests for the model pipeline. These are deliberately shallow — they exist to
catch "the pipeline doesn't even run" (a broken import, a shape mismatch, a typo in a
param name), which is responsible for most broken ML code in practice. Deeper
correctness (does the model actually generalize well) is what results/experiments.md
and the notebooks are for.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from wine_origin.config import load_config
from wine_origin.data import (
    materialize_raw_csv,
    split_features_target,
    train_test_split_stratified,
)
from wine_origin.models import build_active_model, build_baseline


def test_pipeline_trains_on_small_sample_and_predicts_right_shape(tmp_path):
    config = load_config("config/default.yaml")
    df = materialize_raw_csv(tmp_path / "wine.csv")
    # ~20 samples, all 3 classes represented
    small_df = pd.concat([group.sample(n=7, random_state=0) for _, group in df.groupby("target")])
    X, y = split_features_target(small_df)

    model = build_active_model(config)
    model.fit(X, y)
    predictions = model.predict(X)

    assert predictions.shape == (len(X),)
    assert set(predictions).issubset({0, 1, 2})


def test_active_model_beats_baseline_on_held_out_data(tmp_path):
    config = load_config("config/default.yaml")
    df = materialize_raw_csv(tmp_path / "wine.csv")
    train_df, test_df = train_test_split_stratified(
        df, test_size=config["split"]["test_size"], seed=config["seed"]
    )
    X_train, y_train = split_features_target(train_df)
    X_test, y_test = split_features_target(test_df)

    baseline = build_baseline()
    baseline.fit(X_train, y_train)
    baseline_accuracy = np.mean(baseline.predict(X_test) == y_test)

    model = build_active_model(config)
    model.fit(X_train, y_train)
    model_accuracy = np.mean(model.predict(X_test) == y_test)

    assert model_accuracy > baseline_accuracy
