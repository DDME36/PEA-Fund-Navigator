"""Module for backtesting the prediction strategy."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

from app.config import (
    FEATURE_COLUMNS, 
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    HIGH_CONFIDENCE_SAFE_ALLOCATION,
    MEDIUM_CONFIDENCE_SAFE_ALLOCATION,
    LOW_CONFIDENCE_ALLOCATION,
    DANGER_ALLOCATION
)


def calculate_allocation(prediction: int, probability: float) -> int:
    """
    Calculate equity allocation based on prediction and confidence.
    
    prediction: 1 = Safe, 0 = Danger
    """
    if prediction == 1:  # Safe
        if probability >= HIGH_CONFIDENCE_THRESHOLD:
            return HIGH_CONFIDENCE_SAFE_ALLOCATION
        elif probability >= MEDIUM_CONFIDENCE_THRESHOLD:
            return MEDIUM_CONFIDENCE_SAFE_ALLOCATION
        else:
            return LOW_CONFIDENCE_ALLOCATION
    else:  # Danger
        return DANGER_ALLOCATION


def run_backtest(
    df: pd.DataFrame, 
    model: XGBClassifier,
    scaler: Optional[StandardScaler] = None,
    feature_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run backtest comparing strategy vs buy-and-hold.
    """
    if feature_columns is None:
        feature_columns = FEATURE_COLUMNS
    
    # Get available features
    available_features = [col for col in feature_columns if col in df.columns]
    
    # Prepare data
    df_clean = df.dropna(subset=available_features).copy()
    
    if len(df_clean) < 50:
        raise ValueError("Not enough data for backtesting")
    
    # Use last 20% for backtesting (out-of-sample)
    split_idx = int(len(df_clean) * 0.8)
    backtest_df = df_clean.iloc[split_idx:].copy()
    
    # Get predictions and probabilities
    X_backtest = backtest_df[available_features]
    
    if scaler:
        X_scaled = scaler.transform(X_backtest)
    else:
        X_scaled = X_backtest.values
    
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    # Calculate daily returns
    backtest_df = backtest_df.reset_index(drop=True)
    backtest_df["Daily_Return"] = backtest_df["Close"].pct_change()
    backtest_df["Prediction"] = predictions
    
    # Get probability of predicted class for each row
    backtest_df["Probability"] = [float(prob[int(pred)]) for pred, prob in zip(predictions, probabilities)]
    
    # Calculate allocations - use scalar values
    allocations = []
    for i in range(len(predictions)):
        pred = int(predictions[i])
        prob = float(probabilities[i][pred])
        allocations.append(calculate_allocation(pred, prob) / 100)
    backtest_df["Allocation"] = allocations
    
    # Strategy returns (allocation * equity return, rest in fixed income ~0%)
    backtest_df["Strategy_Return"] = backtest_df["Allocation"].shift(1) * backtest_df["Daily_Return"]
    
    # Remove first row (NaN from pct_change)
    backtest_df = backtest_df.dropna()
    
    # Calculate cumulative returns
    backtest_df["Cumulative_BuyHold"] = (1 + backtest_df["Daily_Return"]).cumprod()
    backtest_df["Cumulative_Strategy"] = (1 + backtest_df["Strategy_Return"]).cumprod()
    
    # Calculate metrics
    total_days = len(backtest_df)
    buy_hold_return = (backtest_df["Cumulative_BuyHold"].iloc[-1] - 1) * 100
    strategy_return = (backtest_df["Cumulative_Strategy"].iloc[-1] - 1) * 100
    
    # Win rate - count days where prediction helped
    pred_array = backtest_df["Prediction"].values
    return_array = backtest_df["Daily_Return"].values
    
    correct_predictions = 0
    for i in range(len(pred_array)):
        # Safe prediction (1) and market went up = correct
        # Danger prediction (0) and market went down = correct (we avoided loss)
        if (pred_array[i] == 1 and return_array[i] > 0) or (pred_array[i] == 0 and return_array[i] <= 0):
            correct_predictions += 1
    
    win_rate = correct_predictions / total_days * 100
    
    # Sharpe ratio (annualized, assuming 252 trading days)
    strategy_std = backtest_df["Strategy_Return"].std()
    strategy_mean = backtest_df["Strategy_Return"].mean()
    sharpe_ratio = (strategy_mean / strategy_std) * np.sqrt(252) if strategy_std > 0 else 0
    
    # Max drawdown
    cumulative = backtest_df["Cumulative_Strategy"]
    rolling_max = cumulative.expanding().max()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    # Count safe vs danger predictions
    safe_days = int((backtest_df["Prediction"] == 1).sum())
    danger_days = int((backtest_df["Prediction"] == 0).sum())
    
    return {
        "period": {
            "start": backtest_df["Date"].iloc[0].strftime("%Y-%m-%d") if "Date" in backtest_df.columns else "N/A",
            "end": backtest_df["Date"].iloc[-1].strftime("%Y-%m-%d") if "Date" in backtest_df.columns else "N/A",
            "total_days": total_days
        },
        "returns": {
            "buy_hold_return_pct": round(float(buy_hold_return), 2),
            "strategy_return_pct": round(float(strategy_return), 2),
            "outperformance_pct": round(float(strategy_return - buy_hold_return), 2)
        },
        "metrics": {
            "win_rate_pct": round(float(win_rate), 2),
            "sharpe_ratio": round(float(sharpe_ratio), 2),
            "max_drawdown_pct": round(float(max_drawdown), 2)
        },
        "allocation_stats": {
            "avg_equity_allocation_pct": round(float(backtest_df["Allocation"].mean() * 100), 2),
            "bullish_days": safe_days,  # Safe days
            "bearish_days": danger_days  # Danger days
        }
    }
