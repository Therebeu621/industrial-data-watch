from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

EXPECTED_COLUMNS = [
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

NUMERIC_COLUMNS = [
    "energy_kwh",
    "temperature_c",
    "pressure_bar",
    "flow_m3_h",
]

ALLOWED_EQUIPMENT_TYPES = {
    "COMPRESSOR",
    "PUMP",
    "CHILLER",
    "PACKAGING_LINE",
}

ALLOWED_MACHINE_STATES = {
    "RUNNING",
    "IDLE",
    "STOPPED",
    "MAINTENANCE",
}

STOPPED_STATES = {"STOPPED", "MAINTENANCE"}
EXPECTED_INTERVAL = timedelta(minutes=15)
MISSING_TIMESLOT_THRESHOLD = timedelta(minutes=30)

EQUIPMENT_CATALOG = [
    {
        "equipment_id": "LIL-CP-01",
        "site_id": "LILLE",
        "equipment_type": "COMPRESSOR",
        "commissioned_at": date(2021, 5, 12),
        "status": "ACTIVE",
    },
    {
        "equipment_id": "LIL-CP-02",
        "site_id": "LILLE",
        "equipment_type": "COMPRESSOR",
        "commissioned_at": date(2022, 2, 2),
        "status": "ACTIVE",
    },
    {
        "equipment_id": "LIL-PM-01",
        "site_id": "LILLE",
        "equipment_type": "PUMP",
        "commissioned_at": date(2020, 9, 1),
        "status": "ACTIVE",
    },
    {
        "equipment_id": "LIL-CH-01",
        "site_id": "LILLE",
        "equipment_type": "CHILLER",
        "commissioned_at": date(2019, 3, 15),
        "status": "ACTIVE",
    },
    {
        "equipment_id": "ARR-PM-01",
        "site_id": "ARRAS",
        "equipment_type": "PUMP",
        "commissioned_at": date(2021, 11, 18),
        "status": "ACTIVE",
    },
    {
        "equipment_id": "ARR-PK-01",
        "site_id": "ARRAS",
        "equipment_type": "PACKAGING_LINE",
        "commissioned_at": date(2023, 1, 6),
        "status": "ACTIVE",
    },
]

EQUIPMENT_INDEX = {item["equipment_id"]: item for item in EQUIPMENT_CATALOG}

TEMPERATURE_RANGES = {
    "COMPRESSOR": (35.0, 95.0),
    "PUMP": (10.0, 60.0),
    "CHILLER": (2.0, 18.0),
    "PACKAGING_LINE": (15.0, 55.0),
}

STOPPED_ENERGY_THRESHOLDS = {
    "COMPRESSOR": 4.0,
    "PUMP": 2.5,
    "CHILLER": 3.0,
    "PACKAGING_LINE": 5.0,
}

PRESSURE_DELTA_THRESHOLDS = {
    "COMPRESSOR": 2.5,
    "PUMP": 1.5,
    "CHILLER": 1.0,
    "PACKAGING_LINE": 1.2,
}

ENERGY_SPIKE_ABSOLUTE = {
    "COMPRESSOR": 8.0,
    "PUMP": 4.0,
    "CHILLER": 6.0,
    "PACKAGING_LINE": 7.0,
}


def equipment_reference_df() -> pd.DataFrame:
    return pd.DataFrame(EQUIPMENT_CATALOG)

