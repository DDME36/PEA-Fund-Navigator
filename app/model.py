"""Module for XGBoost model training and prediction."""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from app.config import FEATURE_COLUMNS, TARGET_COLUMN, TEST_SIZE, RANDOM_STATE


class StockPredictor:
    """XGBoost-based stock trend predictor optimized for Thai market."""
    
    def __init__(self, model_path: str = "models/xgb_model.joblib"):
        self.model_path = Path(model_path)
        self.scaler_path = Path("models/scaler.joblib")
        self.model: Optional[XGBClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns = FEATURE_COLUMNS
        self._load_model()
    
    def _load_model(self) -> None:
        """Load model and scaler from disk if exists."""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
        if self.scaler_path.exists():
            self.scaler = joblib.load(self.scaler_path)
    
    def _save_model(self) -> None:
        """Save model and scaler to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        if self.scaler:
            joblib.dump(self.scaler, self.scaler_path)
    
    def _get_available_features(self, df: pd.DataFrame) -> List[str]:
        """Get features that exist in the dataframe."""
        available = [col for col in self.feature_columns if col in df.columns]
        return available
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target from dataframe.
        """
        available_features = self._get_available_features(df)
        
        # Drop rows with NaN values
        required_cols = available_features + [TARGET_COLUMN]
        df_clean = df.dropna(subset=required_cols)
        
        X = df_clean[available_features]
        y = df_clean[TARGET_COLUMN]
        
        return X, y
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the XGBoost model using time-series split.
        Optimized for Thai sideways market.
        """
        available_features = self._get_available_features(df)
        X, y = self.prepare_data(df)
        
        # Time-series split (no shuffle)
        split_idx = int(len(X) * (1 - TEST_SIZE))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Calculate class weights (handle imbalanced data)
        class_counts = y_train.value_counts()
        total = len(y_train)
        scale_pos_weight = class_counts.get(0, 1) / class_counts.get(1, 1)
        
        # Initialize XGBoost with tuned parameters for Thai market
        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=4,  # Shallower to prevent overfitting
            learning_rate=0.05,  # Slower learning
            min_child_weight=5,  # More conservative
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,  # Regularization
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=1.0,  # L2 regularization
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE,
            use_label_encoder=False,
            eval_metric="logloss"
        )
        
        # Train with early stopping
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        test_proba = self.model.predict_proba(X_test_scaled)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        test_accuracy = accuracy_score(y_test, test_pred)
        
        # Additional metrics
        precision = precision_score(y_test, test_pred, zero_division=0)
        recall = recall_score(y_test, test_pred, zero_division=0)
        f1 = f1_score(y_test, test_pred, zero_division=0)
        
        # Feature importance
        feature_importance = dict(zip(available_features, self.model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Save model
        self._save_model()
        
        # Update feature columns to only available ones
        self.feature_columns = available_features
        
        return {
            "train_accuracy": round(train_accuracy, 4),
            "test_accuracy": round(test_accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": available_features,
            "top_features": top_features,
            "class_distribution": {
                "safe_days": int(y_test.sum()),
                "danger_days": int(len(y_test) - y_test.sum())
            }
        }
    
    def predict(self, df: pd.DataFrame) -> Tuple[int, float]:
        """
        Make prediction on latest data.
        
        Returns:
            Tuple of (prediction, probability)
            prediction: 1 = Safe to hold equity, 0 = Danger - reduce equity
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        available_features = self._get_available_features(df)
        
        # Get latest row with all features
        df_clean = df.dropna(subset=available_features)
        
        if df_clean.empty:
            raise ValueError("No valid data for prediction after dropping NaN values")
        
        latest = df_clean[available_features].iloc[-1:].copy()
        
        # Scale features
        if self.scaler:
            latest_scaled = self.scaler.transform(latest)
        else:
            latest_scaled = latest.values
        
        prediction = self.model.predict(latest_scaled)[0]
        probability = self.model.predict_proba(latest_scaled)[0]
        
        # Return probability of the predicted class
        confidence = probability[prediction]
        
        return int(prediction), float(confidence)
    
    def predict_with_details(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Make prediction with additional details for debugging.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        available_features = self._get_available_features(df)
        df_clean = df.dropna(subset=available_features)
        
        if df_clean.empty:
            raise ValueError("No valid data for prediction")
        
        latest = df_clean[available_features].iloc[-1:].copy()
        
        if self.scaler:
            latest_scaled = self.scaler.transform(latest)
        else:
            latest_scaled = latest.values
        
        prediction = self.model.predict(latest_scaled)[0]
        probability = self.model.predict_proba(latest_scaled)[0]
        
        # Get feature values for explanation
        feature_values = {col: float(latest[col].iloc[0]) for col in available_features}
        
        return {
            "prediction": int(prediction),
            "safe_probability": float(probability[1]),
            "danger_probability": float(probability[0]),
            "feature_values": feature_values
        }
    
    def is_trained(self) -> bool:
        """Check if model is trained and loaded."""
        return self.model is not None
