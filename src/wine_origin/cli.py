"""Single entry point for this project: ``python -m wine_origin <command>``.

One CLI with subcommands (rather than three separate scripts) means there's one place
that knows how to load config, set the seed, and set up logging — every command gets
that for free instead of each script reimplementing it slightly differently.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from wine_origin import evaluate as evaluate_mod
from wine_origin import models as models_mod
from wine_origin.config import load_config
from wine_origin.data import (
    load_raw_csv,
    split_features_target,
    train_test_split_stratified,
)
from wine_origin.utils import env_info, set_seed, setup_logging

logger = logging.getLogger(__name__)

CLASS_NAMES = ["class_0", "class_1", "class_2"]


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to a YAML config file (default: config/default.yaml)",
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        metavar="key.path=value",
        help="Override a config value, e.g. --override model.random_forest.n_estimators=300. "
        "Repeatable.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wine_origin",
        description="Train, evaluate, and run predictions for the wine cultivar classifier.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser(
        "train", help="Train the configured model and save it to models/model.joblib"
    )
    _add_common_args(train_parser)

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate a trained model and write results/metrics.json"
    )
    _add_common_args(evaluate_parser)
    evaluate_parser.add_argument(
        "--model", default=None, help="Path to a model file (default: from config)"
    )

    predict_parser = subparsers.add_parser(
        "predict", help="Predict the cultivar for a single wine sample from a JSON file"
    )
    _add_common_args(predict_parser)
    predict_parser.add_argument(
        "--model", default=None, help="Path to a model file (default: from config)"
    )
    predict_parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON file with the 13 feature values, e.g. examples/sample.json",
    )

    return parser


def cmd_train(config: dict) -> None:
    set_seed(config["seed"])
    df = load_raw_csv(config["paths"]["raw_data"])
    train_df, _test_df = train_test_split_stratified(
        df, test_size=config["split"]["test_size"], seed=config["seed"]
    )
    X_train, y_train = split_features_target(train_df)

    model = models_mod.build_active_model(config)
    logger.info("Training %s on %d samples", config["model"]["active"], len(X_train))
    model.fit(X_train, y_train)

    models_mod.save_model(model, config["paths"]["model"])
    logger.info("Saved model to %s", config["paths"]["model"])


def cmd_evaluate(config: dict, model_path: str | None) -> None:
    set_seed(config["seed"])
    model_path = model_path or config["paths"]["model"]
    model = models_mod.load_model(model_path, config["huggingface"]["repo_id"])

    df = load_raw_csv(config["paths"]["raw_data"])
    _train_df, test_df = train_test_split_stratified(
        df, test_size=config["split"]["test_size"], seed=config["seed"]
    )
    X_test, y_test = split_features_target(test_df)

    y_pred = model.predict(X_test)
    metrics = evaluate_mod.compute_metrics(y_test, y_pred)

    X_all, y_all = split_features_target(df)
    metrics.update(
        evaluate_mod.cross_validate_accuracy(
            model, X_all, y_all, n_splits=config["cv"]["n_splits"], seed=config["seed"]
        )
    )
    metrics["env"] = env_info()

    metrics_path = Path(config["paths"]["metrics"])
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")
    logger.info("Wrote metrics to %s", metrics_path)

    evaluate_mod.plot_confusion_matrix(
        metrics["confusion_matrix"], CLASS_NAMES, config["paths"]["confusion_matrix"]
    )
    logger.info("Wrote confusion matrix to %s", config["paths"]["confusion_matrix"])

    print(f"accuracy={metrics['accuracy']:.4f} macro_f1={metrics['macro_f1']:.4f}")


def cmd_predict(config: dict, model_path: str | None, input_path: str) -> None:
    model_path = model_path or config["paths"]["model"]
    model = models_mod.load_model(model_path, config["huggingface"]["repo_id"])

    sample = json.loads(Path(input_path).read_text())
    X = pd.DataFrame([sample])

    prediction = model.predict(X)[0]
    result = {"prediction": CLASS_NAMES[int(prediction)]}
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        result["probabilities"] = dict(zip(CLASS_NAMES, (float(p) for p in proba)))

    print(json.dumps(result, indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config, args.override)
    setup_logging(config["logging"]["level"])

    if args.command == "train":
        cmd_train(config)
    elif args.command == "evaluate":
        cmd_evaluate(config, args.model)
    elif args.command == "predict":
        cmd_predict(config, args.model, args.input)


if __name__ == "__main__":
    main()
