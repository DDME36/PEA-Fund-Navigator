"""Configuration settings for the Stock Market Prediction API."""

from dataclasses import dataclass

@dataclass
class Settings:
    # Main tickers for 4 funds
    TICKER_SET: str = "^SET.BK"  # PEA-E (Thai Equity)
    TICKER_SP500: str = "^GSPC"  # PEA-G (Global Equity)
    TICKER_REITS: list = None  # PEA-P (Property/REITs)
    
    # Legacy ticker (for backward compatibility)
    TICKER: str = "^SET.BK"
    TIMEZONE: str = "Asia/Bangkok"
    
    # Smoothing factor for allocation (0-1, higher = more stable)
    ALLOCATION_SMOOTHING: float = 0.7  # 70% old, 30% new
    
    # Risk profiles
    RISK_PROFILES: dict = None
    
    # Features optimized for Thai sideways market
    FEATURE_COLUMNS: tuple = (
        # RSI variants
        "RSI", "RSI_7", "RSI_Overbought", "RSI_Oversold", "RSI_Divergence",
        # MACD
        "MACD", "MACD_Signal", "MACD_Hist",
        # Moving averages & crossovers
        "SMA_20", "SMA_50", "SMA_200",
        "Price_vs_SMA20", "Price_vs_SMA50", "Price_vs_SMA200",
        "SMA_20_50_Cross", "SMA_50_200_Cross",
        # Bollinger Bands
        "BB_Upper", "BB_Lower", "BB_Middle", "BB_Position", "BB_Width",
        # Volatility - KEY for sideways market
        "ATR_Pct", "Volatility",
        # Momentum
        "Momentum_5", "Momentum_10", "Momentum_20",
        # Returns context
        "Return_5d", "Return_10d", "Return_20d",
        # Volume
        "Volume_Ratio",
    )
    
    TARGET_COLUMN: str = "Target"
    
    # Target settings for Thai market
    DANGER_THRESHOLD: float = -2.0
    LOOKAHEAD_DAYS: int = 5
    
    # Allocation thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.65
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.55
    
    # Allocation percentages
    HIGH_CONFIDENCE_SAFE_ALLOCATION: int = 100
    MEDIUM_CONFIDENCE_SAFE_ALLOCATION: int = 70
    LOW_CONFIDENCE_ALLOCATION: int = 30
    DANGER_ALLOCATION: int = 0
    
    # Legacy names
    HIGH_CONFIDENCE_BULLISH_ALLOCATION: int = 100
    MEDIUM_CONFIDENCE_BULLISH_ALLOCATION: int = 70
    
    # Model parameters
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42

settings = Settings()

# Initialize REITs list
settings.TICKER_REITS = ["LPF.BK", "WHART.BK", "FTREIT.BK"]

# Risk profiles (allocation ranges for each fund)
settings.RISK_PROFILES = {
    "conservative": {
        "name": "ปลอดภัย",
        "description": "เน้นความมั่นคง รักษาเงินต้น",
        "ranges": {
            "PEA-F": (40, 60),  # Bond 40-60%
            "PEA-E": (0, 20),   # Thai Equity 0-20%
            "PEA-G": (0, 20),   # Global Equity 0-20%
            "PEA-P": (20, 40),  # REITs 20-40%
        }
    },
    "moderate": {
        "name": "ปกติ",
        "description": "สมดุลระหว่างความเสี่ยงและผลตอบแทน",
        "ranges": {
            "PEA-F": (20, 40),  # Bond 20-40%
            "PEA-E": (20, 40),  # Thai Equity 20-40%
            "PEA-G": (20, 40),  # Global Equity 20-40%
            "PEA-P": (10, 20),  # REITs 10-20%
        }
    },
    "aggressive": {
        "name": "ดุดัน",
        "description": "เน้นผลตอบแทนสูง ยอมรับความเสี่ยง",
        "ranges": {
            "PEA-F": (0, 20),   # Bond 0-20%
            "PEA-E": (30, 50),  # Thai Equity 30-50%
            "PEA-G": (30, 50),  # Global Equity 30-50%
            "PEA-P": (0, 20),   # REITs 0-20%
        }
    }
}

# Legacy exports
TICKER = settings.TICKER
FEATURE_COLUMNS = list(settings.FEATURE_COLUMNS)
TARGET_COLUMN = settings.TARGET_COLUMN
TIMEZONE = settings.TIMEZONE
DANGER_THRESHOLD = settings.DANGER_THRESHOLD
LOOKAHEAD_DAYS = settings.LOOKAHEAD_DAYS
HIGH_CONFIDENCE_THRESHOLD = settings.HIGH_CONFIDENCE_THRESHOLD
MEDIUM_CONFIDENCE_THRESHOLD = settings.MEDIUM_CONFIDENCE_THRESHOLD
HIGH_CONFIDENCE_SAFE_ALLOCATION = settings.HIGH_CONFIDENCE_SAFE_ALLOCATION
MEDIUM_CONFIDENCE_SAFE_ALLOCATION = settings.MEDIUM_CONFIDENCE_SAFE_ALLOCATION
LOW_CONFIDENCE_ALLOCATION = settings.LOW_CONFIDENCE_ALLOCATION
DANGER_ALLOCATION = settings.DANGER_ALLOCATION
HIGH_CONFIDENCE_BULLISH_ALLOCATION = settings.HIGH_CONFIDENCE_BULLISH_ALLOCATION
MEDIUM_CONFIDENCE_BULLISH_ALLOCATION = settings.MEDIUM_CONFIDENCE_BULLISH_ALLOCATION
TEST_SIZE = settings.TEST_SIZE
RANDOM_STATE = settings.RANDOM_STATE
