# ตั้งค่า Windows Task Scheduler

## วิธีตั้งให้รันอัตโนมัติตอนเปิดเครื่อง

### 1. เปิด Task Scheduler
- กด `Win + R` พิมพ์ `taskschd.msc` แล้ว Enter

### 2. สร้าง Task ใหม่
- คลิก "Create Basic Task..." ทางขวา
- ตั้งชื่อ: `PEA Fund Daily Update`
- Description: `อัพเดทข้อมูลกองทุนวันละครั้ง`

### 3. Trigger
- เลือก "When I log on" (ตอน login เข้า Windows)
- หรือเลือก "Daily" แล้วตั้งเวลา เช่น 08:00

### 4. Action
- เลือก "Start a program"
- Program/script: `C:\path\to\your\project\scripts\run_daily.bat`
- Start in: `C:\path\to\your\project`

### 5. เสร็จสิ้น
- ติ๊ก "Open the Properties dialog..." แล้วกด Finish
- ใน Properties ไปที่ Settings
- ติ๊ก "Run task as soon as possible after a scheduled start is missed"

---

## ทดสอบ
```cmd
cd C:\path\to\your\project
python scripts/daily_update.py
```

## Auto Push to GitHub (Optional)
แก้ไขไฟล์ `run_daily.bat` โดยเอา `REM` ออกจากบรรทัด git commands

---

## สำหรับ Vercel
1. Push โปรเจคไป GitHub
2. Connect repo กับ Vercel
3. ทุกครั้งที่รัน daily_update.py แล้ว push ข้อมูลจะอัพเดทอัตโนมัติ
