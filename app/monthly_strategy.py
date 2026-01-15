"""
Monthly Strategy for Provident Fund
ทำนายรายเดือน - เหมาะกับกองทุนสำรองเลี้ยงชีพ
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple


def create_monthly_data(df: pd.DataFrame) -> pd.DataFrame:
    """Convert daily data to monthly with indicators."""
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
    
    # Monthly indicators
    monthly["RSI"] = calculate_rsi(monthly["Close"], 6)
    monthly["SMA_3"] = monthly["Close"].rolling(3).mean()
    monthly["SMA_6"] = monthly["Close"].rolling(6).mean()
    monthly["SMA_12"] = monthly["Close"].rolling(12).mean()
    
    # Returns
    monthly["Return_1m"] = monthly["Close"].pct_change(1) * 100
    monthly["Return_3m"] = monthly["Close"].pct_change(3) * 100
    monthly["Return_6m"] = monthly["Close"].pct_change(6) * 100
    
    # Volatility
    monthly["Volatility"] = monthly["Close"].pct_change().rolling(6).std() * np.sqrt(12) * 100
    
    # Drawdown
    monthly["Peak"] = monthly["Close"].expanding().max()
    monthly["Drawdown"] = (monthly["Close"] - monthly["Peak"]) / monthly["Peak"] * 100
    
    return monthly.reset_index()


def calculate_rsi(close: pd.Series, period: int = 6) -> pd.Series:
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_monthly_allocation(monthly: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate recommended allocation for next month.
    Returns (allocation 0-100, reasoning dict)
    """
    latest = monthly.iloc[-1]
    
    # Initialize scores
    signals = {}
    
    # 1. Trend Signal (Price vs SMA6)
    above_sma6 = latest["Close"] > latest["SMA_6"]
    signals["trend"] = {
        "name": "Trend (SMA6)",
        "value": "ขาขึ้น" if above_sma6 else "ขาลง",
        "bullish": above_sma6,
        "weight": 0.25
    }
    
    # 2. Momentum Signal (3-month return)
    mom_positive = latest["Return_3m"] > 0
    signals["momentum"] = {
        "name": "Momentum 3M",
        "value": f"{latest['Return_3m']:.1f}%",
        "bullish": mom_positive,
        "weight": 0.25
    }
    
    # 3. RSI Signal
    rsi = latest["RSI"]
    if rsi < 35:
        rsi_signal = "oversold"
        rsi_bullish = True
    elif rsi > 65:
        rsi_signal = "overbought"
        rsi_bullish = False
    else:
        rsi_signal = "neutral"
        rsi_bullish = None
    
    signals["rsi"] = {
        "name": "RSI",
        "value": f"{rsi:.0f} ({rsi_signal})",
        "bullish": rsi_bullish,
        "weight": 0.25
    }
    
    # 4. Volatility Signal
    vol = latest["Volatility"]
    vol_median = monthly["Volatility"].rolling(12).median().iloc[-1]
    low_vol = vol < vol_median * 1.2
    signals["volatility"] = {
        "name": "Volatility",
        "value": f"{vol:.1f}% ({'ต่ำ' if low_vol else 'สูง'})",
        "bullish": low_vol,
        "weight": 0.15
    }
    
    # 5. Drawdown Signal
    dd = latest["Drawdown"]
    safe_dd = dd > -15
    signals["drawdown"] = {
        "name": "Drawdown",
        "value": f"{dd:.1f}%",
        "bullish": safe_dd,
        "weight": 0.10
    }
    
    # Calculate weighted score
    score = 0
    for sig in signals.values():
        if sig["bullish"] is True:
            score += sig["weight"]
        elif sig["bullish"] is False:
            score -= sig["weight"] * 0.5  # Bearish signals have less weight
    
    # Convert score to allocation
    # Score range: roughly -0.5 to 1.0
    # Map to allocation: 0% to 100%
    allocation = max(0, min(100, int((score + 0.3) / 1.3 * 100)))
    
    # Round to nearest 10%
    allocation = round(allocation / 10) * 10
    
    return allocation, signals


def get_monthly_prediction(monthly: pd.DataFrame) -> Dict[str, Any]:
    """Get full monthly prediction with all details."""
    allocation, signals = get_monthly_allocation(monthly)
    latest = monthly.iloc[-1]
    
    # Determine weather
    if allocation >= 80:
        weather = "☀️ ฟ้าเปิด"
        action = f"สัญญาณดีมาก! แนะนำ PEA-E {allocation}%"
        prediction = "Bullish"
    elif allocation >= 60:
        weather = "⛅ ฟ้าครึ้ม"
        action = f"สัญญาณค่อนข้างดี แนะนำ PEA-E {allocation}%"
        prediction = "Bullish"
    elif allocation >= 40:
        weather = "🌥️ มีเมฆ"
        action = f"สัญญาณกลางๆ แนะนำ PEA-E {allocation}%"
        prediction = "Neutral"
    elif allocation >= 20:
        weather = "🌦️ ฝนปรอย"
        action = f"สัญญาณไม่ดี ลดหุ้นเหลือ PEA-E {allocation}%"
        prediction = "Bearish"
    else:
        weather = "🌧️ พายุเข้า"
        action = f"⚠️ อันตราย! หลบไป PEA-F เต็มที่"
        prediction = "Bearish"
    
    # Count bullish/bearish signals
    bullish_count = sum(1 for s in signals.values() if s["bullish"] is True)
    bearish_count = sum(1 for s in signals.values() if s["bullish"] is False)
    
    # Calculate confidence
    total_signals = bullish_count + bearish_count
    if total_signals > 0:
        confidence = max(bullish_count, bearish_count) / len(signals)
    else:
        confidence = 0.5
    
    return {
        "date": latest["Date"].strftime("%Y-%m"),
        "close": float(latest["Close"]),
        "allocation": allocation,
        "prediction": prediction,
        "weather": weather,
        "action": action,
        "confidence": round(confidence, 2),
        "signals": signals,
        "bullish_signals": bullish_count,
        "bearish_signals": bearish_count,
        "indicators": {
            "rsi": round(latest["RSI"], 1),
            "return_1m": round(latest["Return_1m"], 2),
            "return_3m": round(latest["Return_3m"], 2),
            "volatility": round(latest["Volatility"], 2),
            "drawdown": round(latest["Drawdown"], 2),
            "above_sma6": bool(latest["Close"] > latest["SMA_6"])
        }
    }


def backtest_monthly_strategy(monthly: pd.DataFrame) -> Dict[str, Any]:
    """Backtest the monthly strategy."""
    df = monthly.copy()
    
    # Calculate allocation for each month
    allocations = []
    for i in range(12, len(df)):  # Need 12 months history
        subset = df.iloc[:i+1]
        alloc, _ = get_monthly_allocation(subset)
        allocations.append(alloc / 100)
    
    # Pad beginning with 0.5
    allocations = [0.5] * 12 + allocations
    df["Allocation"] = allocations[:len(df)]
    
    df["Monthly_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Allocation"].shift(1) * df["Monthly_Return"]
    
    df = df.dropna()
    
    # Use last 50% for testing
    split = int(len(df) * 0.5)
    test = df.iloc[split:]
    
    # Metrics
    strat_ret = (1 + test["Strategy_Return"]).prod() - 1
    bh_ret = (1 + test["Monthly_Return"]).prod() - 1
    
    # Win rate
    correct = 0
    for i in range(1, len(test)):
        alloc = test["Allocation"].iloc[i-1]
        ret = test["Monthly_Return"].iloc[i]
        if (alloc > 0.5 and ret > 0) or (alloc <= 0.5 and ret <= 0):
            correct += 1
    win_rate = correct / (len(test) - 1) if len(test) > 1 else 0
    
    # Sharpe
    sharpe = test["Strategy_Return"].mean() / test["Strategy_Return"].std() * np.sqrt(12) if test["Strategy_Return"].std() > 0 else 0
    
    # Max Drawdown
    cum = (1 + test["Strategy_Return"]).cumprod()
    max_dd = ((cum - cum.expanding().max()) / cum.expanding().max()).min()
    
    return {
        "period": {
            "start": test["Date"].iloc[0].strftime("%Y-%m"),
            "end": test["Date"].iloc[-1].strftime("%Y-%m"),
            "total_months": len(test)
        },
        "returns": {
            "strategy_return_pct": round(strat_ret * 100, 2),
            "buy_hold_return_pct": round(bh_ret * 100, 2),
            "outperformance_pct": round((strat_ret - bh_ret) * 100, 2)
        },
        "metrics": {
            "win_rate_pct": round(win_rate * 100, 1),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(max_dd * 100, 2)
        }
    }
