# 📦 pipeline_batch — ระบบ Asset Archive Pipeline

โฟลเดอร์นี้เก็บ Pipeline ทั้งหมดสำหรับดึง จัดระเบียบ และ Archive ภาพลวดลายที่ sync มาจาก Drive

---

## 🚀 วิธีใช้งาน (เรียงตามลำดับขั้นตอน)

### ขั้นตอนที่ 1 — รันทุกอย่างในครั้งเดียว
```
ดับเบิ้ลคลิก: run_pipeline.command
```
สคริปต์นี้จะ sync ไฟล์จาก Google Drive และให้ Haiku Vision สแกน + จัดหมวดหมู่รูปทั้งหมดอัตโนมัติ
> ⚠️ ระบบจะ **ข้ามรูปที่เคย classify แล้ว** โดยอัตโนมัติ ไม่เสีย Token ซ้ำ

---

### ขั้นตอนที่ 2 — รีวิวรูปที่ AI ไม่มั่นใจ
```
ดับเบิ้ลคลิก: batch_review.command
```
เปิดหน้าเว็บ http://localhost:5555 (จอสีดำ) แสดงรูปที่สถานะ PENDING
- **A** = Approve (ผ่าน)
- **R** = Reject (ปัดตก)
- **Space / →** = ข้ามไปรูปถัดไป
- ปุ่ม **🤖 ให้ Haiku ดูอีกรอบ** = ส่งรูปให้ AI วิเคราะห์ใหม่ (เสีย Token นิดหน่อย)

---

### ขั้นตอนที่ 3 — สร้าง Asset_Map สรุปผลทั้งหมด
```
ดับเบิ้ลคลิก: batch_finalize.command
```
นำรูปที่ APPROVED ทั้งหมดไปเทียบกับ tspl_database แล้วสร้างตาราง **Asset_Map** ใน Spreadsheet
ระบบจะใช้ทั้ง **ชื่อที่ AI อ่านได้** + **Timestamp การส่งไฟล์** เพื่อจับคู่ให้แม่นยำที่สุด

---

## 📁 รายละเอียดไฟล์แต่ละตัว

| ไฟล์ | หน้าที่ |
|------|---------|
| `run_pipeline.command` | **ปุ่มหลัก** รัน sync + classify รวดเดียวจบ |
| `batch_sync.py` / `.command` | ดึงไฟล์รูปและเอกสารจาก Google Drive มาใส่ Batch_Sync sheet |
| `batch_classify.py` / `.command` | ส่งรูปให้ Claude Haiku Vision วิเคราะห์และเขียนผลลง Batch_Review |
| `batch_review.py` / `.command` | เปิด web UI สำหรับ Human-in-the-loop review |
| `batch_finalize.py` / `.command` | สร้าง Asset_Map โดย match รูปเข้า tspl_database |

---

## 💰 ค่าใช้จ่าย API

- ใช้ **Claude Haiku Vision** ราคาประมาณ **$0.003 USD ต่อรูป** (ประมาณ 10 สตางค์)
- รูป 600 รูป ≈ **$1.80 USD** (~60 บาท)
- การ re-run ไม่เสียเงินซ้ำ เพราะระบบ skip รูปที่ classify แล้ว

---

## 📊 Output ที่ได้

ตาราง `Asset_Map` ใน Google Spreadsheet จะมีคอลัมน์:
- ข้อมูลทุกช่องจาก **tspl_database** (หน้าแรก)
- `in_database` — ✅ หรือ ❌
- `image_url_1/2/3` — ลิงก์รูปภาพ (กดได้)
- `doc_url` — ลิงก์ไฟล์เอกสาร
- `status` — COMPLETE / NO_IMAGE / NO_DOC / MISSING / NEW
- `image_count` — จำนวนรูปที่จับคู่ได้

---

*อัปเดตล่าสุด: พ.ค. 2569*
