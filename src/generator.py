from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from src.models import EQUIPMENT_CATALOG, EXPECTED_COLUMNS


def _state_for_hour(rng: random.Random, hour: int) -> str:
    if 7 <= hour <= 18:
        choices = ["RUNNING", "IDLE", "STOPPED"]
        weights = [0.78, 0.17, 0.05]
    else:
        choices = ["RUNNING", "IDLE", "STOPPED", "MAINTENANCE"]
        weights = [0.45, 0.30, 0.15, 0.10]
    return rng.choices(choices, weights=weights, k=1)[0]


def _baseline_values(equipment_type: str, machine_state: str) -> tuple[float, float, float, float]:
    base = {
        "COMPRESSOR": (24.0, 72.0, 7.2, 230.0),
        "PUMP": (11.0, 31.0, 3.4, 120.0),
        "CHILLER": (18.0, 8.0, 2.8, 155.0),
        "PACKAGING_LINE": (15.0, 28.0, 1.8, 80.0),
    }[equipment_type]

    energy, temperature, pressure, flow = base

    if machine_state == "IDLE":
        return energy * 0.35, temperature - 2.0, pressure * 0.45, flow * 0.20
    if machine_state in {"STOPPED", "MAINTENANCE"}:
        return energy * 0.08, temperature - 5.0, pressure * 0.10, flow * 0.02
    return base


def generate_sensor_dataset(
    output_path: Path,
    seed: int = 42,
    intervals: int = 96,
) -> pd.DataFrame:
    rng = random.Random(seed)
    start_time = datetime(2026, 1, 5, 0, 0, 0)
    records: list[dict[str, object]] = []

    for equipment in EQUIPMENT_CATALOG:
        equipment_id = equipment["equipment_id"]
        site_id = equipment["site_id"]
        equipment_type = equipment["equipment_type"]

        for offset in range(intervals):
            timestamp = start_time + timedelta(minutes=15 * offset)
            machine_state = _state_for_hour(rng, timestamp.hour)
            energy, temperature, pressure, flow = _baseline_values(
                equipment_type,
                machine_state,
            )

            records.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "site_id": site_id,
                    "equipment_id": equipment_id,
                    "equipment_type": equipment_type,
                    "machine_state": machine_state,
                    "energy_kwh": round(rng.gauss(energy, max(energy * 0.06, 0.2)), 3),
                    "temperature_c": round(
                        rng.gauss(temperature, max(abs(temperature) * 0.03, 0.3)),
                        3,
                    ),
                    "pressure_bar": round(
                        max(rng.gauss(pressure, max(pressure * 0.04, 0.05)), 0.0),
                        3,
                    ),
                    "flow_m3_h": round(
                        max(rng.gauss(flow, max(flow * 0.05, 0.3)), 0.0),
                        3,
                    ),
                }
            )

    df = pd.DataFrame(records, columns=EXPECTED_COLUMNS)

    high_energy_mask = (
        (df["equipment_id"] == "LIL-CP-01")
        & (df["timestamp"] == "2026-01-05T12:00:00")
    )
    df.loc[high_energy_mask, ["machine_state", "energy_kwh"]] = ["STOPPED", 12.8]

    high_temperature_mask = (
        (df["equipment_id"] == "LIL-CH-01")
        & (df["timestamp"] == "2026-01-05T09:15:00")
    )
    df.loc[high_temperature_mask, "temperature_c"] = 29.5

    pressure_spike_mask = (
        (df["equipment_id"] == "LIL-CP-02")
        & (df["timestamp"] == "2026-01-05T15:30:00")
    )
    pressure_prev_mask = (
        (df["equipment_id"] == "LIL-CP-02")
        & (df["timestamp"] == "2026-01-05T15:15:00")
    )
    df.loc[pressure_prev_mask, ["machine_state", "pressure_bar"]] = ["RUNNING", 7.2]
    df.loc[pressure_spike_mask, ["machine_state", "pressure_bar"]] = ["RUNNING", 11.4]

    energy_prev_mask = (
        (df["equipment_id"] == "ARR-PK-01")
        & (df["timestamp"] == "2026-01-05T13:00:00")
    )
    energy_spike_mask = (
        (df["equipment_id"] == "ARR-PK-01")
        & (df["timestamp"] == "2026-01-05T13:15:00")
    )
    df.loc[energy_prev_mask, ["machine_state", "energy_kwh"]] = ["RUNNING", 11.5]
    df.loc[energy_spike_mask, ["machine_state", "energy_kwh"]] = ["RUNNING", 29.8]

    missing_gap_mask = (
        (df["equipment_id"] == "ARR-PM-01")
        & (df["timestamp"] == "2026-01-05T17:15:00")
    )
    df = df.loc[~missing_gap_mask].copy()

    duplicate_row = df.loc[
        (df["equipment_id"] == "ARR-PK-01")
        & (df["timestamp"] == "2026-01-05T10:00:00")
    ].iloc[0].to_dict()
    df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)

    invalid_unknown = {
        "timestamp": "2026-01-05T11:00:00",
        "site_id": "LILLE",
        "equipment_id": "LIL-UNK-99",
        "equipment_type": "PUMP",
        "machine_state": "RUNNING",
        "energy_kwh": 10.5,
        "temperature_c": 24.0,
        "pressure_bar": 3.1,
        "flow_m3_h": 90.0,
    }
    invalid_missing_value = {
        "timestamp": "2026-01-05T14:15:00",
        "site_id": "LILLE",
        "equipment_id": "LIL-PM-01",
        "equipment_type": "PUMP",
        "machine_state": "RUNNING",
        "energy_kwh": None,
        "temperature_c": 30.1,
        "pressure_bar": 3.2,
        "flow_m3_h": 118.0,
    }
    invalid_negative_flow = {
        "timestamp": "2026-01-05T18:45:00",
        "site_id": "ARRAS",
        "equipment_id": "ARR-PK-01",
        "equipment_type": "PACKAGING_LINE",
        "machine_state": "RUNNING",
        "energy_kwh": 14.2,
        "temperature_c": 27.5,
        "pressure_bar": 1.9,
        "flow_m3_h": -20.0,
    }
    invalid_state = {
        "timestamp": "2026-01-05T19:00:00",
        "site_id": "LILLE",
        "equipment_id": "LIL-CP-02",
        "equipment_type": "COMPRESSOR",
        "machine_state": "BROKEN",
        "energy_kwh": 20.2,
        "temperature_c": 74.2,
        "pressure_bar": 7.0,
        "flow_m3_h": 210.0,
    }

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [
                    invalid_unknown,
                    invalid_missing_value,
                    invalid_negative_flow,
                    invalid_state,
                ]
            ),
        ],
        ignore_index=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
