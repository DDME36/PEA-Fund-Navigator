# 🚀 คู่มือการใช้งานและ Deploy

## 📍 สถานะปัจจุบัน

### ✅ Auto Run (Task Scheduler)
- **Status**: เปิดใช้งานแล้ว
- **Task Name**: "PEA Fund Update"
- **Trigger**: รันตอนเปิดเครื่อง/login
- **Auto Push**: เปิดอยู่ (จะ push ไป GitHub อัตโนมัติ)

### 📂 ตำแหน่งไฟล์สำคัญ
```
C:\Users\satay\Desktop\mfc\
├── .auto_push                    # Flag สำหรับ auto push
├── update.bat                    # Script หลัก
├── setup_auto_run.bat            # ตั้งค่า auto run
├── setup_auto_run_admin.vbs      # Run as admin
├── logs/                         # Log files
│   └── auto_YYYYMMDD_HHMMSS.log
└── frontend/public/data/
    └── prediction.json           # ข้อมูลที่ถูก push ไป GitHub
```

---

## 🔧 การจัดการ Auto Run

### ตรวจสอบสถานะ
```powershell
# ดู Task Scheduler
Get-ScheduledTask -TaskName "PEA Fund Update"

# ดู Auto Push status
if (Test-Path .auto_push) { "ENABLED" } else { "DISABLED" }
```

### เปิด/ปิด Auto Run

**วิธีที่ 1: ใช้ VBS (แนะนำ)**
```cmd
# ดับเบิลคลิก
setup_auto_run_admin.vbs
```

**วิธีที่ 2: ใช้ update.bat**
```cmd
update.bat
# เลือก 5 (Setup Auto Run)
```

**วิธีที่ 3: Manual**
```cmd
# เปิด
schtasks /Create /TN "PEA Fund Update" /TR "C:\Users\satay\Desktop\mfc\update.bat auto" /SC ONLOGON /F /RL HIGHEST

# ปิด
schtasks /Delete /TN "PEA Fund Update" /F
```

### เปิด/ปิด Auto Push

**เปิด Auto Push:**
```cmd
echo 1 > .auto_push
```

**ปิด Auto Push:**
```cmd
del .auto_push
```

---

## 🌐 การ Deploy เว็บไซต์

### Vercel (ปัจจุบัน)

**การทำงาน:**
1. Script รันอัตโนมัติตอนเปิดเครื่อง
2. สร้าง `prediction.json` ใหม่
3. Push ไป GitHub (ถ้าเปิด Auto Push)
4. Vercel detect การเปลี่ยนแปลง
5. Deploy อัตโนมัติ

**ตรวจสอบ:**
- GitHub: https://github.com/DDME36/PEA-Fund-Navigator
- Vercel: https://vercel.com/dashboard

**Manual Deploy:**
```cmd
update.bat
# เลือก 3 (Update + Push)
```

### การอัพเดทเว็บไซต์

**ไฟล์ที่เปลี่ยนแปลง:**
- ✅ `frontend/app/page.tsx` - เพิ่ม Multi-Fund Component
- ✅ `frontend/components/multi-fund-allocation.tsx` - Component ใหม่
- ✅ `frontend/lib/types.ts` - เพิ่ม types

**ต้อง Deploy:**
```bash
cd frontend
npm run build
git add .
git commit -m "Update: Multi-fund allocation UI"
git push
```

หรือใช้:
```cmd
update.bat
# เลือก 3
```

---

## 📊 การอัพเดทโมเดล

### Re-train Model (แนะนำทุก 1-3 เดือน)

```cmd
python scripts/retrain_model.py
```

**ผลลัพธ์:**
- Train ด้วยข้อมูลล่าสุด
- บันทึกโมเดลใหม่ใน `models/`
- แสดง accuracy, precision, recall, F1

### ทดสอบโมเดลใหม่

```cmd
python scripts/daily_update.py
```

**ตรวจสอบ:**
- ดู `frontend/public/data/prediction.json`
- ตรวจสอบ `ml_details.adjustment`
- ดู Win Rate ใน backtest

---

## 🐛 Troubleshooting

### 1. Auto Run ไม่ทำงาน

**ตรวจสอบ:**
```powershell
Get-ScheduledTask -TaskName "PEA Fund Update" | Select-Object State, LastRunTime
```

**แก้ไข:**
```cmd
# ลบ task เก่า
schtasks /Delete /TN "PEA Fund Update" /F

# สร้างใหม่
setup_auto_run_admin.vbs
```

### 2. Git Push ล้มเหลว

**Error: "Unable to persist credentials"**
```cmd
# แก้ไข credential store
git config --global credential.helper wincred
```

**Error: "Authentication failed"**
```cmd
# ตั้งค่า Git credentials ใหม่
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 3. Vercel ไม่ Deploy

**ตรวจสอบ:**
1. เข้า Vercel Dashboard
2. ดู Deployment logs
3. ตรวจสอบ Build errors

**แก้ไข:**
```bash
cd frontend
npm run build  # ทดสอบ build ก่อน
```

### 4. โมเดลทำนายผิดบ่อย

**ตรวจสอบ:**
```cmd
# ดู backtest results
python scripts/daily_update.py
# ดู Win Rate ใน prediction.json
```

**แก้ไข:**
```cmd
# Re-train ด้วยข้อมูลใหม่
python scripts/retrain_model.py
```

---

## 📝 Log Files

### ตำแหน่ง
```
logs/
├── auto_YYYYMMDD_HHMMSS.log    # Auto run logs
└── update_YYYYMMDD_HHMMSS.log  # Manual run logs
```

### ดู Log ล่าสุด
```powershell
Get-Content (Get-ChildItem logs\auto_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

### ลบ Log เก่า (เก็บแค่ 30 วัน)
```powershell
Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

---

## 🔄 Workflow ปกติ

### รายวัน (อัตโนมัติ)
1. เปิดเครื่อง/Login
2. Task Scheduler รัน `update.bat auto`
3. ดึงข้อมูลตลาด
4. ทำนายด้วย Improved Predictor
5. สร้าง `prediction.json`
6. Push ไป GitHub (ถ้าเปิด Auto Push)
7. Vercel deploy อัตโนมัติ

### รายเดือน (Manual)
1. Re-train model: `python scripts/retrain_model.py`
2. ทดสอบ: `python scripts/daily_update.py`
3. ตรวจสอบ Win Rate
4. Deploy: `update.bat` → เลือก 3

### ฉุกเฉิน (ถ้ามีปัญหา)
1. ปิด Auto Run: `setup_auto_run_admin.vbs` → เลือก 3
2. แก้ไขปัญหา
3. ทดสอบ: `update.bat` → เลือก 1
4. เปิด Auto Run อีกครั้ง

---

## 📞 Quick Commands

```cmd
# ทดสอบ
update.bat → 1

# อัพเดทข้อมูล
update.bat → 2

# อัพเดท + Push
update.bat → 3

# Re-train model
python scripts/retrain_model.py

# ตั้งค่า Auto Run
setup_auto_run_admin.vbs

# ดู Task Scheduler
taskschd.msc
```

---

## ✅ Checklist หลัง Deploy

- [ ] ทดสอบ `python scripts/daily_update.py`
- [ ] ตรวจสอบ `prediction.json` มี `multi_fund`
- [ ] ตรวจสอบ `ml_details.adjustment` มีการปรับปรุง
- [ ] Push ไป GitHub
- [ ] ตรวจสอบ Vercel deploy สำเร็จ
- [ ] เปิดเว็บดูว่าแสดง 4 กอง
- [ ] ทดสอบเปลี่ยนโหมดความเสี่ยง (Conservative/Moderate/Aggressive)
- [ ] ตรวจสอบ Auto Run ยังทำงาน
