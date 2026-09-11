"""Model construction and persistence.

Building models here (rather than inline in cli.py or scripts/run_experiment.py) keeps
one canonical definition of each model, so the CLI's ``train`` command, the notebooks,
and scripts/run_experiment.py can't quietly drift into three different versions of
"the logistic regression model".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_baseline() -> DummyClassifier:
    """The baseline every real model must beat: always predict the most frequent class.

    Why this matters: "84% accuracy" means nothing on its own. If simply guessing the
    majority class already gets 60%, a model at 84% is doing real work; if the majority
    class is 82% of the data, it's barely better than guessing. Report the baseline
    alongside every metric so the reader can judge that for themselves.
    """
    return DummyClassifier(strategy="most_frequent")


def build_logistic_regression(config: dict[str, Any]) -> Pipeline:
    """Standardize features, then fit a logistic regression — the primary model."""
    params = config["model"]["logistic_regression"]
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=params["max_iter"],
                    C=params["C"],
                    random_state=config["seed"],
                ),
            ),
        ]
    )


def build_random_forest(config: dict[str, Any]) -> RandomForestClassifier:
    """A tree-based model for comparison against the linear baseline model."""
    params = config["model"]["random_forest"]
    return RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        random_state=config["seed"],
    )


def build_active_model(config: dict[str, Any]) -> BaseEstimator:
    """Build whichever model ``config["model"]["active"]`` names.

    This is what ``train``/``predict`` use by default, so switching the project's
    primary model is a one-line config change instead of a code change.
    """
    active = config["model"]["active"]
    builders = {
        "logistic_regression": build_logistic_regression,
        "random_forest": build_random_forest,
    }
    if active not in builders:
        raise ValueError(f"Unknown model.active={active!r}, expected one of {list(builders)}")
    return builders[active](config)


def save_model(model: BaseEstimator, path: str | Path) -> None:
    """Save a fitted model with ``joblib`` (the standard for scikit-learn estimators)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: str | Path, hf_repo_id: str = "") -> BaseEstimator:
    """Load a fitted model from ``path``, falling back to Hugging Face Hub if missing.

    This is what makes the Streamlit app and ``predict`` work on a clean machine that
    has never run `python -m wine_origin train`: if nobody has trained a model locally yet, and
    ``hf_repo_id`` is configured (see ``config/default.yaml``'s ``huggingface.repo_id``
    and models/README.md), the model is downloaded from the Hub instead.

    Raises
    ------
    FileNotFoundError
        If the model is missing locally and no ``hf_repo_id`` is configured, with a
        message telling the caller to run `python -m wine_origin train` — not a bare stack trace.
    """
    path = Path(path)
    if path.exists():
        return joblib.load(path)

    if hf_repo_id:
        from huggingface_hub import hf_hub_download

        downloaded = hf_hub_download(repo_id=hf_repo_id, filename="model.joblib")
        return joblib.load(downloaded)

    raise FileNotFoundError(
        f"No model found at {path} and no huggingface.repo_id configured. "
        "Run `python -m wine_origin train` first, or see models/README.md."
    )
