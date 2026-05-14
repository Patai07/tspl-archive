# 🌐 tools_web — เครื่องมือจัดการเว็บและฐานข้อมูล

โฟลเดอร์นี้เก็บสคริปต์สำหรับ Deploy เว็บไซต์, จัดการ Database และงาน Maintenance ต่างๆ

---

## 📁 รายละเอียดไฟล์

| ไฟล์ | หน้าที่ |
|------|---------|
| `deploy.command` | Deploy เว็บไซต์ขึ้น Vercel (ใช้ก่อน push งานขึ้น production) |
| `clear_sheet.command` | ล้างข้อมูลใน Google Sheet ที่ระบุ (ใช้ระวัง!) |
| `run_extractor.command` | รัน semiotic_extractor.py เพื่อดึงข้อมูลสัญลักษณ์จาก Claude |
| `semiotic_extractor.py` | ดึงข้อมูลเชิงสัญญะ (semiotics) ของลวดลายโดยใช้ Claude AI เขียนลง Haiku sheet |
| `db_mirror.py` | Mirror ข้อมูลจาก Google Sheets ลงไฟล์ .csv ในเครื่อง (สำรองข้อมูล) |
| `fix_footer_links.py` | แก้ลิงก์ footer ในไฟล์ HTML ทุกไฟล์ให้ถูกต้อง |
| `optimize_images.py` | สคริปต์ลดขนาดภาพ (Compress) ให้เล็กกว่า 500KB และปรับสัดส่วนภาพแนวตั้งให้เป็น 4:3 อัตโนมัติ (ใส่พื้นหลังเบลอ) เพื่อแก้ปัญหา Deploy ขึ้น Vercel ไม่ผ่าน |

---

## ⚠️ ข้อควรระวัง

- **`clear_sheet.command`** — จะลบข้อมูลใน Sheet ที่ระบุจริงๆ ใช้ด้วยความระมัดระวัง
- **`deploy.command`** — Deploy ขึ้น Vercel จริง มีผลกระทบกับหน้าเว็บที่ใช้งานจริง
- **`semiotic_extractor.py`** — เขียนข้อมูลลง **Haiku sheet** เท่านั้น ไม่แตะหน้า Master (ปลอดภัย)

---

*อัปเดตล่าสุด: พ.ค. 2569*
