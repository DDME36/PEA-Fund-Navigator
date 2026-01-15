"""
Backtest ML Ensemble model
รันผ่าน: python scripts/backtest.py
"""

import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_fetcher import fetch_stock_data
from app.monthly_ml import MonthlyMLPredictor, create_monthly_data_for_ml
from app.config import TICKER


def main():
    print("\n" + "="*50)
    print("📈 Backtesting ML Ensemble")
    print("="*50)
    
    predictor = MonthlyMLPredictor()
    
    if not predictor.is_trained():
        print("❌ Model not trained. Run: python scripts/train.py")
        return
    
    df = fetch_stock_data(TICKER)
    monthly = create_monthly_data_for_ml(df)
    
    # Create features
    df_feat = predictor.create_features(monthly)
    features = predictor.feature_columns
    df_clean = df_feat.dropna(subset=features + ["Target"])
    
    # Split
    split = int(len(df_clean) * 0.7)
    test_df = df_clean.iloc[split:].copy()
    
    # Predict
    X_test = test_df[features]
    X_scaled = predictor.scaler.transform(X_test)
    
    predictions = predictor.model.predict(X_scaled)
    probabilities = predictor.model.predict_proba(X_scaled)
    
    test_df["Prediction"] = predictions
    test_df["Confidence"] = [prob[pred] for pred, prob in zip(predictions, probabilities)]
    
    # Allocation
    def get_alloc(row):
        if row["Prediction"] == 1:
            return 0.7 if row["Confidence"] >= 0.6 else 0.5
        else:
            return 0.2 if row["Confidence"] >= 0.6 else 0.4
    
    test_df["Allocation"] = test_df.apply(get_alloc, axis=1)
    test_df["Monthly_Return"] = test_df["Close"].pct_change()
    test_df["Strategy_Return"] = test_df["Allocation"].shift(1) * test_df["Monthly_Return"]
    test_df = test_df.dropna()
    
    # Metrics
    strat_ret = (1 + test_df["Strategy_Return"]).prod() - 1
    bh_ret = (1 + test_df["Monthly_Return"]).prod() - 1
    win_rate = sum(test_df["Prediction"] == test_df["Target"]) / len(test_df) * 100
    sharpe = test_df["Strategy_Return"].mean() / test_df["Strategy_Return"].std() * np.sqrt(12)
    cum = (1 + test_df["Strategy_Return"]).cumprod()
    max_dd = ((cum - cum.expanding().max()) / cum.expanding().max()).min() * 100
    
    print(f"\nPeriod: {test_df['Date'].iloc[0].strftime('%Y-%m')} to {test_df['Date'].iloc[-1].strftime('%Y-%m')}")
    print(f"Months: {len(test_df)}")
    
    print(f"\n📊 Returns:")
    print(f"   Strategy: {strat_ret*100:.2f}%")
    print(f"   Buy & Hold: {bh_ret*100:.2f}%")
    print(f"   Outperform: {(strat_ret-bh_ret)*100:.2f}%")
    
    print(f"\n📈 Metrics:")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Sharpe Ratio: {sharpe:.2f}")
    print(f"   Max Drawdown: {max_dd:.2f}%")
    print("="*50)


if __name__ == "__main__":
    main()
