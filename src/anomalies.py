from __future__ import annotations

from typing import Any

import pandas as pd

from src.models import (
    ENERGY_SPIKE_ABSOLUTE,
    EXPECTED_INTERVAL,
    MISSING_TIMESLOT_THRESHOLD,
    PRESSURE_DELTA_THRESHOLDS,
    STOPPED_ENERGY_THRESHOLDS,
    STOPPED_STATES,
    TEMPERATURE_RANGES,
)


def _record(
    row: pd.Series,
    anomaly_type: str,
    severity: str,
    description: str,
    measured_value: float | None = None,
    previous_value: float | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": row["timestamp"],
        "equipment_id": row["equipment_id"],
        "equipment_type": row["equipment_type"],
        "anomaly_type": anomaly_type,
        "severity": severity,
        "description": description,
        "measured_value": measured_value,
        "previous_value": previous_value,
    }


def detect_anomalies(clean_df: pd.DataFrame) -> pd.DataFrame:
    anomalies: list[dict[str, Any]] = []
    if clean_df.empty:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "equipment_id",
                "equipment_type",
                "anomaly_type",
                "severity",
                "description",
                "measured_value",
                "previous_value",
            ]
        )

    for _, group in clean_df.sort_values(["equipment_id", "timestamp"]).groupby("equipment_id"):
        previous_row = None

        for _, row in group.iterrows():
            equipment_type = row["equipment_type"]

            if (
                row["machine_state"] in STOPPED_STATES
                and row["energy_kwh"] > STOPPED_ENERGY_THRESHOLDS[equipment_type]
            ):
                anomalies.append(
                    _record(
                        row,
                        "HIGH_ENERGY_WHILE_STOPPED",
                        "high",
                        (
                            f"Energy remained high while machine state was "
                            f"{row['machine_state']}"
                        ),
                        measured_value=float(row["energy_kwh"]),
                        previous_value=STOPPED_ENERGY_THRESHOLDS[equipment_type],
                    )
                )

            temp_min, temp_max = TEMPERATURE_RANGES[equipment_type]
            if row["temperature_c"] < temp_min or row["temperature_c"] > temp_max:
                anomalies.append(
                    _record(
                        row,
                        "TEMPERATURE_OUT_OF_RANGE",
                        "high",
                        "Temperature outside expected operating range",
                        measured_value=float(row["temperature_c"]),
                        previous_value=temp_max if row["temperature_c"] > temp_max else temp_min,
                    )
                )

            if previous_row is not None:
                pressure_delta = abs(row["pressure_bar"] - previous_row["pressure_bar"])
                if (
                    row["machine_state"] == "RUNNING"
                    and previous_row["machine_state"] == "RUNNING"
                    and pressure_delta >= PRESSURE_DELTA_THRESHOLDS[equipment_type]
                ):
                    anomalies.append(
                        _record(
                            row,
                            "PRESSURE_DROP_OR_SPIKE",
                            "medium",
                            "Pressure changed sharply between two consecutive readings",
                            measured_value=float(row["pressure_bar"]),
                            previous_value=float(previous_row["pressure_bar"]),
                        )
                    )

                energy_delta = row["energy_kwh"] - previous_row["energy_kwh"]
                if (
                    row["machine_state"] == "RUNNING"
                    and previous_row["machine_state"] == "RUNNING"
                    and previous_row["energy_kwh"] > 0
                    and energy_delta >= ENERGY_SPIKE_ABSOLUTE[equipment_type]
                    and row["energy_kwh"] >= previous_row["energy_kwh"] * 2.0
                ):
                    anomalies.append(
                        _record(
                            row,
                            "ENERGY_SPIKE",
                            "medium",
                            "Energy consumption increased sharply",
                            measured_value=float(row["energy_kwh"]),
                            previous_value=float(previous_row["energy_kwh"]),
                        )
                    )

                gap = row["timestamp"] - previous_row["timestamp"]
                if gap >= MISSING_TIMESLOT_THRESHOLD:
                    anomalies.append(
                        _record(
                            row,
                            "MISSING_TIMESLOT",
                            "low",
                            "Gap detected in the measurement timeline",
                            measured_value=gap.total_seconds() / 60.0,
                            previous_value=EXPECTED_INTERVAL.total_seconds() / 60.0,
                        )
                    )

            previous_row = row

    anomaly_df = pd.DataFrame(anomalies)
    if anomaly_df.empty:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "equipment_id",
                "equipment_type",
                "anomaly_type",
                "severity",
                "description",
                "measured_value",
                "previous_value",
            ]
        )

    return anomaly_df.sort_values(["timestamp", "equipment_id", "anomaly_type"]).reset_index(
        drop=True
    )
