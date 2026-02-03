# 🚀 การปรับปรุงโมเดล - PEA Fund Navigator

## 📊 ปัญหาที่พบ (ก่อนปรับปรุง)

### 1. Win Rate ต่ำมาก (42.9%)
- โมเดลทายผิดมากกว่าทายถูก
- ทาย "Bearish" บ่อยเกินไป (Bearish Bias)
- ตลาดจริงๆ ขึ้นบ่อยกว่า แต่โมเดลไม่กล้าทาย Bullish

### 2. ข้อมูลขัดแย้งกัน
```
Trend Score: 100/100 (ขาขึ้นแข็งแกร่ง)
ML Prediction: Bearish (52%)
Recommendation: "PEA-F ปลอดภัยกว่า"
```
- Momentum 3m: +6.32%, 6m: +8.05% (ดีมาก)
- แต่โมเดลกลับทาย Bearish!

### 3. Ensemble ไม่เห็นด้วยกัน
- XGBoost: Bearish (57%)
- Random Forest: Bearish (60%)
- Gradient Boosting: Bullish (61%)
- Ensemble: Bearish (52%) - แทบจะ 50:50

### 4. Sharpe Ratio ต่ำ (0.53)
- ควรอยู่ที่ 1.0+ เพื่อถือว่าดี
- Return ดี (+4.24%) แต่ความเสี่ยงสูงเกินไป

---

## 💡 แนวทางแก้ไข

### 1. **Trend-Aware Adjustment**
ปรับ prediction ตาม trend score:
- Trend Score > 70% → เพิ่มน้ำหนัก Bullish
- Trend Score < 30% → เพิ่มน้ำหนัก Bearish

### 2. **Momentum Boost**
ใช้ momentum ช่วยตัดสิน:
- Momentum 3m > 3% และ 6m > 5% → Bullish +2
- Momentum 3m > 0% และ 6m > 0% → Bullish +1
- Momentum ติดลบ → Bearish

### 3. **RSI Contrarian Signals**
ใช้ RSI แบบ contrarian:
- RSI < 30 (Oversold) → Bullish +1 (มักจะ bounce)
- RSI > 70 (Overbought) → Bearish +1 (มักจะ correct)

### 4. **Drawdown Recovery**
- Drawdown < -15% → Bullish +1 (oversold, likely to recover)
- Drawdown > -5% → Bearish +1 (near peak, be careful)

### 5. **Signal-Based Calibration**
รวม ML prediction กับ signals:
```python
adjusted_prob = 0.6 * ml_prob + 0.4 * signal_ratio
```
- 60% จาก ML
- 40% จาก Technical Signals

---

## ✅ ผลลัพธ์หลังปรับปรุง

### ตัวอย่างการทำงาน (2026-02-03)

**ข้อมูลตลาด:**
- Trend Score: 100/100 (ขาขึ้นแข็งแกร่ง)
- Momentum 3m: +6.32%, 6m: +8.05%
- RSI: 74.3 (Overbought)
- Drawdown: -21.18% (Deep)

**Base ML Prediction:**
- Bearish (52.1%)
- XGBoost: Bearish, RF: Bearish, GB: Bullish

**Signal Analysis:**
- Bullish Signals: 4
  - Trend Score > 70 (+2)
  - Momentum positive (+1)
  - Drawdown < -15% (+1)
- Bearish Signals: 2
  - RSI > 70 (+1)
  - Drawdown still significant (+1)

**Final Prediction:**
- **Bullish (55.4%)** ✅
- Prediction CHANGED by trend adjustment!

---

## 📈 คาดการณ์การปรับปรุง

### Win Rate
- เดิม: 42.9%
- คาดหวัง: **55-60%** (เพิ่ม 12-17%)

### Sharpe Ratio
- เดิม: 0.53
- คาดหวัง: **0.8-1.2** (เพิ่ม 50-125%)

### Consistency
- ลด Bearish Bias
- ทำนายสอดคล้องกับ Trend มากขึ้น
- ลดความขัดแย้งระหว่าง Indicators

---

## 🔧 การใช้งาน

### ใช้ Improved Predictor
```python
from app.improved_predictor import ImprovedPredictor

predictor = ImprovedPredictor()
prediction, confidence, details = predictor.predict_with_trend_adjustment(monthly)

# ดู adjustment details
if "adjustment" in details:
    adj = details["adjustment"]
    print(f"Base: {adj['base_prediction']} ({adj['base_confidence']:.1%})")
    print(f"Signals: Bullish={adj['bullish_signals']}, Bearish={adj['bearish_signals']}")
    print(f"Final: {adj['adjusted_prediction']} ({adj['adjusted_confidence']:.1%})")
```

### Backtest Improved Model
```python
backtest_result = predictor.backtest_improved(monthly)
print(f"Win Rate: {backtest_result['metrics']['win_rate_pct']}%")
print(f"Sharpe: {backtest_result['metrics']['sharpe_ratio']}")
```

---

## 🎯 สิ่งที่ยังต้องพัฒนาต่อ

### 1. **Re-train Model**
- โมเดลปัจจุบัน train ตั้งแต่ 2026-01-15
- ควร re-train ด้วยข้อมูลใหม่ทุก 1-3 เดือน

### 2. **Feature Engineering**
- เพิ่ม features จาก 4 กองทุน (PEA-G, PEA-P)
- เพิ่ม Macro indicators (GDP, Inflation, Interest Rate)
- เพิ่ม Sentiment indicators (News, Social Media)

### 3. **Ensemble Weighting**
- ปรับน้ำหนัก XGBoost, RF, GB ตาม performance
- ใช้ Stacking แทน Simple Voting

### 4. **Risk Management**
- เพิ่ม Stop Loss / Take Profit
- Dynamic Position Sizing
- Volatility-based Allocation

### 5. **Multi-Timeframe Analysis**
- รวม Daily + Weekly + Monthly signals
- Long-term trend + Short-term timing

---

## 📝 สรุป

การปรับปรุงครั้งนี้แก้ปัญหาหลักๆ ได้:
- ✅ แก้ Bearish Bias
- ✅ ลดความขัดแย้งระหว่าง Indicators
- ✅ เพิ่มความสอดคล้องกับ Trend
- ✅ ใช้ Technical Signals ช่วยตัดสิน

**คาดว่า Win Rate จะเพิ่มจาก 42.9% → 55-60%**

ต้องรอ backtest ย้อนหลังเพื่อยืนยันผลลัพธ์จริง!
