from __future__ import annotations

import pandas as pd

from src.ml_anomalies import train_and_detect_anomalies


def test_train_and_detect_anomalies_returns_scored_rows() -> None:
    rows = []
    for index in range(60):
        rows.append(
            {
                "timestamp": pd.Timestamp("2026-01-05T00:00:00") + pd.Timedelta(minutes=15 * index),
                "site_id": "LILLE",
                "equipment_id": "LIL-CP-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 24.0,
                "temperature_c": 72.0,
                "pressure_bar": 7.2,
                "flow_m3_h": 230.0,
                "date": pd.Timestamp("2026-01-05").date(),
                "hour_of_day": index % 24,
                "is_running": True,
                "energy_per_flow": 24.0 / 230.0,
            }
        )

    rows.append(
        {
            "timestamp": pd.Timestamp("2026-01-05T15:00:00"),
            "site_id": "LILLE",
            "equipment_id": "LIL-CP-01",
            "equipment_type": "COMPRESSOR",
            "machine_state": "RUNNING",
            "energy_kwh": 80.0,
            "temperature_c": 110.0,
            "pressure_bar": 15.0,
            "flow_m3_h": 40.0,
            "date": pd.Timestamp("2026-01-05").date(),
            "hour_of_day": 15,
            "is_running": True,
            "energy_per_flow": 2.0,
        }
    )

    anomalies = train_and_detect_anomalies(pd.DataFrame(rows), contamination=0.02)

    assert not anomalies.empty
    assert "ml_anomaly_score" in anomalies.columns
    assert (anomalies["energy_kwh"] == 80.0).any()

