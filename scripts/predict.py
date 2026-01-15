"""
Quick prediction script
รันผ่าน: python scripts/predict.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_fetcher import fetch_stock_data
from app.monthly_ml import MonthlyMLPredictor, create_monthly_data_for_ml
from app.config import TICKER


def main():
    print("\n" + "="*50)
    print("🔮 PEA PVD Navigator - Prediction")
    print("="*50)
    
    predictor = MonthlyMLPredictor()
    
    if not predictor.is_trained():
        print("❌ Model not trained. Run: python scripts/train.py")
        return
    
    df = fetch_stock_data(TICKER)
    monthly = create_monthly_data_for_ml(df)
    
    prediction, confidence, details = predictor.predict(monthly)
    
    # Calculate allocation
    if prediction == 1:  # Bullish
        if confidence >= 0.70: pea_e = 100
        elif confidence >= 0.65: pea_e = 80
        elif confidence >= 0.60: pea_e = 70
        elif confidence >= 0.55: pea_e = 60
        else: pea_e = 50
    else:  # Bearish
        if confidence >= 0.70: pea_e = 0
        elif confidence >= 0.65: pea_e = 20
        elif confidence >= 0.60: pea_e = 30
        elif confidence >= 0.55: pea_e = 40
        else: pea_e = 50
    
    pea_f = 100 - pea_e
    
    # Weather
    if pea_e >= 80: weather = "☀️ ฟ้าเปิด"
    elif pea_e >= 60: weather = "⛅ ฟ้าครึ้ม"
    elif pea_e >= 40: weather = "🌥️ มีเมฆ"
    elif pea_e >= 20: weather = "🌦️ ฝนปรอย"
    else: weather = "🌧️ พายุเข้า"
    
    latest_date = monthly['Date'].iloc[-1].strftime('%Y-%m')
    
    print(f"\nTicker: {TICKER}")
    print(f"Date: {latest_date}")
    print(f"\nPrediction: {'📈 Bullish' if prediction == 1 else '📉 Bearish'}")
    print(f"Confidence: {confidence:.1%}")
    print(f"Weather: {weather}")
    
    # Individual models
    print(f"\nModel Votes:")
    for name, info in details["individual_models"].items():
        vote = "📈" if info["prediction"] == 1 else "📉"
        print(f"  {name.upper()}: {vote} ({info['confidence']:.1%})")
    
    print(f"\n💼 Recommended Allocation:")
    print(f"   PEA-E (หุ้น): {pea_e}%")
    print(f"   PEA-F (ตราสารหนี้): {pea_f}%")
    print("="*50)


if __name__ == "__main__":
    main()
