"""
Train ML Ensemble model
รันผ่าน: python scripts/train.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_fetcher import fetch_stock_data
from app.monthly_ml import MonthlyMLPredictor, create_monthly_data_for_ml
from app.config import TICKER


def main():
    print("\n" + "="*50)
    print("🚀 Training ML Ensemble Model")
    print("="*50)
    print(f"Ticker: {TICKER}")
    
    print("\nFetching data...")
    df = fetch_stock_data(TICKER)
    monthly = create_monthly_data_for_ml(df)
    print(f"Monthly data: {len(monthly)} rows")
    
    print("\nTraining...")
    predictor = MonthlyMLPredictor()
    metrics = predictor.train(monthly)
    
    print("\n" + "="*50)
    print("✅ Training Complete!")
    print("="*50)
    print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"\nTop Features:")
    for feat, imp in metrics['top_features'][:5]:
        print(f"  {feat}: {imp:.4f}")


if __name__ == "__main__":
    main()
