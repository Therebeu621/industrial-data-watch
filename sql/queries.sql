-- Average energy consumption per equipment and day
SELECT
    date,
    equipment_id,
    ROUND(AVG(energy_kwh)::numeric, 3) AS avg_energy_kwh
FROM clean_sensor_readings
GROUP BY date, equipment_id
ORDER BY date, equipment_id;

-- Energy consumption aggregated by equipment type
SELECT
    equipment_type,
    ROUND(SUM(energy_kwh)::numeric, 3) AS total_energy_kwh,
    ROUND(AVG(energy_kwh)::numeric, 3) AS avg_energy_kwh
FROM clean_sensor_readings
GROUP BY equipment_type
ORDER BY total_energy_kwh DESC;

-- Anomaly counts by type
SELECT
    anomaly_type,
    COUNT(*) AS anomaly_count
FROM detected_anomalies
GROUP BY anomaly_type
ORDER BY anomaly_count DESC, anomaly_type;

-- Most unstable machines based on anomaly volume
SELECT
    equipment_id,
    COUNT(*) AS anomaly_count
FROM detected_anomalies
GROUP BY equipment_id
ORDER BY anomaly_count DESC, equipment_id;

-- Rejection rate of the latest batch
WITH totals AS (
    SELECT
        (SELECT COUNT(*) FROM raw_sensor_readings) AS raw_count,
        (SELECT COUNT(*) FROM rejected_records) AS rejected_count
)
SELECT
    raw_count,
    rejected_count,
    ROUND(
        CASE
            WHEN raw_count = 0 THEN 0
            ELSE (rejected_count::numeric / raw_count::numeric) * 100
        END,
        2
    ) AS rejection_rate_pct
FROM totals;

