"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class MarketStatus(BaseModel):
    """Market status based on Thai time."""
    thai_time: str
    is_trading_day: bool
    is_market_hours: bool
    status: str
    next_update: str


class PredictionResponse(BaseModel):
    """Response model for /predict endpoint."""
    ticker: str
    date: str
    prediction: str  # "Bullish" or "Bearish"
    probability: float
    recommended_allocation: int  # 0-100%
    allocation_reasoning: str
    weather: str  # สภาพอากาศตลาด
    action: str   # สิ่งที่ควรทำ
    market_status: Optional[MarketStatus] = None


class TrainResponse(BaseModel):
    """Response model for /train endpoint."""
    status: str
    train_accuracy: float
    test_accuracy: float
    train_samples: int
    test_samples: int
    features_used: List[str]


class BacktestPeriod(BaseModel):
    """Backtest period details."""
    start: str
    end: str
    total_days: int


class BacktestReturns(BaseModel):
    """Backtest return metrics."""
    buy_hold_return_pct: float
    strategy_return_pct: float
    outperformance_pct: float


class BacktestMetrics(BaseModel):
    """Backtest performance metrics."""
    win_rate_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float


class AllocationStats(BaseModel):
    """Allocation statistics."""
    avg_equity_allocation_pct: float
    bullish_days: int
    bearish_days: int


class BacktestResponse(BaseModel):
    """Response model for /backtest endpoint."""
    period: BacktestPeriod
    returns: BacktestReturns
    metrics: BacktestMetrics
    allocation_stats: AllocationStats


class IndicatorsResponse(BaseModel):
    """Response model for /indicators endpoint."""
    ticker: str
    date: str
    close: float
    indicators: Dict[str, float]


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str
    model_loaded: bool
    ticker: str
    market_status: Optional[MarketStatus] = None
    last_trained: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
