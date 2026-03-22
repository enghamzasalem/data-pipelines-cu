#!/usr/bin/env python3
"""
Test script for the gold price prediction model
Loads the trained model and evaluates it on test data
"""

import argparse
import pandas as pd
import sys
import numpy as np
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_model(model_path):
    """Load the trained model"""
    try:
        model_info = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
        logger.info(f"Training date: {model_info.get('training_date', 'Unknown')}")
        logger.info(f"Training accuracy: {model_info.get('accuracy', 'Unknown'):.4f}")
        return model_info
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None


def load_test_data(data_path):
    """Load test data from training_data.csv"""
    try:
        train_file = os.path.join(data_path, "training_data.csv")
        if not os.path.exists(train_file):
            logger.error(f"Training data file not found: {train_file}")
            return None

        df = pd.read_csv(train_file)
        logger.info(f"Loaded {len(df)} records from {train_file}")

        # Use last 20% as test set (same split as training)
        test_size = int(len(df) * 0.2)
        test_df = df.iloc[-test_size:] if test_size > 0 else df

        logger.info(f"Using {len(test_df)} records for testing")
        return test_df
    except Exception as e:
        logger.error(f"Error loading test data: {str(e)}")
        return None


def test_model(model_info, test_df):
    """Test the model on test data"""
    if model_info is None or test_df is None:
        return False

    model = model_info["model"]

    # Prepare features and target
    feature_cols = ["sentiment_mean", "news_count"]
    X_test = test_df[feature_cols]
    y_test = test_df["target"]

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, output_dict=True)

    logger.info(f"\n{'='*50}")
    logger.info("MODEL TEST RESULTS")
    logger.info(f"{'='*50}")
    logger.info(f"Test Accuracy: {accuracy:.4f}")
    logger.info(f"\nConfusion Matrix:")
    logger.info(f"{conf_matrix}")
    logger.info(f"\nClassification Report:")
    logger.info(classification_report(y_test, y_pred))

    # Calculate baseline accuracy (always predict majority class)
    majority_class = y_test.mode()[0]
    baseline_accuracy = (y_test == majority_class).mean()
    logger.info(
        f"\nBaseline Accuracy (predict majority class): {baseline_accuracy:.4f}"
    )

    # Additional metrics
    logger.info(f"\nTest set size: {len(y_test)}")
    logger.info(f"Class distribution: {y_test.value_counts().to_dict()}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Test the gold price prediction model")
    parser.add_argument(
        "--model", type=str, required=True, help="Path to the trained model file (.pkl)"
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to the data directory containing training_data.csv",
    )

    args = parser.parse_args()

    # Load model and test data
    model_info = load_model(args.model)
    test_df = load_test_data(args.data)

    # Test model
    if test_model(model_info, test_df):
        logger.info("Model testing completed successfully")
    else:
        logger.error("Model testing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
