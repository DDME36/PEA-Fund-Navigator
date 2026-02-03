# Changelog - PEA Fund Navigator

## [2.0.0] - 2026-02-03

### 🎉 Major Update: Multi-Fund Support

#### Added
- **4-Fund Allocation System**
  - PEA-F (Fixed Income) - ตราสารหนี้
  - PEA-E (Thai Equity) - หุ้นไทย (SET Index)
  - PEA-G (Global Equity) - หุ้นต่างประเทศ (S&P 500)
  - PEA-P (Property/REITs) - อสังหาฯ (LPF, WHART, FTREIT)

- **3 Risk Profiles**
  - Conservative (ปลอดภัย) - เน้นความมั่นคง
  - Moderate (ปกติ) - สมดุล
  - Aggressive (ดุดัน) - เน้นผลตอบแทน

- **EMA Smoothing**
  - ลดการสวิงของสัดส่วน
  - ใช้ Exponential Moving Average (70% old, 30% new)
  - บันทึกประวัติสัดส่วนใน `models/allocation_history.json`

- **Multi-Asset Data Fetching**
  - ดึงข้อมูล SET Index (^SET.BK)
  - ดึงข้อมูล S&P 500 (^GSPC)
  - ดึงข้อมูล Thai REITs (LPF.BK, WHART.BK, FTREIT.BK)
  - คำนวณ Bond Yield (ใช้ค่าประมาณ 2.5% ต่อปี)

#### Changed
- `scripts/daily_update.py` - รองรับ 4 กองทุน
- `app/config.py` - เพิ่ม risk profiles และ smoothing settings
- `frontend/lib/types.ts` - เพิ่ม MultiFundAllocation interface
- `frontend/components/` - เพิ่ม multi-fund-allocation.tsx

#### Technical Details
- **Smoothing Formula**: `new = 0.7 * old + 0.3 * predicted`
- **Score Calculation**: 
  - Return Score (50%)
  - Trend Score (30%)
  - Volatility Score (20%)
- **Normalization**: สัดส่วนถูก normalize ให้รวมเป็น 100% เสมอ

---

## [1.0.0] - 2026-01-15

### Initial Release
- ML Ensemble Model (XGBoost + RF + GB)
- 2-Fund Allocation (PEA-E vs PEA-F)
- Monthly prediction
- Backtest system
- Auto-update script
