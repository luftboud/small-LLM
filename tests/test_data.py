"""Catches the most common silent mistakes in an ML data pipeline: wrong shape,
missing values that sneak through, and train/test contamination.
"""

from __future__ import annotations

from wine_origin.data import (
    TARGET_COLUMN,
    materialize_raw_csv,
    split_features_target,
    train_test_split_stratified,
)


def test_materialized_csv_has_expected_shape(tmp_path):
    df = materialize_raw_csv(tmp_path / "wine.csv")
    assert df.shape == (178, 14)  # 13 features + target
    assert TARGET_COLUMN in df.columns
    assert set(df[TARGET_COLUMN].unique()) == {0, 1, 2}


def test_no_missing_values(tmp_path):
    df = materialize_raw_csv(tmp_path / "wine.csv")
    assert df.isna().sum().sum() == 0


def test_split_is_stratified(tmp_path):
    df = materialize_raw_csv(tmp_path / "wine.csv")
    train_df, test_df = train_test_split_stratified(df, test_size=0.2, seed=42)

    train_proportions = train_df[TARGET_COLUMN].value_counts(normalize=True).sort_index()
    test_proportions = test_df[TARGET_COLUMN].value_counts(normalize=True).sort_index()

    # Stratified splitting should keep class proportions close between train and test,
    # not just "some of each class made it in".
    assert (train_proportions - test_proportions).abs().max() < 0.05


def test_no_overlap_between_train_and_test(tmp_path):
    df = materialize_raw_csv(tmp_path / "wine.csv")
    train_df, test_df = train_test_split_stratified(df, test_size=0.2, seed=42)

    train_rows = {tuple(row) for row in train_df.itertuples(index=False)}
    test_rows = {tuple(row) for row in test_df.itertuples(index=False)}
    assert train_rows.isdisjoint(test_rows)

    assert len(train_df) + len(test_df) == len(df)


def test_split_features_target_shapes(tmp_path):
    df = materialize_raw_csv(tmp_path / "wine.csv")
    X, y = split_features_target(df)
    assert X.shape == (178, 13)
    assert y.shape == (178,)
    assert TARGET_COLUMN not in X.columns
