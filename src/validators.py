from __future__ import annotations

import json
from typing import Iterable

import pandas as pd

from src.models import (
    ALLOWED_EQUIPMENT_TYPES,
    ALLOWED_MACHINE_STATES,
    EQUIPMENT_INDEX,
    EXPECTED_COLUMNS,
    NUMERIC_COLUMNS,
)


def _normalize_text(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip().str.upper()
    return values.where(series.notna(), pd.NA)


def _append_reason(reason_buckets: list[list[str]], indexes: Iterable[int], reason: str) -> None:
    for idx in indexes:
        reason_buckets[idx].append(reason)


def validate_and_split(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in raw_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = raw_df.copy()
    if "source_row_number" not in df.columns:
        df.insert(0, "source_row_number", range(1, len(df) + 1))

    df = df[["source_row_number", *EXPECTED_COLUMNS]].copy()
    original_df = df.copy()

    df["site_id"] = _normalize_text(df["site_id"])
    df["equipment_id"] = _normalize_text(df["equipment_id"])
    df["equipment_type"] = _normalize_text(df["equipment_type"])
    df["machine_state"] = _normalize_text(df["machine_state"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    reasons: list[list[str]] = [[] for _ in range(len(df))]

    critical_columns = [
        "timestamp",
        "site_id",
        "equipment_id",
        "equipment_type",
        "machine_state",
        "energy_kwh",
        "temperature_c",
        "pressure_bar",
        "flow_m3_h",
    ]
    critical_missing = df[critical_columns].isna().any(axis=1)
    _append_reason(reasons, critical_missing[critical_missing].index, "missing_critical_value")

    unknown_equipment = ~df["equipment_id"].isin(EQUIPMENT_INDEX.keys())
    _append_reason(reasons, unknown_equipment[unknown_equipment].index, "unknown_equipment_id")

    invalid_equipment_type = ~df["equipment_type"].isin(ALLOWED_EQUIPMENT_TYPES)
    _append_reason(
        reasons,
        invalid_equipment_type[invalid_equipment_type].index,
        "invalid_equipment_type",
    )

    invalid_machine_state = ~df["machine_state"].isin(ALLOWED_MACHINE_STATES)
    _append_reason(
        reasons,
        invalid_machine_state[invalid_machine_state].index,
        "invalid_machine_state",
    )

    type_mismatch = df.apply(
        lambda row: (
            row["equipment_id"] in EQUIPMENT_INDEX
            and row["equipment_type"] != EQUIPMENT_INDEX[row["equipment_id"]]["equipment_type"]
        ),
        axis=1,
    )
    _append_reason(reasons, type_mismatch[type_mismatch].index, "equipment_type_mismatch")

    negative_values = (
        (df["energy_kwh"] < 0)
        | (df["pressure_bar"] < 0)
        | (df["flow_m3_h"] < 0)
    )
    _append_reason(reasons, negative_values[negative_values].index, "negative_measurement")

    implausible_values = (
        (df["temperature_c"] < -30)
        | (df["temperature_c"] > 130)
        | (df["pressure_bar"] > 25)
        | (df["flow_m3_h"] > 5000)
        | (df["energy_kwh"] > 500)
    )
    _append_reason(reasons, implausible_values[implausible_values].index, "implausible_measurement")

    duplicate_rows = df.duplicated(subset=EXPECTED_COLUMNS, keep="first")
    _append_reason(reasons, duplicate_rows[duplicate_rows].index, "duplicate_record")

    rejected_mask = pd.Series([bool(bucket) for bucket in reasons], index=df.index)

    rejected_df = original_df.loc[rejected_mask, ["source_row_number", "equipment_id"]].copy()
    rejected_df["rejection_reason"] = [";".join(reasons[idx]) for idx in rejected_df.index]
    rejected_df["raw_payload"] = original_df.loc[rejected_mask].apply(
        lambda row: json.dumps(
            {
                key: (None if pd.isna(value) else str(value))
                for key, value in row.to_dict().items()
            },
            sort_keys=True,
        ),
        axis=1,
    )

    valid_df = df.loc[~rejected_mask, EXPECTED_COLUMNS].copy()
    valid_df = valid_df.sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)
    return valid_df, rejected_df.reset_index(drop=True)

