"""Minimal interactive demo: enter (or sample) a wine's chemistry, get a prediction.

Run with `streamlit run app/streamlit_app.py` (see app/README.md). This is
intentionally small — one page, no auth, no database —
because for a course project the point is showing the model works, not building a
production frontend. See README.md's "other demo formats" note for what a
research-track or a heavier engineering-track project might do instead.
"""

from __future__ import annotations

import random

import pandas as pd
import streamlit as st

from wine_origin.config import load_config
from wine_origin.data import load_raw_csv, train_test_split_stratified
from wine_origin.models import load_model

CLASS_NAMES = ["class_0 (cultivar 1)", "class_1 (cultivar 2)", "class_2 (cultivar 3)"]

# (label, min, max, default, step) — bounds are a bit wider than the dataset's actual
# min/max so a curious user can push past the training data's range.
FEATURE_SPECS = [
    ("alcohol", 10.0, 16.0, 13.0, 0.01),
    ("malic_acid", 0.0, 7.0, 2.3, 0.01),
    ("ash", 1.0, 4.0, 2.4, 0.01),
    ("alcalinity_of_ash", 8.0, 35.0, 19.5, 0.1),
    ("magnesium", 60.0, 175.0, 100.0, 1.0),
    ("total_phenols", 0.5, 4.5, 2.3, 0.01),
    ("flavanoids", 0.0, 5.5, 2.0, 0.01),
    ("nonflavanoid_phenols", 0.0, 0.8, 0.36, 0.01),
    ("proanthocyanins", 0.0, 4.0, 1.6, 0.01),
    ("color_intensity", 1.0, 14.0, 5.1, 0.1),
    ("hue", 0.3, 1.9, 0.96, 0.01),
    ("od280/od315_of_diluted_wines", 1.0, 4.5, 2.6, 0.01),
    ("proline", 250.0, 1750.0, 747.0, 1.0),
]


@st.cache_resource
def get_config():
    return load_config("config/default.yaml")


@st.cache_resource
def get_model(_config):
    return load_model(_config["paths"]["model"], _config["huggingface"]["repo_id"])


@st.cache_data
def get_test_samples(_config):
    df = load_raw_csv(_config["paths"]["raw_data"])
    _train_df, test_df = train_test_split_stratified(
        df, test_size=_config["split"]["test_size"], seed=_config["seed"]
    )
    return test_df


def main() -> None:
    st.set_page_config(page_title="Wine cultivar classifier", page_icon="\U0001f377")
    st.title("\U0001f377 Wine cultivar classifier")
    st.caption(
        "Predicts which of 3 cultivars a wine comes from, from 13 chemical "
        "measurements. Trained on the UCI Wine Recognition dataset (178 samples) — "
        "see data/README.md for what that does and doesn't cover."
    )

    config = get_config()

    try:
        model = get_model(config)
    except FileNotFoundError:
        st.error(
            "No trained model found at `models/model.joblib`. Run "
            "`python -m wine_origin train` first, then reload this page."
        )
        st.stop()

    try:
        test_df = get_test_samples(config)
    except FileNotFoundError:
        test_df = None

    if "feature_values" not in st.session_state:
        st.session_state.feature_values = {
            name: default for name, _, _, default, _ in FEATURE_SPECS
        }

    if st.button("\U0001f3b2 Fill with a random test-set sample", disabled=test_df is None):
        row = test_df.sample(n=1, random_state=random.randint(0, 10_000)).iloc[0]
        st.session_state.feature_values = {name: float(row[name]) for name, *_ in FEATURE_SPECS}
        st.session_state.true_label = CLASS_NAMES[int(row["target"])]
    elif test_df is None:
        st.info("Run `python scripts/download_data.py` to enable sampling real test-set rows.")

    st.subheader("Chemical measurements")
    columns = st.columns(3)
    values = {}
    for i, (name, lo, hi, _default, step) in enumerate(FEATURE_SPECS):
        with columns[i % 3]:
            values[name] = st.number_input(
                name,
                min_value=lo,
                max_value=hi,
                value=st.session_state.feature_values[name],
                step=step,
            )
    st.session_state.feature_values = values

    if "true_label" in st.session_state:
        st.caption(f"Sampled row's true label: **{st.session_state.true_label}**")

    if st.button("Predict", type="primary"):
        X = pd.DataFrame([values])
        prediction = model.predict(X)[0]
        st.success(f"Predicted: **{CLASS_NAMES[int(prediction)]}**")

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            st.bar_chart(pd.Series(proba, index=CLASS_NAMES, name="probability"))

    st.divider()
    st.caption(
        "Model: logistic regression on standardized features (see results/experiments.md "
        "for how this was chosen over random forest and SVM). Limitations: trained on "
        "only 178 samples from one source (see data/README.md) — treat predictions on "
        "wines very different from that data with caution."
    )


if __name__ == "__main__":
    main()
