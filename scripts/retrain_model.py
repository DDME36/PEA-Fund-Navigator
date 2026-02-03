"""
Re-train ML Model
ใช้เมื่อต้องการ train โมเดลใหม่ด้วยข้อมูลล่าสุด
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_fetcher import fetch_stock_data
from app.improved_predictor import ImprovedPredictor
from app.monthly_ml import create_monthly_data_for_ml
from app.config import settings


def retrain_model():
    """Re-train the ML model with latest data"""
    print("=" * 60)
    print("Re-training ML Model")
    print("=" * 60)
    
    # Fetch latest data
    print("\n[1/3] Fetching latest data...")
    df = fetch_stock_data(ticker=settings.TICKER_SET, period="max")
    print(f"   Got {len(df)} days of data")
    
    # Create monthly data
    print("\n[2/3] Creating monthly data...")
    monthly = create_monthly_data_for_ml(df)
    print(f"   Got {len(monthly)} months of data")
    
    # Train model
    print("\n[3/3] Training Improved ML Predictor...")
    predictor = ImprovedPredictor()
    
    train_result = predictor.train(monthly)
    
    print("\n" + "=" * 60)
    print("Training Results:")
    print("=" * 60)
    print(f"Train Accuracy: {train_result['train_accuracy']:.2%}")
    print(f"Test Accuracy:  {train_result['test_accuracy']:.2%}")
    print(f"Precision:      {train_result['precision']:.2%}")
    print(f"Recall:         {train_result['recall']:.2%}")
    print(f"F1 Score:       {train_result['f1_score']:.2%}")
    print(f"\nTrain Samples:  {train_result['train_samples']}")
    print(f"Test Samples:   {train_result['test_samples']}")
    print(f"Features Used:  {train_result['features_used']}")
    
    print("\n" + "=" * 60)
    print("Top 10 Important Features:")
    print("=" * 60)
    for i, (name, importance) in enumerate(train_result['top_features'], 1):
        print(f"{i:2d}. {name:20s} {importance:.4f}")
    
    print("\n" + "=" * 60)
    print("Model saved successfully!")
    print("Run 'python scripts/daily_update.py' to generate new predictions")
    print("=" * 60)


if __name__ == "__main__":
    retrain_model()
