# industrial-data-watch

`industrial-data-watch` is a small data engineering prototype built around industrial and energy sensor data.

The project simulates measurements emitted by machines such as compressors, pumps and chillers, then runs a simple pipeline to:

- ingest raw CSV data
- validate and clean records
- detect a few operational anomalies
- export analysis-ready datasets
- load curated results into PostgreSQL

The scope is intentionally limited. This is not a production data platform. It is a compact, reproducible project meant to show solid fundamentals around Python, SQL, Docker, data quality and pipeline structure.

## Why this project

The idea behind the repository is simple:

> Explore how a backend-oriented developer can structure, validate and exploit technical data in a realistic industrial context.

It focuses on:

- data reliability
- explicit validation rules
- simple anomaly detection
- readable SQL schema
- reproducible local execution

## Functional overview

The dataset models timestamped readings for several industrial assets:

- compressors
- pumps
- chillers
- packaging lines

Each reading contains:

- `timestamp`
- `site_id`
- `equipment_id`
- `equipment_type`
- `machine_state`
- `energy_kwh`
- `temperature_c`
- `pressure_bar`
- `flow_m3_h`

The pipeline handles:

1. raw CSV ingestion
2. schema and quality checks
3. duplicate and invalid record rejection
4. enrichment of clean records
5. rule-based anomaly detection
6. optional exploratory ML anomaly scoring
7. PostgreSQL loading

## Project structure

```text
industrial-data-watch/
|-- data/
|   |-- raw/
|   |   `-- sensor_readings.csv
|   `-- sample_output/
|       |-- cleaned_readings.csv
|       |-- detected_anomalies.csv
|       `-- rejected_records.csv
|-- scripts/
|   |-- init_db.sh
|   `-- run_pipeline.sh
|-- sql/
|   |-- queries.sql
|   `-- schema.sql
|-- src/
|   |-- anomalies.py
|   |-- config.py
|   |-- database.py
|   |-- generator.py
|   |-- logging_utils.py
|   |-- main.py
|   |-- ml_anomalies.py
|   |-- models.py
|   |-- pipeline.py
|   |-- transformers.py
|   `-- validators.py
|-- tests/
|   |-- test_anomalies.py
|   `-- test_validators.py
|-- .env.example
|-- docker-compose.yml
|-- Makefile
`-- requirements.txt
```

## Architecture

```text
                    +----------------------+
                    | data/raw/*.csv       |
                    | generated telemetry  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | validation layer     |
                    | schema + quality     |
                    +----+------------+----+
                         |            |
                         |            v
                         |   +----------------------+
                         |   | rejected_records     |
                         |   | invalid rows + cause |
                         |   +----------------------+
                         v
                +--------------------------+
                | transformation layer     |
                | sorting + enrichment     |
                +------------+-------------+
                             |
                             v
                +--------------------------+
                | anomaly detection        |
                | rule-based checks        |
                +------------+-------------+
                             |
                +------------+-------------+
                |                          |
                v                          v
    +--------------------------+   +----------------------+
    | cleaned_readings.csv     |   | detected_anomalies   |
    | analysis-ready dataset   |   | anomaly events       |
    +------------+-------------+   +-----------+----------+
                 |                             |
                 +-------------+---------------+
                               |
                               v
                    +----------------------+
                    | PostgreSQL           |
                    | raw / clean / rules  |
                    +----------------------+
```

## Pipeline flow

```text
Raw CSV
  -> schema validation
  -> quality checks
  -> rejected records
  -> cleaned records
  -> anomaly detection
  -> PostgreSQL tables + CSV exports
```

## Data quality checks

Implemented checks include:

- missing required columns
- invalid timestamps
- invalid numeric values
- duplicate rows
- unknown equipment ids
- invalid machine states
- equipment type mismatch
- clearly implausible values such as negative flow or pressure

Invalid rows are isolated in `rejected_records.csv` and optionally loaded into the `rejected_records` table.

## Detected anomalies

The anomaly layer uses simple, explainable business rules:

- `HIGH_ENERGY_WHILE_STOPPED`
- `TEMPERATURE_OUT_OF_RANGE`
- `PRESSURE_DROP_OR_SPIKE`
- `ENERGY_SPIKE`
- `MISSING_TIMESLOT`

The goal is to keep the core detection logic readable, deterministic, and easy to reason about.

## Experimental ML Anomalies

As a complement to the rule-based approach, the pipeline also runs an unsupervised Machine Learning model (`IsolationForest` from scikit-learn). 
This acts as an exploratory baseline to catch multidimensional anomalies that might slip past the hardcoded rules. The results are exported separately.

## Database model

The PostgreSQL schema contains:

- `equipment_reference`
- `raw_sensor_readings`
- `clean_sensor_readings`
- `detected_anomalies`
- `rejected_records`

The pipeline reloads demo data on each run so that the local setup stays deterministic.

## Quick start

### 1. Install Python dependencies

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 2. Optional environment file

```bash
cp .env.example .env
```

Both Docker Compose and the Python application read these variables. The project still provides sensible defaults, so this step is optional.

### 3. Start PostgreSQL with Docker Compose

```bash
docker-compose up -d
```

The database is exposed on `localhost:55432` by default with:

- database: `industrial_watch`
- user: `industrial_user`
- password: `industrial_pass`

### 4. Generate the sample dataset

```bash
.venv/bin/python -m src.main generate
```

### 5. Run the pipeline

```bash
.venv/bin/python -m src.main run
```

### 6. Or do both in one command

```bash
.venv/bin/python -m src.main all
```

## Run without PostgreSQL

If PostgreSQL is not available, the pipeline can still export cleaned records, rejected rows and detected anomalies as CSV files:

```bash
.venv/bin/python -m src.main all --skip-db
```

## Output files

Running the pipeline produces:

- `data/raw/sensor_readings.csv`
- `data/sample_output/cleaned_readings.csv`
- `data/sample_output/detected_anomalies.csv`
- `data/sample_output/ml_detected_anomalies.csv`
- `data/sample_output/rejected_records.csv`

## Useful commands

```bash
make install
make generate
make run
make run-no-db
make test
```

## Example SQL queries

Some ready-to-run queries are provided in [sql/queries.sql](/home/anisse/industrial/sql/queries.sql).

Examples include:

- average energy consumption per machine
- anomaly counts by type
- most unstable machines based on anomaly volume
- energy consumption aggregated by equipment type

## Technical choices

- `pandas` keeps the CSV processing simple and readable
- `SQLAlchemy` provides a clean PostgreSQL integration
- `pytest` covers the most important validation and anomaly rules
- `Docker Compose` makes local database setup reproducible

The project intentionally avoids heavier tooling such as Kafka, Spark or Airflow. For this scope, they would add more noise than value.

## Limits

- batch-oriented pipeline only
- simulated data instead of real telemetry
- ML anomaly detection is exploratory only and does not replace business rules
- no scheduler and no orchestration layer

## Possible extensions

- expose the pipeline through a small FastAPI endpoint
- add a dashboard layer for anomaly exploration
- add metrics export for observability
- schedule the pipeline with cron or CI
- introduce time-window aggregations or materialized views
