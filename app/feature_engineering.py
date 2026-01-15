"""Module for calculating technical indicators and feature engineering."""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD, Signal line, and Histogram."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist


def calculate_sma(close: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return close.rolling(window=period).mean()


def calculate_ema(close: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return close.ewm(span=period, adjust=False).mean()


def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range - measures volatility."""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def calculate_volatility(close: pd.Series, period: int = 20) -> pd.Series:
    """Calculate rolling volatility (standard deviation of returns)."""
    returns = close.pct_change()
    return returns.rolling(window=period).std() * np.sqrt(252) * 100  # Annualized %


def calculate_momentum(close: pd.Series, period: int = 10) -> pd.Series:
    """Calculate price momentum."""
    return close.pct_change(periods=period) * 100


def calculate_rsi_divergence(close: pd.Series, rsi: pd.Series, period: int = 14) -> pd.Series:
    """
    Detect RSI divergence - useful for sideways market.
    Positive = bullish divergence (price down, RSI up)
    Negative = bearish divergence (price up, RSI down)
    """
    price_change = close.pct_change(periods=period)
    rsi_change = rsi.diff(periods=period)
    
    # Normalize
    divergence = (rsi_change / 100) - price_change
    return divergence


def calculate_bb_position(close: pd.Series, bb_upper: pd.Series, bb_lower: pd.Series) -> pd.Series:
    """Calculate where price is within Bollinger Bands (0-1 scale)."""
    return (close - bb_lower) / (bb_upper - bb_lower)


def calculate_volume_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculate volume relative to moving average."""
    vol_ma = volume.rolling(window=period).mean()
    return volume / vol_ma


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to the dataframe.
    Optimized for Thai market (sideways, range-bound).
    """
    df = df.copy()
    
    # Basic indicators
    df["RSI"] = calculate_rsi(df["Close"])
    df["RSI_7"] = calculate_rsi(df["Close"], period=7)  # Short-term RSI
    
    # MACD
    df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = calculate_macd(df["Close"])
    
    # Moving Averages
    df["SMA_20"] = calculate_sma(df["Close"], 20)
    df["SMA_50"] = calculate_sma(df["Close"], 50)
    df["SMA_200"] = calculate_sma(df["Close"], 200)
    df["EMA_12"] = calculate_ema(df["Close"], 12)
    df["EMA_26"] = calculate_ema(df["Close"], 26)
    
    # Bollinger Bands
    df["BB_Upper"], df["BB_Middle"], df["BB_Lower"] = calculate_bollinger_bands(df["Close"])
    df["BB_Position"] = calculate_bb_position(df["Close"], df["BB_Upper"], df["BB_Lower"])
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Middle"] * 100  # Band width %
    
    # Volatility indicators - IMPORTANT for sideways market
    df["ATR"] = calculate_atr(df["High"], df["Low"], df["Close"])
    df["ATR_Pct"] = df["ATR"] / df["Close"] * 100  # ATR as % of price
    df["Volatility"] = calculate_volatility(df["Close"])
    
    # Momentum
    df["Momentum_5"] = calculate_momentum(df["Close"], 5)
    df["Momentum_10"] = calculate_momentum(df["Close"], 10)
    df["Momentum_20"] = calculate_momentum(df["Close"], 20)
    
    # RSI Divergence - good for catching reversals in sideways market
    df["RSI_Divergence"] = calculate_rsi_divergence(df["Close"], df["RSI"])
    
    # Volume analysis
    if "Volume" in df.columns:
        df["Volume_Ratio"] = calculate_volume_ratio(df["Volume"])
        df["Volume_MA20"] = calculate_sma(df["Volume"], 20)
    
    # Price relative to MAs (trend strength)
    df["Price_vs_SMA20"] = (df["Close"] - df["SMA_20"]) / df["SMA_20"] * 100
    df["Price_vs_SMA50"] = (df["Close"] - df["SMA_50"]) / df["SMA_50"] * 100
    df["Price_vs_SMA200"] = (df["Close"] - df["SMA_200"]) / df["SMA_200"] * 100
    
    # SMA crossover signals
    df["SMA_20_50_Cross"] = (df["SMA_20"] > df["SMA_50"]).astype(int)
    df["SMA_50_200_Cross"] = (df["SMA_50"] > df["SMA_200"]).astype(int)
    
    # Overbought/Oversold zones
    df["RSI_Overbought"] = (df["RSI"] > 70).astype(int)
    df["RSI_Oversold"] = (df["RSI"] < 30).astype(int)
    
    # Weekly returns (for context)
    df["Return_5d"] = df["Close"].pct_change(periods=5) * 100
    df["Return_10d"] = df["Close"].pct_change(periods=10) * 100
    df["Return_20d"] = df["Close"].pct_change(periods=20) * 100
    
    return df


def create_target(df: pd.DataFrame, threshold: float = -2.0, lookahead: int = 5) -> pd.DataFrame:
    """
    Create target for Thai market strategy:
    Instead of predicting up/down, predict if we should AVOID (defensive mode).
    
    Target = 1: Safe to hold equity (no big drop coming)
    Target = 0: Danger - should reduce equity (big drop coming)
    
    Args:
        df: DataFrame with Close prices
        threshold: % drop that triggers "danger" signal (default -2%)
        lookahead: Days to look ahead (default 5 = 1 week)
    """
    df = df.copy()
    
    # Calculate max drawdown in next N days
    future_returns = []
    for i in range(len(df)):
        if i + lookahead < len(df):
            future_prices = df["Close"].iloc[i+1:i+lookahead+1]
            current_price = df["Close"].iloc[i]
            min_future = future_prices.min()
            max_drop = (min_future - current_price) / current_price * 100
            future_returns.append(max_drop)
        else:
            future_returns.append(np.nan)
    
    df["Future_MaxDrop"] = future_returns
    
    # Target: 1 = Safe (no big drop), 0 = Danger (big drop coming)
    df["Target"] = (df["Future_MaxDrop"] > threshold).astype(int)
    
    return df


def create_target_weekly_return(df: pd.DataFrame, positive_threshold: float = 0.5) -> pd.DataFrame:
    """
    Target based on weekly return - better for sideways market.
    
    Target = 1: Next week return > threshold (worth holding)
    Target = 0: Next week return <= threshold (not worth the risk)
    """
    df = df.copy()
    
    # Calculate 5-day forward return
    df["Future_Return_5d"] = df["Close"].shift(-5) / df["Close"] - 1
    df["Future_Return_5d"] = df["Future_Return_5d"] * 100  # Convert to %
    
    # Target: 1 if next week return > threshold
    df["Target"] = (df["Future_Return_5d"] > positive_threshold).astype(int)
    
    return df


def create_target_mean_reversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mean reversion target - BEST for Thai sideways market.
    
    Logic: 
    - When price is LOW relative to recent range → likely to go UP → hold equity
    - When price is HIGH relative to recent range → likely to go DOWN → reduce equity
    
    Uses BB_Position and RSI to determine if we're at extreme
    """
    df = df.copy()
    
    # Calculate 5-day forward return
    df["Future_Return_5d"] = (df["Close"].shift(-5) / df["Close"] - 1) * 100
    
    # Target based on whether holding equity would be profitable
    # 1 = Hold equity (expect positive return)
    # 0 = Reduce equity (expect negative or flat return)
    df["Target"] = (df["Future_Return_5d"] > 0).astype(int)
    
    return df


def create_target_simple(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple target: Next day price > Current day.
    Kept for backward compatibility.
    """
    df = df.copy()
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    return df
