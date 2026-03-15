from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.anomalies import detect_anomalies
from src.config import (
    ANOMALY_OUTPUT_PATH,
    CLEAN_OUTPUT_PATH,
    ML_ANOMALY_OUTPUT_PATH,
    REJECTED_OUTPUT_PATH,
)
from src.database import create_db_engine, init_schema, write_pipeline_results
from src.ml_anomalies import train_and_detect_anomalies
from src.transformers import enrich_sensor_data
from src.validators import validate_and_split

logger = logging.getLogger(__name__)


def _ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_pipeline(
    input_path: Path,
    clean_output_path: Path = CLEAN_OUTPUT_PATH,
    anomaly_output_path: Path = ANOMALY_OUTPUT_PATH,
    ml_anomaly_output_path: Path = ML_ANOMALY_OUTPUT_PATH,
    rejected_output_path: Path = REJECTED_OUTPUT_PATH,
    skip_db: bool = False,
) -> dict[str, int]:
    logger.info("Reading raw data from %s", input_path)
    raw_df = pd.read_csv(input_path)
    raw_df.insert(0, "source_row_number", range(1, len(raw_df) + 1))
    logger.info("Loaded %s raw records", len(raw_df))

    valid_df, rejected_df = validate_and_split(raw_df)
    logger.info("Validated records: %s", len(valid_df))
    logger.info("Rejected records: %s", len(rejected_df))

    clean_df = enrich_sensor_data(valid_df)
    anomalies_df = detect_anomalies(clean_df)
    logger.info("Detected anomalies: %s", len(anomalies_df))
    
    ml_anomalies_df = train_and_detect_anomalies(clean_df)
    logger.info("Detected ML anomalies: %s", len(ml_anomalies_df))

    _ensure_output_dir(clean_output_path)
    _ensure_output_dir(anomaly_output_path)
    _ensure_output_dir(ml_anomaly_output_path)
    _ensure_output_dir(rejected_output_path)
    clean_df.to_csv(clean_output_path, index=False)
    anomalies_df.to_csv(anomaly_output_path, index=False)
    ml_anomalies_df.to_csv(ml_anomaly_output_path, index=False)
    rejected_df.to_csv(rejected_output_path, index=False)
    logger.info("Exported CSV outputs to %s", clean_output_path.parent)

    if not skip_db:
        engine = create_db_engine()
        init_schema(engine)
        write_pipeline_results(engine, raw_df, clean_df, anomalies_df, rejected_df)

    return {
        "raw_records": len(raw_df),
        "valid_records": len(clean_df),
        "rejected_records": len(rejected_df),
        "anomalies": len(anomalies_df),
        "ml_anomalies": len(ml_anomalies_df),
    }

