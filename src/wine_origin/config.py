"""Load and validate the YAML config that drives every command in this project."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

REQUIRED_KEYS = ("seed", "paths", "split", "cv", "model", "logging")


class ConfigError(ValueError):
    """Raised when config/default.yaml (or an override) is missing or malformed."""


def load_config(path: str | Path, overrides: list[str] | None = None) -> dict[str, Any]:
    """Load a YAML config file and apply ``key.path=value`` overrides.

    Parameters
    ----------
    path : str or Path
        Path to a YAML file, e.g. ``config/default.yaml``.
    overrides : list of str, optional
        Strings of the form ``"model.random_forest.n_estimators=300"``, as passed via
        the CLI's repeatable ``--override`` flag. Values are parsed with
        :func:`yaml.safe_load` so ``42``, ``true``, ``null``, and quoted strings all
        come out as the right Python type.

    Returns
    -------
    dict
        The merged configuration.

    Raises
    ------
    ConfigError
        If the file is missing, isn't a mapping, or is missing a required top-level key.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ConfigError(f"{config_path} must contain a YAML mapping at the top level")

    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        raise ConfigError(f"{config_path} is missing required key(s): {', '.join(missing)}")

    config = copy.deepcopy(config)
    for override in overrides or []:
        _apply_override(config, override)
    return config


def _apply_override(config: dict[str, Any], override: str) -> None:
    if "=" not in override:
        raise ConfigError(f"--override must be 'key.path=value', got: {override!r}")
    dotted_key, raw_value = override.split("=", 1)
    value = yaml.safe_load(raw_value)

    node = config
    *parents, leaf = dotted_key.split(".")
    for part in parents:
        if part not in node or not isinstance(node[part], dict):
            raise ConfigError(f"--override key path does not exist in config: {dotted_key!r}")
        node = node[part]
    if leaf not in node:
        raise ConfigError(f"--override key path does not exist in config: {dotted_key!r}")
    node[leaf] = value
