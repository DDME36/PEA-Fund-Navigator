"""Module for fetching stock data from yfinance."""

import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime
import pytz

from app.config import TIMEZONE


def get_thai_time() -> datetime:
    """Get current time in Thailand timezone."""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)


def is_trading_day() -> bool:
    """Check if today is a trading day (Mon-Fri)."""
    thai_time = get_thai_time()
    # 0 = Monday, 6 = Sunday
    return thai_time.weekday() < 5


def get_market_status() -> dict:
    """Get current market status based on Thai time."""
    thai_time = get_thai_time()
    weekday = thai_time.weekday()
    hour = thai_time.hour
    
    is_weekend = weekday >= 5
    # SET opens 10:00-12:30, 14:30-16:30
    is_market_hours = (10 <= hour < 12) or (hour == 12 and thai_time.minute <= 30) or (14 <= hour < 16) or (hour == 16 and thai_time.minute <= 30)
    
    if is_weekend:
        status = "ปิดทำการ (วันหยุด)"
        next_update = "วันจันทร์"
    elif is_market_hours:
        status = "ตลาดเปิด"
        next_update = "อัพเดทหลังตลาดปิด"
    else:
        status = "ตลาดปิด"
        next_update = "พรุ่งนี้" if hour >= 17 else "10:00 น."
    
    return {
        "thai_time": thai_time.strftime("%d/%m/%Y %H:%M น."),
        "is_trading_day": not is_weekend,
        "is_market_hours": is_market_hours and not is_weekend,
        "status": status,
        "next_update": next_update
    }


def fetch_stock_data(ticker: str, period: str = "max") -> pd.DataFrame:
    """
    Fetch historical stock data from yfinance.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'TDEX.BK')
        period: Data period ('max', '5y', '1y', etc.)
    
    Returns:
        DataFrame with OHLCV data
    
    Raises:
        ValueError: If no data is returned
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data returned for ticker: {ticker}")
        
        df = df.reset_index()
        df.columns = [col if col != "Date" else "Date" for col in df.columns]
        
        # Ensure Date column is datetime
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")


def fetch_latest_data(ticker: str, days: int = 250) -> pd.DataFrame:
    """
    Fetch recent stock data for prediction.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to fetch (need enough for indicator calculation)
    
    Returns:
        DataFrame with recent OHLCV data
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=f"{days}d")
        
        if df.empty:
            raise ValueError(f"No recent data for ticker: {ticker}")
        
        df = df.reset_index()
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error fetching latest data: {str(e)}")
