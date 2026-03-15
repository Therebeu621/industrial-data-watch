from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SAMPLE_OUTPUT_DIR = DATA_DIR / "sample_output"
RAW_DATA_PATH = RAW_DATA_DIR / "sensor_readings.csv"
CLEAN_OUTPUT_PATH = SAMPLE_OUTPUT_DIR / "cleaned_readings.csv"
ANOMALY_OUTPUT_PATH = SAMPLE_OUTPUT_DIR / "detected_anomalies.csv"
ML_ANOMALY_OUTPUT_PATH = SAMPLE_OUTPUT_DIR / "ml_detected_anomalies.csv"
REJECTED_OUTPUT_PATH = SAMPLE_OUTPUT_DIR / "rejected_records.csv"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "55432"))
DB_NAME = os.getenv("DB_NAME", "industrial_watch")
DB_USER = os.getenv("DB_USER", "industrial_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "industrial_pass")


def build_database_url() -> str:
    return (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
