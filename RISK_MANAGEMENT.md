# 🛡️ Risk Management System

## ปัญหาที่พบ

### Backtest Results (ก่อนใช้ Risk Management)
- **Win Rate: 64%** ✅ (ทายถูก)
- **Return: -4.15%** ❌ (ขาดทุน!)
- **Sharpe: -0.15** ❌ (แย่มาก)

### สาเหตุ: **ทายผิดแล้วเสียหนัก!**

**เมื่อทายผิด (5 ครั้ง):**
- Allocation เฉลี่ย: **94%** (สูงเกินไป!)
- ขาดทุนเฉลี่ย: **-3.34%** ต่อเดือน
- **Total damage: -15.71%**

**เมื่อทายถูก (9 ครั้ง):**
- Allocation เฉลี่ย: 74.4%
- กำไรเฉลี่ย: +2.25% ต่อเดือน
- **Total gain: +24.85%**

**เดือนที่เสียหนักสุด:**
1. **2025-01**: ทาย ขึ้น 100% → จริง ลง **-8.43%** ❌
2. **2025-10**: ทาย ขึ้น 100% → จริง ลง **-4.03%** ❌
3. **2025-02**: ทาย ขึ้น 100% → จริง ลง **-3.79%** ❌

---

## 💡 แก้ไขอย่างไร?

### Risk Management System

#### 1. **Position Sizing based on Confidence**

```python
if confidence < 60%:  allocation = 30%
if confidence < 65%:  allocation = 50%
if confidence < 75%:  allocation = 70%
if confidence >= 75%: allocation = 85%
```

**ไม่เกิน 80%** (Max Allocation Limit)

#### 2. **Volatility-based Adjustment**

```python
if volatility > 15%:
    penalty = (volatility - 15) / 100
    allocation *= (1 - penalty)
```

**ตัวอย่าง:**
- Volatility 20% → penalty 5% → ลด allocation 5%
- Volatility 25% → penalty 10% → ลด allocation 10%

#### 3. **Drawdown Protection**

```python
if drawdown < -20%:  # Deep drawdown (oversold)
    allocation *= 1.1  # เพิ่มนิดหน่อย (contrarian)
    
if drawdown > -5%:   # Near peak
    allocation *= 0.9  # ลดลง (ระมัดระวัง)
```

#### 4. **Trend Confirmation**

```python
if prediction == Bullish AND trend_score < 30:
    allocation *= 0.8  # ลด 20% (ขัดแย้งกัน)
    
if prediction == Bearish AND trend_score > 70:
    allocation *= 1.2  # ไม่ลดมากเกินไป
```

---

## 📊 ตัวอย่างการทำงาน

### ก่อนใช้ Risk Management
```
Prediction: Bullish
Confidence: 78%
Allocation: 78% (ตาม confidence ตรงๆ)
```

### หลังใช้ Risk Management
```
Prediction: Bullish
Confidence: 73.6%
Base Allocation: 70% (จาก confidence)

Adjustments:
- Volatility: 2.74% (ต่ำ) → ไม่ปรับ
- Drawdown: -21.2% (ลึก) → +10% (oversold)
- Trend: 100/100 (แข็งแกร่ง) → ไม่ปรับ

Final Allocation: 77%
Reason: "Confidence ดี (73.6%) | Deep drawdown (-21.2%) → oversold"
```

---

## 🎯 ผลลัพธ์ที่คาดหวัง

### เป้าหมาย
- **ลดขาดทุนเมื่อทายผิด** จาก -15.71% → -8%
- **รักษากำไรเมื่อทายถูก** ที่ +24.85%
- **Net Return** จาก -4.15% → **+10-15%**
- **Sharpe Ratio** จาก -0.15 → **0.8-1.2**

### กลยุทธ์
1. **ไม่ลงทุนเต็มที่** เมื่อ confidence ต่ำ
2. **ลด exposure** เมื่อ volatility สูง
3. **Contrarian** เมื่อ drawdown ลึก (oversold)
4. **ระมัดระวัง** เมื่อใกล้จุดสูงสุด

---

## 🔧 การใช้งาน

### ใน daily_update.py
```python
from app.risk_management import apply_risk_management

# หลัง ML prediction
risk_result = apply_risk_management(
    prediction=ml_prediction,
    confidence=ml_confidence,
    ml_features=ml_features,
    trend_data=trend_analysis
)

allocation = risk_result["allocation"]
reason = risk_result["reason"]
```

### Output
```json
{
  "allocation": 77,
  "allocation_decimal": 0.77,
  "reason": "Confidence ดี (73.6%) | Deep drawdown (-21.2%) → oversold",
  "risk_adjusted": true,
  "original_confidence": 0.736,
  "volatility": 2.74,
  "drawdown": -21.18,
  "trend_score": 100
}
```

---

## 📈 Backtest ใหม่

ต้องรอ backtest ด้วย Risk Management เพื่อยืนยันผลลัพธ์

**คาดการณ์:**
- Win Rate: 64% (เท่าเดิม)
- Return: **+10-15%** (ดีขึ้น 14-19%)
- Sharpe: **0.8-1.2** (ดีขึ้นมาก)

---

## ⚠️ ข้อควรระวัง

1. **Over-optimization** - อย่าปรับจนเกินไป
2. **Backtest bias** - ต้องทดสอบกับข้อมูลใหม่
3. **Market regime change** - ต้อง re-calibrate เป็นระยะ
4. **Black swan events** - Risk management ไม่ได้ป้องกัน 100%

---

## 📝 TODO

- [ ] Backtest ด้วย Risk Management
- [ ] เพิ่ม Stop Loss mechanism
- [ ] เพิ่ม Take Profit levels
- [ ] Dynamic position sizing based on Kelly Criterion
- [ ] Portfolio rebalancing rules
