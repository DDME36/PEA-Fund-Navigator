"""
Analyze Backtest Results
วิเคราะห์ว่าทำไม Win Rate สูงแต่ Return ติดลบ
"""

import json
import pandas as pd

# Load data
with open("frontend/public/data/prediction.json", "r", encoding="utf-8") as f:
    data = json.load(f)

history = data["backtest"]["history"]
df = pd.DataFrame(history)

print("=" * 60)
print("Backtest Analysis - Why High Win Rate but Negative Return?")
print("=" * 60)

# Basic stats
print(f"\nTotal months: {len(df)}")
print(f"Correct predictions: {df['correct'].sum()} / {len(df)} = {df['correct'].mean()*100:.1f}%")
print(f"Final value: {df['strategy_value'].iloc[-1]:.2f} (Start: 100)")
print(f"Return: {(df['strategy_value'].iloc[-1] - 100):.2f}%")

# Calculate actual returns
df['actual_return_pct'] = (df['buyhold_value'] / df['buyhold_value'].shift(1) - 1) * 100
df['actual_return_pct'] = df['actual_return_pct'].fillna(0)

# Analyze correct vs incorrect predictions
print("\n" + "=" * 60)
print("Correct Predictions Analysis")
print("=" * 60)

correct_df = df[df['correct'] == True].copy()
incorrect_df = df[df['correct'] == False].copy()

print(f"\nCorrect predictions ({len(correct_df)} months):")
print(f"  Avg allocation: {correct_df['allocation'].mean():.1f}%")
print(f"  Avg actual return: {correct_df['actual_return_pct'].mean():.2f}%")
print(f"  Total impact: {correct_df['actual_return_pct'].sum():.2f}%")

print(f"\nIncorrect predictions ({len(incorrect_df)} months):")
print(f"  Avg allocation: {incorrect_df['allocation'].mean():.1f}%")
print(f"  Avg actual return: {incorrect_df['actual_return_pct'].mean():.2f}%")
print(f"  Total impact: {incorrect_df['actual_return_pct'].sum():.2f}%")

# Analyze by prediction type
print("\n" + "=" * 60)
print("Prediction Type Analysis")
print("=" * 60)

bullish = df[df['prediction'] == 'ขึ้น'].copy()
bearish = df[df['prediction'] == 'ลง'].copy()

print(f"\nBullish predictions ({len(bullish)} months):")
print(f"  Correct: {bullish['correct'].sum()} / {len(bullish)} = {bullish['correct'].mean()*100:.1f}%")
print(f"  Avg allocation: {bullish['allocation'].mean():.1f}%")
print(f"  Avg actual return: {bullish['actual_return_pct'].mean():.2f}%")

print(f"\nBearish predictions ({len(bearish)} months):")
print(f"  Correct: {bearish['correct'].sum()} / {len(bearish)} = {bearish['correct'].mean()*100:.1f}%")
print(f"  Avg allocation: {bearish['allocation'].mean():.1f}%")
print(f"  Avg actual return: {bearish['actual_return_pct'].mean():.2f}%")

# Find worst months
print("\n" + "=" * 60)
print("Worst Performing Months")
print("=" * 60)

df['strategy_return'] = df['strategy_value'].pct_change() * 100
worst = df.nsmallest(5, 'strategy_return')[['date', 'prediction', 'actual', 'allocation', 'strategy_return', 'actual_return_pct', 'correct']]
print(worst.to_string(index=False))

# Find best months
print("\n" + "=" * 60)
print("Best Performing Months")
print("=" * 60)

best = df.nlargest(5, 'strategy_return')[['date', 'prediction', 'actual', 'allocation', 'strategy_return', 'actual_return_pct', 'correct']]
print(best.to_string(index=False))

# Problem diagnosis
print("\n" + "=" * 60)
print("DIAGNOSIS")
print("=" * 60)

# Check if we're too aggressive when wrong
wrong_bullish = df[(df['prediction'] == 'ขึ้น') & (df['correct'] == False)]
if len(wrong_bullish) > 0:
    print(f"\n⚠️ Problem 1: Wrong Bullish Predictions")
    print(f"  Count: {len(wrong_bullish)} months")
    print(f"  Avg allocation: {wrong_bullish['allocation'].mean():.1f}% (too high!)")
    print(f"  Avg loss: {wrong_bullish['actual_return_pct'].mean():.2f}%")
    print(f"  Total damage: {(wrong_bullish['allocation'].mean()/100 * wrong_bullish['actual_return_pct'].sum()):.2f}%")

# Check if we're too conservative when right
right_bullish = df[(df['prediction'] == 'ขึ้น') & (df['correct'] == True)]
if len(right_bullish) > 0:
    print(f"\n✅ Correct Bullish Predictions")
    print(f"  Count: {len(right_bullish)} months")
    print(f"  Avg allocation: {right_bullish['allocation'].mean():.1f}%")
    print(f"  Avg gain: {right_bullish['actual_return_pct'].mean():.2f}%")
    print(f"  Total gain: {(right_bullish['allocation'].mean()/100 * right_bullish['actual_return_pct'].sum()):.2f}%")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("\n1. ลด allocation เมื่อ confidence ต่ำ")
print("2. เพิ่ม Stop Loss mechanism")
print("3. ใช้ Volatility-based position sizing")
print("4. Re-train model บ่อยขึ้น (ทุก 1 เดือน)")
