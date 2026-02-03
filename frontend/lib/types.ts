// API Response Types

export interface MarketStatus {
  thai_time: string;
  is_trading_day: boolean;
  is_market_hours: boolean;
  status: string;
  next_update: string;
}

export interface Signal {
  name: string;
  value: string;
  bullish: boolean | null;
  weight: number;
}

export interface MLFeatures {
  Return_1m: number;
  Return_3m: number;
  RSI_6: number;
  Price_SMA6_Ratio: number;
  Volatility_3m: number;
  Drawdown: number;
}

export interface IndividualModel {
  prediction: number;
  confidence: number;
}

export interface MLDetails {
  individual_models: Record<string, IndividualModel>;
  ensemble_proba: {
    down: number;
    up: number;
  };
}

export interface TopFeature {
  name: string;
  importance: number;
}

export interface TrendAnalysis {
  trend: string;
  trend_icon: string;
  trend_score: number;
  momentum: {
    "1m": number;
    "3m": number;
    "6m": number;
  };
  price_position: {
    vs_sma3: string;
    vs_sma6: string;
    vs_sma12: string;
  };
  comparison: {
    recommendation: string;
    reason: string;
    expected_equity: number;
    bond_return: number;
  };
}

export interface MultiFundAllocation {
  "PEA-F": number;
  "PEA-E": number;
  "PEA-G": number;
  "PEA-P": number;
}

export interface MultiFundData {
  default: MultiFundAllocation;
  conservative: MultiFundAllocation;
  moderate: MultiFundAllocation;
  aggressive: MultiFundAllocation;
  market_data: Record<string, any>;
}

export interface PredictionResponse {
  ticker: string;
  date: string;
  prediction: "Bullish" | "Bearish" | "Neutral";
  probability: number;
  recommended_allocation: number;  // PEA-E % (legacy)
  allocation_reasoning: string;
  weather: string;
  action: string;
  market_status?: MarketStatus;
  signals?: Record<string, Signal>;
  indicators?: {
    rsi: number;
    return_1m: number;
    return_3m: number;
    volatility: number;
    drawdown: number;
    above_sma6: boolean;
  };
  ml_features?: MLFeatures;
  ml_details?: MLDetails;
  top_features?: TopFeature[];
  trend?: TrendAnalysis;
  multi_fund?: MultiFundData;  // NEW: 4-fund allocations
}

export interface BacktestPeriod {
  start: string;
  end: string;
  months?: number;
  total_days?: number;
}

export interface BacktestReturns {
  buy_hold_return_pct: number;
  strategy_return_pct: number;
  outperformance_pct?: number;
  excess_return_pct?: number;
}

export interface BacktestMetrics {
  win_rate_pct: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
  total_trades?: number;
  correct_trades?: number;
  volatility_pct?: number;
}

export interface AllocationStats {
  avg_equity_allocation_pct: number;
  bullish_days: number;
  bearish_days: number;
}

export interface BacktestHistory {
  date: string;
  allocation: number;
  prediction: string;
  actual: string;
  correct: boolean;
  strategy_value: number;
  buyhold_value: number;
  bond_value: number;
}

export interface BacktestResponse {
  period: BacktestPeriod;
  returns: BacktestReturns;
  metrics: BacktestMetrics;
  allocation_stats?: AllocationStats;
  final_capital?: number;
  history?: BacktestHistory[];
}

export interface IndicatorsResponse {
  ticker: string;
  date: string;
  close: number;
  indicators: {
    RSI: number;
    MACD: number;
    MACD_Signal: number;
    SMA_50: number;
    SMA_200: number;
    BB_Upper: number;
    BB_Middle: number;
    BB_Lower: number;
  };
}

export interface TrainResponse {
  status: string;
  train_accuracy: number;
  test_accuracy: number;
  train_samples: number;
  test_samples: number;
  features_used: string[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  ticker: string;
  market_status?: MarketStatus;
  last_trained?: string;
}
