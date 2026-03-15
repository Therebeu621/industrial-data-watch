from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.config import RAW_DATA_PATH
from src.generator import generate_sensor_dataset
from src.logging_utils import configure_logging
from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Industrial sensor data pipeline demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a sample raw dataset")
    generate_parser.add_argument(
        "--output",
        type=Path,
        default=RAW_DATA_PATH,
        help="Target CSV path for the generated dataset",
    )
    generate_parser.add_argument("--seed", type=int, default=42, help="Random seed")

    run_parser = subparsers.add_parser("run", help="Run validation, cleaning and anomaly detection")
    run_parser.add_argument(
        "--input",
        type=Path,
        default=RAW_DATA_PATH,
        help="Input CSV path",
    )
    run_parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip PostgreSQL loading and only export CSV outputs",
    )

    all_parser = subparsers.add_parser("all", help="Generate data and run the full pipeline")
    all_parser.add_argument("--seed", type=int, default=42, help="Random seed")
    all_parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip PostgreSQL loading and only export CSV outputs",
    )
    return parser


def main() -> None:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "generate":
        dataset = generate_sensor_dataset(args.output, seed=args.seed)
        logger.info("Generated %s rows in %s", len(dataset), args.output)
        return

    if args.command == "run":
        summary = run_pipeline(args.input, skip_db=args.skip_db)
        logger.info("Pipeline summary: %s", summary)
        return

    if args.command == "all":
        dataset = generate_sensor_dataset(RAW_DATA_PATH, seed=args.seed)
        logger.info("Generated %s rows in %s", len(dataset), RAW_DATA_PATH)
        summary = run_pipeline(RAW_DATA_PATH, skip_db=args.skip_db)
        logger.info("Pipeline summary: %s", summary)


if __name__ == "__main__":
    main()

