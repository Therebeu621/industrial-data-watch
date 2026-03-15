from __future__ import annotations

import pandas as pd

from src.validators import validate_and_split


def test_validate_and_split_rejects_unknown_equipment_and_duplicates() -> None:
    df = pd.DataFrame(
        [
            {
                "timestamp": "2026-01-05T00:00:00",
                "site_id": "LILLE",
                "equipment_id": "LIL-CP-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 24.0,
                "temperature_c": 71.0,
                "pressure_bar": 7.1,
                "flow_m3_h": 232.0,
            },
            {
                "timestamp": "2026-01-05T00:00:00",
                "site_id": "LILLE",
                "equipment_id": "LIL-CP-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 24.0,
                "temperature_c": 71.0,
                "pressure_bar": 7.1,
                "flow_m3_h": 232.0,
            },
            {
                "timestamp": "2026-01-05T00:15:00",
                "site_id": "LILLE",
                "equipment_id": "UNKNOWN-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 24.0,
                "temperature_c": 70.0,
                "pressure_bar": 7.0,
                "flow_m3_h": 231.0,
            },
        ]
    )

    valid_df, rejected_df = validate_and_split(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 2
    assert any("duplicate_record" in reason for reason in rejected_df["rejection_reason"])
    assert any("unknown_equipment_id" in reason for reason in rejected_df["rejection_reason"])


def test_validate_and_split_rejects_missing_critical_value() -> None:
    df = pd.DataFrame(
        [
            {
                "timestamp": "2026-01-05T00:00:00",
                "site_id": "LILLE",
                "equipment_id": "LIL-PM-01",
                "equipment_type": "PUMP",
                "machine_state": "RUNNING",
                "energy_kwh": None,
                "temperature_c": 30.0,
                "pressure_bar": 3.0,
                "flow_m3_h": 110.0,
            }
        ]
    )

    valid_df, rejected_df = validate_and_split(df)

    assert valid_df.empty
    assert len(rejected_df) == 1
    assert rejected_df.iloc[0]["rejection_reason"] == "missing_critical_value"

