"""Feature preparation.

The wine dataset's 13 chemical measurements are already numeric, complete, and
comparably scaled to what a real analysis would use directly — see
notebooks/01-data-exploration.ipynb. There is no hand-engineered feature to add
without inventing one for its own sake. Scaling happens inside the model pipeline
(see models.py's ``StandardScaler``), not here, since it's a model concern rather
than a dataset concern.

This module exists as a placeholder in the pattern every project in this template
follows: once your project needs real feature engineering (derived columns, text
vectorization, encoding), it goes here rather than inline in data.py or models.py,
so data.py stays "get me clean rows" and models.py stays "get me a fitted estimator".
"""

from __future__ import annotations

import pandas as pd


def identity_features(X: pd.DataFrame) -> pd.DataFrame:
    """Return features unchanged. Replace with real transformations if you add any."""
    return X
