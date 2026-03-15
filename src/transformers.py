from __future__ import annotations

import numpy as np
import pandas as pd


def enrich_sensor_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                *df.columns,
                "date",
                "hour_of_day",
                "is_running",
                "energy_per_flow",
            ]
        )

    clean_df = df.copy().sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)
    clean_df["date"] = clean_df["timestamp"].dt.date
    clean_df["hour_of_day"] = clean_df["timestamp"].dt.hour.astype(int)
    clean_df["is_running"] = clean_df["machine_state"].eq("RUNNING")
    clean_df["energy_per_flow"] = np.where(
        clean_df["flow_m3_h"] > 0,
        clean_df["energy_kwh"] / clean_df["flow_m3_h"],
        np.nan,
    )
    return clean_df

