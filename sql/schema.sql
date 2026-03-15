CREATE TABLE IF NOT EXISTS equipment_reference (
    equipment_id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    commissioned_at DATE NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_sensor_readings (
    reading_id SERIAL PRIMARY KEY,
    source_row_number INTEGER NOT NULL,
    timestamp TEXT,
    site_id TEXT,
    equipment_id TEXT,
    equipment_type TEXT,
    machine_state TEXT,
    energy_kwh TEXT,
    temperature_c TEXT,
    pressure_bar TEXT,
    flow_m3_h TEXT,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clean_sensor_readings (
    reading_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    site_id TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    machine_state TEXT NOT NULL,
    energy_kwh NUMERIC(10, 3) NOT NULL,
    temperature_c NUMERIC(10, 3) NOT NULL,
    pressure_bar NUMERIC(10, 3) NOT NULL,
    flow_m3_h NUMERIC(10, 3) NOT NULL,
    date DATE NOT NULL,
    hour_of_day INTEGER NOT NULL,
    is_running BOOLEAN NOT NULL,
    energy_per_flow NUMERIC(12, 6),
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detected_anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    equipment_id TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    measured_value NUMERIC(12, 3),
    previous_value NUMERIC(12, 3),
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rejected_records (
    rejection_id SERIAL PRIMARY KEY,
    source_row_number INTEGER NOT NULL,
    equipment_id TEXT,
    rejection_reason TEXT NOT NULL,
    raw_payload TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

