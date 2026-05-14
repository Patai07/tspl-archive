# 🔧 tools_debug — สคริปต์ Debug และวิเคราะห์ปัญหา

โฟลเดอร์นี้เก็บสคริปต์ที่ใช้แก้ไขปัญหาและตรวจสอบข้อมูลระหว่างการพัฒนา
**ไม่ใช่ส่วนหนึ่งของ Pipeline หลัก** — ใช้เมื่อต้องการ diagnose ปัญหาเท่านั้น

---

## 📁 รายละเอียดไฟล์

| ไฟล์ | หน้าที่ |
|------|---------|
| `debug_match.py` | ตรวจสอบว่าชื่อลายจาก LINE match กับ Database ได้ดีแค่ไหน แสดงรายการที่ match ไม่ได้ |
| `debug_time.py` | ตรวจสอบ Timestamp ของไฟล์ใน LINE_Sync ว่า format ถูกต้องและ parse ได้ไหม |

---

## 🏃 วิธีรัน

```bash
cd /Users/phu/Desktop/งานพี่กบ/Web
python3 tools_debug/debug_match.py
python3 tools_debug/debug_time.py
```

---

## 💡 เมื่อไหร่ที่ควรใช้

- เมื่อ Asset_Map มีลาย MISSING เยอะผิดปกติ → รัน `debug_match.py` เพื่อดูว่าชื่อผิดเพี้ยนตรงไหน
- เมื่อ Context-Aware Matching จับคู่รูปกับเอกสารผิดพลาด → รัน `debug_time.py` เพื่อตรวจ Timestamp

---

*อัปเดตล่าสุด: พ.ค. 2569*
