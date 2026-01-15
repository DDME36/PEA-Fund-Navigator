# 🧭 PEA Fund Navigator

ระบบ AI นำทางสำหรับกองทุนสำรองเลี้ยงชีพ PEA - แนะนำสัดส่วน PEA-E (หุ้น) vs PEA-F (ตราสารหนี้)

## 📊 Model

**ML Ensemble** - รวม 3 โมเดล:
- XGBoost
- Random Forest  
- Gradient Boosting

ใช้ข้อมูลรายเดือนจาก TDEX.BK (SET50 ETF)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### 2. Run Daily Update

```bash
python scripts/daily_update.py
```

### 3. Run Frontend

```bash
cd frontend
npm run dev
```

เปิด http://localhost:3000

---

## 🌐 Deploy บน Vercel

### วิธีตั้งค่า:

1. **Push โปรเจคขึ้น GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/DDME36/PEA-Fund-Navigator.git
   git push -u origin main
   ```

2. **เชื่อม Vercel กับ GitHub**
   - ไปที่ [vercel.com](https://vercel.com)
   - Import repository `PEA-Fund-Navigator`
   - ตั้งค่า:
     - Framework: Next.js
     - Root Directory: `frontend`
   - Deploy!

3. **ตั้งค่าอัพเดทอัตโนมัติ (บนคอมคุณ)**
   ```
   รัน: scripts/setup_startup_vercel.bat
   ```
   
   ทุกครั้งที่เปิดคอม จะ:
   - รัน `daily_update.py` อัพเดทข้อมูล
   - Push ไป GitHub อัตโนมัติ
   - Vercel จะ deploy ใหม่อัตโนมัติ

---

## 📁 Scripts

| ไฟล์ | คำอธิบาย |
|------|----------|
| `scripts/daily_update.py` | อัพเดทข้อมูลและ prediction |
| `scripts/auto_update.bat` | รันอัพเดท (local only) |
| `scripts/update_and_push.bat` | รันอัพเดท + push GitHub |
| `scripts/setup_startup_vercel.bat` | ตั้งค่ารันอัตโนมัติตอนเปิดคอม |
| `scripts/remove_startup.bat` | ลบการรันอัตโนมัติ |

---

## 📈 Performance (ML Backtest)

- **Win Rate**: ~71%
- **Return**: +10.98% (vs Buy&Hold -5.06%)
- **Sharpe Ratio**: 1.53
- **Max Drawdown**: -1.18%

---

## 📁 Project Structure

```
├── app/                    # Backend (Python)
│   ├── monthly_ml.py      # ML Ensemble model
│   ├── data_fetcher.py    # ดึงข้อมูลราคา
│   └── config.py          # ตั้งค่า
│
├── frontend/              # Frontend (Next.js)
│   ├── app/page.tsx       # หน้าหลัก
│   ├── public/data/       # JSON data
│   └── lib/               # Types & API
│
├── scripts/               # Scripts
│   ├── daily_update.py    # อัพเดทรายวัน
│   └── *.bat              # Windows scripts
│
└── models/                # Saved ML models
    ├── monthly_ml.joblib
    └── monthly_scaler.joblib
```

---

## ⚠️ Disclaimer

ใช้ประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำการลงทุน
