"""
Daily Update Script
รันวันละครั้งตอนเปิดคอม เพื่อ:
1. ดึงข้อมูลล่าสุด
2. Train ML model (ถ้าจำเป็น)
3. สร้าง prediction
4. สร้าง backtest results
5. บันทึกเป็น JSON

Usage:
    python scripts/daily_update.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_fetcher import fetch_stock_data
from app.monthly_ml import MonthlyMLPredictor, create_monthly_data_for_ml
from app.config import settings

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent / "frontend" / "public" / "data"
OUTPUT_FILE = OUTPUT_DIR / "prediction.json"


def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def get_thai_time() -> str:
    """Get current time in Thai timezone"""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%Y-%m-%d %H:%M:%S")


def get_weather_and_action(prediction: int, confidence: float, allocation: int) -> tuple:
    """Get weather emoji and action text based on prediction."""
    if prediction == 1:  # Bullish
        if confidence >= 0.7:
            return "☀️ ฟ้าเปิด", f"สัญญาณดีมาก! แนะนำ PEA-E {allocation}%"
        elif confidence >= 0.6:
            return "⛅ ฟ้าครึ้ม", f"สัญญาณค่อนข้างดี แนะนำ PEA-E {allocation}%"
        else:
            return "🌥️ มีเมฆ", f"สัญญาณกลางๆ แนะนำ PEA-E {allocation}%"
    else:  # Bearish
        if confidence >= 0.7:
            return "🌧️ พายุเข้า", f"⚠️ อันตราย! หลบไป PEA-F เต็มที่"
        elif confidence >= 0.6:
            return "🌦️ ฝนปรอย", f"สัญญาณไม่ดี ลดหุ้นเหลือ PEA-E {allocation}%"
        else:
            return "🌥️ มีเมฆ", f"สัญญาณกลางๆ แนะนำ PEA-E {allocation}%"


def calculate_allocation(prediction: int, confidence: float) -> int:
    """
    Calculate recommended allocation based on prediction and confidence.
    ใช้ confidence โดยตรงเพื่อให้สัดส่วนละเอียดขึ้น
    """
    if prediction == 1:  # Bullish
        # confidence 0.5-1.0 → allocation 50-100%
        allocation = int(50 + (confidence - 0.5) * 100)
        return min(100, max(50, allocation))
    else:  # Bearish
        # confidence 0.5-1.0 → allocation 50-0%
        allocation = int(50 - (confidence - 0.5) * 100)
        return min(50, max(0, allocation))


def run_daily_update():
    """Run daily prediction update using ML Ensemble model"""
    print("=" * 50)
    print(f"🚀 Daily Update (ML Ensemble) - {get_thai_time()}")
    print("=" * 50)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Fetch data
        print("\n📊 Fetching market data...")
        df = fetch_stock_data(ticker=settings.TICKER, period="5y")
        print(f"   Got {len(df)} days of data")
        
        # Create monthly data for ML
        print("\n📅 Creating monthly data...")
        monthly_ml = create_monthly_data_for_ml(df)
        print(f"   Got {len(monthly_ml)} months of data")
        
        # Initialize ML predictor
        print("\n🤖 Initializing ML Ensemble...")
        predictor = MonthlyMLPredictor()
        
        # Train if model doesn't exist
        if not predictor.is_trained():
            print("\n🎯 Training ML model (first time)...")
            train_result = predictor.train(monthly_ml)
            print(f"   Train accuracy: {train_result['train_accuracy']:.2%}")
            print(f"   Test accuracy: {train_result['test_accuracy']:.2%}")
            print(f"   Precision: {train_result['precision']:.2%}")
            print(f"   Recall: {train_result['recall']:.2%}")
            print(f"   F1 Score: {train_result['f1_score']:.2%}")
        else:
            print(f"   Model loaded (trained: {predictor.last_trained})")
        
        # Get ML prediction
        print("\n🔮 Getting ML prediction...")
        ml_prediction, ml_confidence, ml_details = predictor.predict(monthly_ml)
        
        # Calculate allocation
        allocation = calculate_allocation(ml_prediction, ml_confidence)
        weather, action = get_weather_and_action(ml_prediction, ml_confidence, allocation)
        
        # Get ML features for display
        print("\n📈 Getting ML features...")
        ml_features = predictor.get_current_features(monthly_ml)
        top_features = predictor.get_top_features(5)
        
        # Get trend analysis
        print("\n📊 Analyzing trend...")
        trend_analysis = predictor.get_trend_analysis(monthly_ml)
        
        # Run ML backtest
        print("\n📊 Running ML backtest...")
        backtest_result = predictor.backtest(monthly_ml)
        
        # Prepare output
        latest_date = monthly_ml["Date"].iloc[-1].strftime("%Y-%m")
        
        output_data = {
            "updated_at": get_thai_time(),
            "updated_timestamp": datetime.now().isoformat(),
            "prediction": {
                "ticker": settings.TICKER,
                "date": latest_date,
                "prediction": "Bullish" if ml_prediction == 1 else "Bearish",
                "probability": ml_confidence,
                "recommended_allocation": allocation,
                "allocation_reasoning": action,
                "weather": weather,
                "action": action,
                "ml_details": ml_details,
                "ml_features": ml_features,
                "top_features": [{"name": name, "importance": round(imp, 4)} for name, imp in top_features],
                "trend": trend_analysis,
            },
            "backtest": {
                "period": backtest_result["period"],
                "returns": backtest_result["returns"],
                "metrics": backtest_result["metrics"],
                "history": backtest_result.get("history", []),
            },
            "model_info": {
                "type": "ML Ensemble (XGB + RF + GB)",
                "ticker": settings.TICKER,
                "last_trained": predictor.last_trained,
            }
        }
        
        # Save to JSON
        print(f"\n💾 Saving to {OUTPUT_FILE}...")
        output_data = convert_to_serializable(output_data)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 50)
        print("✅ Daily update completed!")
        print(f"   ML Prediction: {'Bullish' if ml_prediction == 1 else 'Bearish'} ({ml_confidence:.1%})")
        print(f"   Allocation: PEA-E {allocation}%")
        print(f"   Weather: {weather}")
        print(f"   Updated at: {get_thai_time()}")
        print("=" * 50)
        
        return output_data
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error state
        error_data = {
            "updated_at": get_thai_time(),
            "updated_timestamp": datetime.now().isoformat(),
            "error": str(e),
            "prediction": None,
            "backtest": None,
            "model_info": {
                "type": "ML Ensemble (XGB + RF + GB)",
                "ticker": settings.TICKER,
            }
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        return None


if __name__ == "__main__":
    run_daily_update()
