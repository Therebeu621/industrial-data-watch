from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import SCHEMA_PATH, build_database_url
from src.models import EXPECTED_COLUMNS, equipment_reference_df

logger = logging.getLogger(__name__)


def create_db_engine() -> Engine:
    return create_engine(build_database_url())


def init_schema(engine: Engine, schema_path: Path = SCHEMA_PATH) -> None:
    sql_script = schema_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql_script.split(";") if statement.strip()]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def reset_demo_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE detected_anomalies, clean_sensor_readings, "
                "raw_sensor_readings, rejected_records RESTART IDENTITY"
            )
        )
        connection.execute(text("DELETE FROM equipment_reference"))


def load_reference_data(engine: Engine) -> None:
    reference_df = equipment_reference_df()
    reference_df.to_sql("equipment_reference", engine, if_exists="append", index=False, method="multi")


def prepare_raw_for_storage(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    if "source_row_number" not in df.columns:
        df.insert(0, "source_row_number", range(1, len(df) + 1))
    df = df[["source_row_number", *EXPECTED_COLUMNS]].copy()
    for column in EXPECTED_COLUMNS:
        df[column] = df[column].where(df[column].notna(), None)
        df[column] = df[column].map(lambda value: None if value is None else str(value))
    return df


def write_pipeline_results(
    engine: Engine,
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    anomalies_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
) -> None:
    reset_demo_tables(engine)
    load_reference_data(engine)
    prepare_raw_for_storage(raw_df).to_sql(
        "raw_sensor_readings",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    if not clean_df.empty:
        clean_df.to_sql(
            "clean_sensor_readings",
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )

    if not anomalies_df.empty:
        anomalies_df.to_sql(
            "detected_anomalies",
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )

    if not rejected_df.empty:
        rejected_df.to_sql(
            "rejected_records",
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )

    logger.info("Loaded data into PostgreSQL")

