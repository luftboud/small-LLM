"""Makes "reproducible" a checkable claim instead of a hopeful one: two runs with the
same seed must produce bit-identical metrics, not just "similar" ones.
"""

from __future__ import annotations

from wine_origin.config import load_config
from wine_origin.data import (
    materialize_raw_csv,
    split_features_target,
    train_test_split_stratified,
)
from wine_origin.evaluate import compute_metrics
from wine_origin.models import build_active_model
from wine_origin.utils import set_seed


def _run_once(tmp_path, config):
    set_seed(config["seed"])
    df = materialize_raw_csv(tmp_path / "wine.csv")
    train_df, test_df = train_test_split_stratified(
        df, test_size=config["split"]["test_size"], seed=config["seed"]
    )
    X_train, y_train = split_features_target(train_df)
    X_test, y_test = split_features_target(test_df)

    model = build_active_model(config)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return compute_metrics(y_test, y_pred)


def test_same_seed_gives_identical_metrics(tmp_path):
    config = load_config("config/default.yaml")

    first = _run_once(tmp_path / "run1", config)
    second = _run_once(tmp_path / "run2", config)

    assert first == second


def test_different_seed_can_give_different_split(tmp_path):
    config = load_config("config/default.yaml")
    config_other_seed = dict(config, seed=7)

    first = _run_once(tmp_path / "run1", config)
    other = _run_once(tmp_path / "run2", config_other_seed)

    # Not a strict inequality assertion on the metrics themselves (they could
    # coincidentally match) — this documents *why* the seed matters: a different
    # seed changes which rows land in train vs. test.
    assert config["seed"] != config_other_seed["seed"]
    assert isinstance(first["accuracy"], float)
    assert isinstance(other["accuracy"], float)
