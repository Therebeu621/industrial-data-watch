from __future__ import annotations

import pandas as pd

from src.anomalies import detect_anomalies
from src.transformers import enrich_sensor_data


def test_detect_anomalies_flags_temperature_and_stopped_energy() -> None:
    df = pd.DataFrame(
        [
            {
                "timestamp": pd.Timestamp("2026-01-05T00:00:00"),
                "site_id": "LILLE",
                "equipment_id": "LIL-CH-01",
                "equipment_type": "CHILLER",
                "machine_state": "STOPPED",
                "energy_kwh": 5.2,
                "temperature_c": 28.0,
                "pressure_bar": 2.4,
                "flow_m3_h": 2.0,
            }
        ]
    )

    anomalies = detect_anomalies(enrich_sensor_data(df))
    anomaly_types = set(anomalies["anomaly_type"].tolist())

    assert "HIGH_ENERGY_WHILE_STOPPED" in anomaly_types
    assert "TEMPERATURE_OUT_OF_RANGE" in anomaly_types


def test_detect_anomalies_flags_missing_timeslot_and_energy_spike() -> None:
    df = pd.DataFrame(
        [
            {
                "timestamp": pd.Timestamp("2026-01-05T00:00:00"),
                "site_id": "LILLE",
                "equipment_id": "LIL-CP-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 20.0,
                "temperature_c": 70.0,
                "pressure_bar": 7.0,
                "flow_m3_h": 220.0,
            },
            {
                "timestamp": pd.Timestamp("2026-01-05T00:45:00"),
                "site_id": "LILLE",
                "equipment_id": "LIL-CP-01",
                "equipment_type": "COMPRESSOR",
                "machine_state": "RUNNING",
                "energy_kwh": 40.0,
                "temperature_c": 72.0,
                "pressure_bar": 7.1,
                "flow_m3_h": 225.0,
            },
        ]
    )

    anomalies = detect_anomalies(enrich_sensor_data(df))
    anomaly_types = set(anomalies["anomaly_type"].tolist())

    assert "MISSING_TIMESLOT" in anomaly_types
    assert "ENERGY_SPIKE" in anomaly_types

