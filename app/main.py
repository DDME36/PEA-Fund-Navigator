"""FastAPI application for Stock Market Prediction API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import numpy as np

from app.config import (
    TICKER,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    HIGH_CONFIDENCE_SAFE_ALLOCATION,
    MEDIUM_CONFIDENCE_SAFE_ALLOCATION,
    LOW_CONFIDENCE_ALLOCATION,
    DANGER_ALLOCATION,
    DANGER_THRESHOLD,
    LOOKAHEAD_DAYS
)
from app.data_fetcher import fetch_stock_data, fetch_latest_data, get_market_status, get_thai_time
from app.feature_engineering import add_technical_indicators, create_target_mean_reversion
from app.model import StockPredictor
from app.backtest import run_backtest
from app.strategy import get_strategy_signals, backtest_ensemble, calculate_allocation_from_signal
from app.monthly_strategy import create_monthly_data, get_monthly_prediction, backtest_monthly_strategy
from app.monthly_ml import MonthlyMLPredictor, create_monthly_data_for_ml
from app.schemas import (
    PredictionResponse,
    TrainResponse,
    BacktestResponse,
    HealthResponse,
    ErrorResponse
)

# Global instances
predictor: StockPredictor = None
monthly_predictor: MonthlyMLPredictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize models on startup."""
    global predictor, monthly_predictor
    predictor = StockPredictor()
    monthly_predictor = MonthlyMLPredictor()
    yield


app = FastAPI(
    title="AI Navigator - PEA PVD Optimization",
    description="ระบบ GPS นำทางอัจฉริยะสำหรับกองทุนสำรองเลี้ยงชีพ",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_allocation_reasoning(prediction: int, probability: float, allocation: int) -> str:
    """Generate human-readable allocation reasoning."""
    trend = "Bullish" if prediction == 1 else "Bearish"
    confidence = "high" if probability >= HIGH_CONFIDENCE_THRESHOLD else "medium" if probability >= MEDIUM_CONFIDENCE_THRESHOLD else "low"
    
    return f"{trend} prediction with {confidence} confidence ({probability:.1%}). Recommended {allocation}% equity allocation."


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status."""
    market = get_market_status()
    last_trained = None
    if monthly_predictor and monthly_predictor.last_trained:
        last_trained = monthly_predictor.last_trained
    
    return HealthResponse(
        status="healthy",
        model_loaded=monthly_predictor.is_trained() if monthly_predictor else False,
        ticker=TICKER,
        market_status=market,
        last_trained=last_trained
    )


@app.post("/train", response_model=TrainResponse, responses={500: {"model": ErrorResponse}})
async def train_model():
    """
    Train Monthly ML Model (XGBoost + RandomForest + GradientBoosting Ensemble)
    ใช้เวลานานกว่า rule-based เพราะต้อง train 3 models
    """
    try:
        # Fetch historical data
        df = fetch_stock_data(TICKER)
        monthly = create_monthly_data_for_ml(df)
        
        # Train ML model
        metrics = monthly_predictor.train(monthly)
        
        return TrainResponse(
            status="success",
            train_accuracy=metrics["train_accuracy"],
            test_accuracy=metrics["test_accuracy"],
            train_samples=metrics["train_samples"],
            test_samples=metrics["test_samples"],
            features_used=[f"{metrics['features_used']} features"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict", response_model=PredictionResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def predict():
    """
    ทำนายรายเดือนด้วย ML Ensemble
    แนะนำสัดส่วน PEA-E (หุ้น) vs PEA-F (ตราสารหนี้) รวมกัน = 100%
    """
    try:
        market = get_market_status()
        df = fetch_stock_data(TICKER)
        
        # Try ML prediction first
        if monthly_predictor.is_trained():
            monthly = create_monthly_data_for_ml(df)
            prediction, confidence, details = monthly_predictor.predict(monthly)
            
            # Calculate allocation (must sum to 100%)
            if prediction == 1:  # Bullish - favor equity
                if confidence >= 0.70:
                    pea_e = 100
                elif confidence >= 0.65:
                    pea_e = 80
                elif confidence >= 0.60:
                    pea_e = 70
                elif confidence >= 0.55:
                    pea_e = 60
                else:
                    pea_e = 50
            else:  # Bearish - favor bond
                if confidence >= 0.70:
                    pea_e = 0
                elif confidence >= 0.65:
                    pea_e = 20
                elif confidence >= 0.60:
                    pea_e = 30
                elif confidence >= 0.55:
                    pea_e = 40
                else:
                    pea_e = 50
            
            pea_f = 100 - pea_e
            
            # Determine weather based on equity allocation
            if pea_e >= 80:
                weather = "☀️ ฟ้าเปิด"
                action = f"สัญญาณดีมาก! ลุยหุ้นเต็มที่"
                pred_text = "Bullish"
            elif pea_e >= 60:
                weather = "⛅ ฟ้าครึ้ม"
                action = f"สัญญาณค่อนข้างดี เน้นหุ้น"
                pred_text = "Bullish"
            elif pea_e >= 40:
                weather = "🌥️ มีเมฆ"
                action = f"ไม่แน่ใจ แบ่งครึ่งๆ"
                pred_text = "Neutral"
            elif pea_e >= 20:
                weather = "🌦️ ฝนปรอย"
                action = f"สัญญาณไม่ดี เน้นตราสารหนี้"
                pred_text = "Bearish"
            else:
                weather = "🌧️ พายุเข้า"
                action = f"⚠️ อันตราย! หลบไปตราสารหนี้"
                pred_text = "Bearish"
            
            # Build reasoning
            ind = details["individual_models"]
            votes_up = sum(1 for m in ind.values() if m["prediction"] == 1)
            reasoning = f"ML Vote: {votes_up}/3 ทายขึ้น | ความมั่นใจ {confidence:.0%}"
            
            latest_date = monthly["Date"].iloc[-1].strftime("%Y-%m")
            
        else:
            # Fallback to rule-based
            monthly = create_monthly_data(df)
            pred = get_monthly_prediction(monthly)
            
            pea_e = pred["allocation"]
            pea_f = 100 - pea_e
            confidence = pred["confidence"]
            weather = pred["weather"]
            action = pred["action"]
            pred_text = pred["prediction"]
            reasoning = f"Rule-Based | {pred['bullish_signals']} สัญญาณซื้อ"
            latest_date = pred["date"]
        
        return PredictionResponse(
            ticker=TICKER,
            date=latest_date,
            prediction=pred_text,
            probability=round(confidence, 4),
            recommended_allocation=pea_e,  # PEA-E %
            allocation_reasoning=reasoning,
            weather=weather,
            action=f"{action} → PEA-E {pea_e}% | PEA-F {pea_f}%",
            market_status=market
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict/monthly")
async def predict_monthly_detail():
    """
    รายละเอียดการทำนายรายเดือนแบบเต็ม
    """
    try:
        df = fetch_stock_data(TICKER)
        monthly = create_monthly_data(df)
        pred = get_monthly_prediction(monthly)
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backtest", response_model=BacktestResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def backtest():
    """
    Backtest ML Monthly Strategy
    """
    try:
        if not monthly_predictor.is_trained():
            raise HTTPException(status_code=400, detail="Model not trained. Call /train first.")
        
        df = fetch_stock_data(TICKER)
        monthly = create_monthly_data_for_ml(df)
        
        # Create features
        df_feat = monthly_predictor.create_features(monthly)
        features = monthly_predictor.feature_columns
        
        df_clean = df_feat.dropna(subset=features + ["Target"])
        
        # Time-series split
        split = int(len(df_clean) * 0.7)
        test_df = df_clean.iloc[split:].copy()
        
        # Get predictions for test period
        X_test = test_df[features]
        X_scaled = monthly_predictor.scaler.transform(X_test)
        
        predictions = monthly_predictor.model.predict(X_scaled)
        probabilities = monthly_predictor.model.predict_proba(X_scaled)
        
        test_df["Prediction"] = predictions
        test_df["Confidence"] = [prob[pred] for pred, prob in zip(predictions, probabilities)]
        
        # Calculate allocation based on prediction
        def get_alloc(row):
            if row["Prediction"] == 1:
                if row["Confidence"] >= 0.7:
                    return 1.0
                elif row["Confidence"] >= 0.6:
                    return 0.7
                else:
                    return 0.5
            else:
                if row["Confidence"] >= 0.7:
                    return 0.0
                elif row["Confidence"] >= 0.6:
                    return 0.2
                else:
                    return 0.4
        
        test_df["Allocation"] = test_df.apply(get_alloc, axis=1)
        test_df["Monthly_Return"] = test_df["Close"].pct_change()
        test_df["Strategy_Return"] = test_df["Allocation"].shift(1) * test_df["Monthly_Return"]
        
        test_df = test_df.dropna()
        
        # Metrics
        strat_ret = (1 + test_df["Strategy_Return"]).prod() - 1
        bh_ret = (1 + test_df["Monthly_Return"]).prod() - 1
        
        # Win rate
        correct = 0
        for i in range(len(test_df)):
            pred = test_df["Prediction"].iloc[i]
            actual = test_df["Target"].iloc[i]
            if pred == actual:
                correct += 1
        win_rate = correct / len(test_df) if len(test_df) > 0 else 0
        
        # Sharpe
        sharpe = test_df["Strategy_Return"].mean() / test_df["Strategy_Return"].std() * np.sqrt(12) if test_df["Strategy_Return"].std() > 0 else 0
        
        # Max Drawdown
        cum = (1 + test_df["Strategy_Return"]).cumprod()
        max_dd = ((cum - cum.expanding().max()) / cum.expanding().max()).min()
        
        return BacktestResponse(
            period={
                "start": test_df["Date"].iloc[0].strftime("%Y-%m"),
                "end": test_df["Date"].iloc[-1].strftime("%Y-%m"),
                "total_days": len(test_df)
            },
            returns={
                "buy_hold_return_pct": round(bh_ret * 100, 2),
                "strategy_return_pct": round(strat_ret * 100, 2),
                "outperformance_pct": round((strat_ret - bh_ret) * 100, 2)
            },
            metrics={
                "win_rate_pct": round(win_rate * 100, 1),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_dd * 100, 2)
            },
            allocation_stats={
                "avg_equity_allocation_pct": round(test_df["Allocation"].mean() * 100, 1),
                "bullish_days": int((test_df["Prediction"] == 1).sum()),
                "bearish_days": int((test_df["Prediction"] == 0).sum())
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/indicators")
async def get_current_indicators():
    """Get current technical indicator values for TDEX.BK."""
    try:
        df = fetch_latest_data(TICKER, days=250)
        df = add_technical_indicators(df)
        
        latest = df.dropna().iloc[-1]
        
        return {
            "ticker": TICKER,
            "date": latest["Date"].strftime("%Y-%m-%d") if "Date" in df.columns else "N/A",
            "close": round(latest["Close"], 2),
            "indicators": {
                "RSI": round(latest["RSI"], 2),
                "MACD": round(latest["MACD"], 4),
                "MACD_Signal": round(latest["MACD_Signal"], 4),
                "SMA_50": round(latest["SMA_50"], 2),
                "SMA_200": round(latest["SMA_200"], 2),
                "BB_Upper": round(latest["BB_Upper"], 2),
                "BB_Middle": round(latest["BB_Middle"], 2),
                "BB_Lower": round(latest["BB_Lower"], 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
