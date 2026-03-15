from __future__ import annotations

import logging

import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


def train_and_detect_anomalies(df: pd.DataFrame, contamination: float = 0.01) -> pd.DataFrame:
    """
    Experimental ML anomaly detection using Isolation Forest.
    This acts as a baseline to complement rule-based anomalies.
    """
    logger.info("Starting ML anomaly detection (Isolation Forest)")
    
    if df.empty:
        logger.warning("Empty dataframe provided to ML anomaly detection")
        return pd.DataFrame()

    # Select numerical features that make sense for anomaly detection
    features = ["energy_kwh", "temperature_c", "pressure_bar", "flow_m3_h"]
    
    # Ensure columns exist in the dataframe
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        logger.warning("Missing columns for ML detection: %s", missing_cols)
        return pd.DataFrame()

    # Drop rows with NaN in features for the ML model
    ml_df = df.dropna(subset=features).copy()
    
    if len(ml_df) < 50:
        logger.warning("Not enough data to train Isolation Forest (rows=%s)", len(ml_df))
        return pd.DataFrame()

    X = ml_df[features]

    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    
    # Predict anomalies: -1 is anomaly, 1 is normal
    ml_df["ml_prediction"] = model.fit_predict(X)
    ml_df["ml_anomaly_score"] = model.decision_function(X)
    
    # Filter only the detected anomalies
    anomalies = ml_df[ml_df["ml_prediction"] == -1].copy()
    anomalies.drop(columns=["ml_prediction"], inplace=True)
    
    logger.info("ML model detected %s anomalies", len(anomalies))
    return anomalies
