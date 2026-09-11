"""Small cross-cutting helpers: seeding, environment fingerprinting, logging."""

from __future__ import annotations

import logging
import platform
import random
import subprocess
import sys
from importlib.metadata import version
from typing import Any

import numpy as np


def set_seed(seed: int) -> None:
    """Fix every source of randomness this project uses.

    Why this matters: a "reproducible" result that only sets ``numpy``'s seed but not
    Python's ``random`` module (or vice versa) is not actually reproducible — whichever
    one you forgot will silently drift between runs. Extend this function, don't
    scatter extra ``.seed()`` calls elsewhere, whenever a new source of randomness is
    introduced.

    Parameters
    ----------
    seed : int
        Seed value applied to ``random`` and ``numpy``.

    Notes
    -----
    If you add PyTorch: ``torch.manual_seed(seed)`` and, for full GPU determinism,
    ``torch.use_deterministic_algorithms(True)``. If you add TensorFlow:
    ``tf.random.set_seed(seed)``. Neither is a dependency of this project.
    """
    random.seed(seed)
    np.random.seed(seed)


def _git_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return "unknown"


def env_info() -> dict[str, Any]:
    """Capture a fingerprint of the environment a run happened in.

    This is what turns "it worked on my machine" into something checkable: it gets
    written into ``results/metrics.json`` alongside the metrics, so anyone reading the
    results table can see exactly what produced it and try to reproduce it.

    Returns
    -------
    dict
        Python/OS/platform info, versions of the key libraries this project depends
        on, and the current git commit hash (``"unknown"`` outside a git repo).
    """
    packages = ["numpy", "pandas", "scikit-learn", "matplotlib", "joblib"]
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "package_versions": {pkg: _safe_version(pkg) for pkg in packages},
        "git_commit": _git_commit_hash(),
    }


def _safe_version(package: str) -> str:
    try:
        return version(package)
    except Exception:
        return "unknown"


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging once, at the format every CLI command shares.

    Why this matters: ``print`` statements can't be turned off, filtered by severity,
    or redirected — the first time you need to silence noisy library output while
    debugging your own code, you'll wish everything used ``logging`` instead.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
