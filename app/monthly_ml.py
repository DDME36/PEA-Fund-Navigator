"""
Monthly ML Model for Provident Fund
ใช้ XGBoost + LightGBM + Random Forest ensemble
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from xgboost import XGBClassifier
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class MonthlyMLPredictor:
    """ML-based monthly predictor using ensemble of models."""
    
    def __init__(self, model_path: str = "models/monthly_ml.joblib"):
        self.model_path = Path(model_path)
        self.scaler_path = Path("models/monthly_scaler.joblib")
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.last_trained = None
        self._load_model()
    
    def _load_model(self):
        """Load saved model if exists."""
        if self.model_path.exists():
            saved = joblib.load(self.model_path)
            self.model = saved.get("model")
            self.feature_columns = saved.get("features", [])
            self.last_trained = saved.get("last_trained")
        if self.scaler_path.exists():
            self.scaler = joblib.load(self.scaler_path)
    
    def _save_model(self):
        """Save model to disk."""
        from datetime import datetime
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_trained = datetime.now().isoformat()
        joblib.dump({
            "model": self.model,
            "features": self.feature_columns,
            "last_trained": self.last_trained
        }, self.model_path)
        if self.scaler:
            joblib.dump(self.scaler, self.scaler_path)
    
    def create_features(self, monthly: pd.DataFrame) -> pd.DataFrame:
        """Create ML features from monthly data."""
        df = monthly.copy()
        
        # Price-based features
        df["Return_1m"] = df["Close"].pct_change(1)
        df["Return_2m"] = df["Close"].pct_change(2)
        df["Return_3m"] = df["Close"].pct_change(3)
        df["Return_6m"] = df["Close"].pct_change(6)
        df["Return_12m"] = df["Close"].pct_change(12)
        
        # Moving averages
        df["SMA_3"] = df["Close"].rolling(3).mean()
        df["SMA_6"] = df["Close"].rolling(6).mean()
        df["SMA_12"] = df["Close"].rolling(12).mean()
        
        # Price relative to MAs
        df["Price_SMA3_Ratio"] = df["Close"] / df["SMA_3"]
        df["Price_SMA6_Ratio"] = df["Close"] / df["SMA_6"]
        df["Price_SMA12_Ratio"] = df["Close"] / df["SMA_12"]
        
        # MA crossovers
        df["SMA3_SMA6_Ratio"] = df["SMA_3"] / df["SMA_6"]
        df["SMA6_SMA12_Ratio"] = df["SMA_6"] / df["SMA_12"]
        
        # Volatility
        df["Volatility_3m"] = df["Return_1m"].rolling(3).std()
        df["Volatility_6m"] = df["Return_1m"].rolling(6).std()
        df["Volatility_12m"] = df["Return_1m"].rolling(12).std()
        
        # RSI
        df["RSI_6"] = self._calculate_rsi(df["Close"], 6)
        df["RSI_12"] = self._calculate_rsi(df["Close"], 12)
        
        # Momentum indicators
        df["ROC_3"] = df["Close"].pct_change(3)
        df["ROC_6"] = df["Close"].pct_change(6)
        
        # Drawdown
        df["Peak"] = df["Close"].expanding().max()
        df["Drawdown"] = (df["Close"] - df["Peak"]) / df["Peak"]
        
        # High/Low range
        df["HL_Range"] = (df["High"] - df["Low"]) / df["Close"]
        df["HL_Range_3m"] = df["HL_Range"].rolling(3).mean()
        
        # Volume features (if available)
        if "Volume" in df.columns and df["Volume"].sum() > 0:
            df["Volume_SMA3"] = df["Volume"].rolling(3).mean()
            df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA3"]
        
        # Lagged returns (previous months)
        for lag in [1, 2, 3]:
            df[f"Return_Lag{lag}"] = df["Return_1m"].shift(lag)
        
        # Target: Next month positive return
        df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        
        return df
    
    def _calculate_rsi(self, close: pd.Series, period: int) -> pd.Series:
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature columns."""
        exclude = ["Date", "Open", "High", "Low", "Close", "Volume", "Target", "Peak"]
        return [col for col in df.columns if col not in exclude and not df[col].isna().all()]
    
    def train(self, monthly: pd.DataFrame) -> Dict[str, Any]:
        """Train the ensemble model."""
        print("Creating features...")
        df = self.create_features(monthly)
        
        # Get feature columns
        self.feature_columns = self.get_feature_columns(df)
        print(f"Features: {len(self.feature_columns)}")
        
        # Drop NaN
        df_clean = df.dropna(subset=self.feature_columns + ["Target"])
        print(f"Samples after cleaning: {len(df_clean)}")
        
        if len(df_clean) < 30:
            raise ValueError("Not enough data for training")
        
        X = df_clean[self.feature_columns]
        y = df_clean["Target"]
        
        # Time-series split (no shuffle!)
        split_idx = int(len(X) * 0.7)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create ensemble of models
        print("Training ensemble model...")
        
        # Model 1: XGBoost
        xgb = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss',
            verbosity=0
        )
        
        # Model 2: Random Forest
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        # Model 3: Gradient Boosting
        gb = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        # Voting ensemble
        self.model = VotingClassifier(
            estimators=[
                ('xgb', xgb),
                ('rf', rf),
                ('gb', gb)
            ],
            voting='soft'  # Use probabilities
        )
        
        print("Fitting ensemble...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        test_proba = self.model.predict_proba(X_test_scaled)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        precision = precision_score(y_test, test_pred, zero_division=0)
        recall = recall_score(y_test, test_pred, zero_division=0)
        f1 = f1_score(y_test, test_pred, zero_division=0)
        
        # Feature importance (from XGBoost)
        xgb_model = self.model.named_estimators_['xgb']
        importance = dict(zip(self.feature_columns, xgb_model.feature_importances_))
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Save model
        self._save_model()
        
        print("\n" + "="*50)
        print("Training Complete!")
        print("="*50)
        
        return {
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": len(self.feature_columns),
            "top_features": top_features
        }
    
    def predict(self, monthly: pd.DataFrame) -> Tuple[int, float, Dict]:
        """
        Predict next month direction.
        Returns: (prediction, confidence, details)
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        df = self.create_features(monthly)
        df_clean = df.dropna(subset=self.feature_columns)
        
        if df_clean.empty:
            raise ValueError("No valid data for prediction")
        
        # Get latest row
        latest = df_clean[self.feature_columns].iloc[-1:].copy()
        
        # Scale
        latest_scaled = self.scaler.transform(latest)
        
        # Predict
        prediction = self.model.predict(latest_scaled)[0]
        proba = self.model.predict_proba(latest_scaled)[0]
        
        confidence = float(proba[prediction])
        
        # Get individual model predictions
        individual_preds = {}
        for name, model in self.model.named_estimators_.items():
            pred = model.predict(latest_scaled)[0]
            prob = model.predict_proba(latest_scaled)[0]
            individual_preds[name] = {
                "prediction": int(pred),
                "confidence": float(prob[pred])
            }
        
        return int(prediction), confidence, {
            "individual_models": individual_preds,
            "ensemble_proba": {
                "down": float(proba[0]),
                "up": float(proba[1])
            }
        }
    
    def is_trained(self) -> bool:
        return self.model is not None
    
    def backtest(self, monthly: pd.DataFrame, initial_capital: float = 100000) -> Dict[str, Any]:
        """
        Backtest the ML model on historical data.
        Uses walk-forward approach: train on past data, predict next month.
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        df = self.create_features(monthly)
        df_clean = df.dropna(subset=self.feature_columns + ["Target"])
        
        if len(df_clean) < 30:
            raise ValueError("Not enough data for backtest")
        
        # Walk-forward backtest
        results = []
        capital = initial_capital
        position = 0  # 0 = bond, 1 = equity
        
        # Start from 70% of data (after training period)
        start_idx = int(len(df_clean) * 0.7)
        
        for i in range(start_idx, len(df_clean) - 1):
            current = df_clean.iloc[i]
            next_row = df_clean.iloc[i + 1]
            
            # Get features and predict
            X = df_clean[self.feature_columns].iloc[i:i+1]
            X_scaled = self.scaler.transform(X)
            
            prediction = self.model.predict(X_scaled)[0]
            proba = self.model.predict_proba(X_scaled)[0]
            confidence = float(proba[prediction])
            
            # Calculate allocation based on prediction
            if prediction == 1:  # Bullish
                if confidence >= 0.7:
                    allocation = 1.0
                elif confidence >= 0.6:
                    allocation = 0.7
                else:
                    allocation = 0.5
            else:  # Bearish
                if confidence >= 0.7:
                    allocation = 0.0
                elif confidence >= 0.6:
                    allocation = 0.3
                else:
                    allocation = 0.5
            
            # Calculate actual return
            actual_return = (next_row["Close"] - current["Close"]) / current["Close"]
            actual_direction = 1 if actual_return > 0 else 0
            
            # Portfolio return (equity * allocation + bond * (1-allocation))
            bond_return = 0.003  # ~3.6% annual bond return
            portfolio_return = actual_return * allocation + bond_return * (1 - allocation)
            
            capital *= (1 + portfolio_return)
            
            results.append({
                "date": current.name if hasattr(current, 'name') else i,
                "prediction": int(prediction),
                "actual": actual_direction,
                "confidence": confidence,
                "allocation": allocation,
                "actual_return": actual_return,
                "portfolio_return": portfolio_return,
                "capital": capital,
                "correct": prediction == actual_direction
            })
        
        # Calculate metrics
        results_df = pd.DataFrame(results)
        
        total_trades = len(results_df)
        correct_trades = results_df["correct"].sum()
        win_rate = correct_trades / total_trades if total_trades > 0 else 0
        
        # Returns
        total_return = (capital - initial_capital) / initial_capital * 100
        buy_hold_return = (df_clean["Close"].iloc[-1] - df_clean["Close"].iloc[start_idx]) / df_clean["Close"].iloc[start_idx] * 100
        
        # Sharpe ratio (annualized)
        monthly_returns = results_df["portfolio_return"]
        if len(monthly_returns) > 1 and monthly_returns.std() > 0:
            sharpe = (monthly_returns.mean() * 12) / (monthly_returns.std() * np.sqrt(12))
        else:
            sharpe = 0
        
        # Max drawdown
        cumulative = (1 + results_df["portfolio_return"]).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        # Volatility (annualized)
        volatility = monthly_returns.std() * np.sqrt(12) * 100
        
        # Get actual dates
        start_date = df_clean["Date"].iloc[start_idx] if "Date" in df_clean.columns else df_clean.index[start_idx]
        end_date = df_clean["Date"].iloc[-1] if "Date" in df_clean.columns else df_clean.index[-1]
        
        start_str = start_date.strftime("%Y-%m") if hasattr(start_date, 'strftime') else str(start_date)[:7]
        end_str = end_date.strftime("%Y-%m") if hasattr(end_date, 'strftime') else str(end_date)[:7]
        
        return {
            "period": {
                "start": start_str,
                "end": end_str,
                "months": total_trades
            },
            "returns": {
                "strategy_return_pct": round(total_return, 2),
                "buy_hold_return_pct": round(buy_hold_return, 2),
                "excess_return_pct": round(total_return - buy_hold_return, 2)
            },
            "metrics": {
                "win_rate_pct": round(win_rate * 100, 1),
                "total_trades": total_trades,
                "correct_trades": int(correct_trades),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "volatility_pct": round(volatility, 2)
            },
            "final_capital": round(capital, 2)
        }
    
    def get_top_features(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top N most important features from the model."""
        if self.model is None:
            return []
        
        try:
            xgb_model = self.model.named_estimators_['xgb']
            importance = dict(zip(self.feature_columns, xgb_model.feature_importances_))
            return sorted(importance.items(), key=lambda x: x[1], reverse=True)[:n]
        except:
            return []
    
    def get_current_features(self, monthly: pd.DataFrame) -> Dict[str, float]:
        """Get current feature values for display."""
        df = self.create_features(monthly)
        df_clean = df.dropna(subset=self.feature_columns)
        
        if df_clean.empty:
            return {}
        
        latest = df_clean.iloc[-1]
        
        # Return key features for display
        display_features = {
            "Return_1m": round(latest.get("Return_1m", 0) * 100, 2),
            "Return_3m": round(latest.get("Return_3m", 0) * 100, 2),
            "RSI_6": round(latest.get("RSI_6", 50), 1),
            "Price_SMA6_Ratio": round(latest.get("Price_SMA6_Ratio", 1) * 100 - 100, 2),
            "Volatility_3m": round(latest.get("Volatility_3m", 0) * 100, 2),
            "Drawdown": round(latest.get("Drawdown", 0) * 100, 2),
        }
        
        return display_features


def create_monthly_data_for_ml(df: pd.DataFrame) -> pd.DataFrame:
    """Convert daily data to monthly for ML."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    
    monthly = df.resample("ME").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()
    
    return monthly.reset_index()
