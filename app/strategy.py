"""
Multiple trading strategies for Thai sideways market.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from enum import Enum


class Signal(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


def strategy_sma_crossover(df: pd.DataFrame) -> pd.Series:
    """
    Classic SMA Crossover Strategy.
    - Buy when SMA20 > SMA50 (Golden Cross)
    - Sell when SMA20 < SMA50 (Death Cross)
    """
    signal = (df["SMA_20"] > df["SMA_50"]).astype(int)
    return signal


def strategy_rsi_mean_reversion(df: pd.DataFrame) -> pd.Series:
    """
    RSI Mean Reversion - good for sideways market.
    - Buy when RSI < 30 (oversold)
    - Sell when RSI > 70 (overbought)
    - Hold otherwise
    """
    signal = pd.Series(index=df.index, data=0)
    signal[df["RSI"] < 30] = 1  # Buy
    signal[df["RSI"] > 70] = -1  # Sell
    return signal


def strategy_bollinger_squeeze(df: pd.DataFrame) -> pd.Series:
    """
    🏆 BEST STRATEGY for Thai market
    Bollinger Band squeeze - adjust exposure based on volatility.
    
    Logic:
    - Tight bands (squeeze) = low volatility = reduce exposure (potential breakout coming)
    - Wide bands = high volatility = increase exposure (trend in progress)
    """
    bb_width_ma = df["BB_Width"].rolling(20).mean()
    
    alloc = pd.Series(index=df.index, data=0.5)  # Default 50%
    alloc[df["BB_Width"] < bb_width_ma * 0.8] = 0.3   # Squeeze = reduce to 30%
    alloc[df["BB_Width"] > bb_width_ma * 1.2] = 0.7   # Expansion = increase to 70%
    alloc[df["BB_Width"] > bb_width_ma * 1.5] = 1.0   # Strong expansion = full 100%
    
    return alloc


def strategy_best_combo(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Best combination strategy based on backtest results:
    1. Bollinger Squeeze (primary)
    2. Price > SMA50 (trend filter)
    3. RSI filter (avoid overbought)
    """
    # Base allocation from BB Squeeze
    bb_width_ma = df["BB_Width"].rolling(20).mean()
    alloc = pd.Series(index=df.index, data=0.5)
    alloc[df["BB_Width"] < bb_width_ma * 0.8] = 0.3
    alloc[df["BB_Width"] > bb_width_ma * 1.2] = 0.7
    alloc[df["BB_Width"] > bb_width_ma * 1.5] = 1.0
    
    # Trend filter: reduce if below SMA50
    below_sma50 = df["Close"] < df["SMA_50"]
    alloc[below_sma50] = alloc[below_sma50] * 0.5  # Halve allocation
    
    # RSI filter: reduce if overbought
    overbought = df["RSI"] > 70
    alloc[overbought] = alloc[overbought] * 0.5
    
    # Oversold boost
    oversold = df["RSI"] < 30
    alloc[oversold] = np.minimum(alloc[oversold] * 1.5, 1.0)
    
    # Calculate confidence based on signal alignment
    confidence = pd.Series(index=df.index, data=0.5)
    
    # High confidence when multiple signals align
    bullish_signals = (
        (df["Close"] > df["SMA_50"]).astype(int) +
        (df["RSI"] < 60).astype(int) +
        (df["MACD"] > df["MACD_Signal"]).astype(int) +
        (df["BB_Width"] > bb_width_ma).astype(int)
    )
    
    confidence = bullish_signals / 4  # 0 to 1
    
    return alloc, confidence


def strategy_macd_crossover(df: pd.DataFrame) -> pd.Series:
    """
    MACD Crossover Strategy.
    - Buy when MACD > Signal
    - Sell when MACD < Signal
    """
    signal = (df["MACD"] > df["MACD_Signal"]).astype(int)
    return signal


def strategy_momentum(df: pd.DataFrame) -> pd.Series:
    """
    Momentum Strategy - follow the trend.
    - Buy when short-term momentum is positive
    - Sell when short-term momentum is negative
    """
    signal = (df["Momentum_5"] > 0).astype(int)
    return signal


def strategy_volatility_filter(df: pd.DataFrame) -> pd.Series:
    """
    Volatility Filter - reduce exposure during high volatility.
    - Full exposure when volatility is low
    - Reduce exposure when volatility is high
    """
    # Use ATR_Pct as volatility measure
    vol_median = df["ATR_Pct"].rolling(50).median()
    
    signal = pd.Series(index=df.index, data=1)
    signal[df["ATR_Pct"] > vol_median * 1.5] = 0  # High volatility = reduce
    
    return signal


def strategy_trend_following(df: pd.DataFrame) -> pd.Series:
    """
    Trend Following with multiple timeframes.
    - Strong buy: Price > SMA20 > SMA50 > SMA200
    - Buy: Price > SMA50
    - Sell: Price < SMA50
    """
    signal = pd.Series(index=df.index, data=0)
    
    # Strong uptrend
    strong_up = (df["Close"] > df["SMA_20"]) & (df["SMA_20"] > df["SMA_50"]) & (df["SMA_50"] > df["SMA_200"])
    signal[strong_up] = 1
    
    # Moderate uptrend
    moderate_up = (df["Close"] > df["SMA_50"]) & ~strong_up
    signal[moderate_up] = 1
    
    # Downtrend
    down = df["Close"] < df["SMA_50"]
    signal[down] = -1
    
    return signal


def ensemble_strategy(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Ensemble of multiple strategies - vote system.
    Returns signal and confidence.
    """
    strategies = {
        "sma_cross": strategy_sma_crossover(df),
        "rsi_reversion": strategy_rsi_mean_reversion(df),
        "bb_bounce": strategy_bollinger_bounce(df),
        "macd": strategy_macd_crossover(df),
        "trend": strategy_trend_following(df),
    }
    
    # Convert all to same scale (-1, 0, 1)
    votes = pd.DataFrame(strategies)
    
    # Normalize SMA and MACD (they return 0/1, convert to -1/1)
    votes["sma_cross"] = votes["sma_cross"] * 2 - 1
    votes["macd"] = votes["macd"] * 2 - 1
    
    # Calculate average vote
    avg_vote = votes.mean(axis=1)
    
    # Signal: 1 if avg > 0.2, -1 if avg < -0.2, else 0
    signal = pd.Series(index=df.index, data=0)
    signal[avg_vote > 0.2] = 1
    signal[avg_vote < -0.2] = -1
    
    # Confidence: absolute value of average vote
    confidence = avg_vote.abs()
    
    return signal, confidence


def calculate_allocation_from_signal(signal: int, confidence: float) -> int:
    """
    Convert signal and confidence to allocation percentage.
    """
    if signal == 1:  # Buy signal
        if confidence > 0.6:
            return 100
        elif confidence > 0.4:
            return 70
        else:
            return 50
    elif signal == -1:  # Sell signal
        if confidence > 0.6:
            return 0
        elif confidence > 0.4:
            return 20
        else:
            return 30
    else:  # Hold
        return 50


def get_strategy_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get all strategy signals for the latest data point.
    """
    latest_idx = df.dropna().index[-1]
    
    signals = {
        "sma_crossover": int(strategy_sma_crossover(df).loc[latest_idx]),
        "rsi_reversion": int(strategy_rsi_mean_reversion(df).loc[latest_idx]),
        "bollinger_bounce": int(strategy_bollinger_bounce(df).loc[latest_idx]),
        "macd_crossover": int(strategy_macd_crossover(df).loc[latest_idx]),
        "trend_following": int(strategy_trend_following(df).loc[latest_idx]),
    }
    
    # Ensemble
    ensemble_sig, ensemble_conf = ensemble_strategy(df)
    
    return {
        "individual_signals": signals,
        "ensemble_signal": int(ensemble_sig.loc[latest_idx]),
        "ensemble_confidence": float(ensemble_conf.loc[latest_idx]),
    }


def backtest_strategy(df: pd.DataFrame, strategy_func) -> Dict[str, float]:
    """
    Backtest a single strategy.
    """
    df = df.copy()
    df["Signal"] = strategy_func(df)
    df["Daily_Return"] = df["Close"].pct_change()
    
    # Position: 1 if signal >= 0, 0 if signal < 0
    df["Position"] = (df["Signal"] >= 0).astype(int)
    
    # Strategy return
    df["Strategy_Return"] = df["Position"].shift(1) * df["Daily_Return"]
    
    df = df.dropna()
    
    # Metrics
    total_return = (1 + df["Strategy_Return"]).prod() - 1
    buy_hold_return = (1 + df["Daily_Return"]).prod() - 1
    
    # Win rate
    wins = ((df["Signal"].shift(1) >= 0) & (df["Daily_Return"] > 0)).sum()
    wins += ((df["Signal"].shift(1) < 0) & (df["Daily_Return"] <= 0)).sum()
    win_rate = wins / len(df)
    
    # Sharpe
    sharpe = df["Strategy_Return"].mean() / df["Strategy_Return"].std() * np.sqrt(252) if df["Strategy_Return"].std() > 0 else 0
    
    return {
        "total_return_pct": round(total_return * 100, 2),
        "buy_hold_pct": round(buy_hold_return * 100, 2),
        "outperformance_pct": round((total_return - buy_hold_return) * 100, 2),
        "win_rate_pct": round(win_rate * 100, 2),
        "sharpe_ratio": round(sharpe, 2)
    }


def backtest_best_strategy(df: pd.DataFrame) -> Dict[str, float]:
    """
    Backtest the best combo strategy (Bollinger Squeeze + filters).
    """
    df = df.copy()
    alloc, confidence = strategy_best_combo(df)
    df["Allocation"] = alloc
    df["Confidence"] = confidence
    df["Daily_Return"] = df["Close"].pct_change()
    
    # Strategy return
    df["Strategy_Return"] = df["Allocation"].shift(1) * df["Daily_Return"]
    
    df = df.dropna()
    
    # Use last 20% for out-of-sample
    split_idx = int(len(df) * 0.8)
    test_df = df.iloc[split_idx:]
    
    # Metrics
    total_return = (1 + test_df["Strategy_Return"]).prod() - 1
    buy_hold_return = (1 + test_df["Daily_Return"]).prod() - 1
    
    # Win rate
    correct = 0
    for i in range(1, len(test_df)):
        alloc_val = test_df["Allocation"].iloc[i-1]
        ret = test_df["Daily_Return"].iloc[i]
        if (alloc_val > 0.5 and ret > 0) or (alloc_val <= 0.5 and ret <= 0):
            correct += 1
    win_rate = correct / (len(test_df) - 1) if len(test_df) > 1 else 0
    
    # Sharpe
    sharpe = test_df["Strategy_Return"].mean() / test_df["Strategy_Return"].std() * np.sqrt(252) if test_df["Strategy_Return"].std() > 0 else 0
    
    # Max drawdown
    cumulative = (1 + test_df["Strategy_Return"]).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    return {
        "total_return_pct": round(total_return * 100, 2),
        "buy_hold_pct": round(buy_hold_return * 100, 2),
        "outperformance_pct": round((total_return - buy_hold_return) * 100, 2),
        "win_rate_pct": round(win_rate * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "avg_allocation_pct": round(test_df["Allocation"].mean() * 100, 2)
    }


def backtest_ensemble(df: pd.DataFrame) -> Dict[str, float]:
    """
    Backtest using the best strategy (Bollinger Squeeze combo).
    """
    return backtest_best_strategy(df)
