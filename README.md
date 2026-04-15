# 🏛️ Thai Symbol Pattern Lab (TSPL) - Technical Documentation

โปรเจกต์คลังข้อมูลลวดลายไทยดิจิทัล พัฒนาเพื่อการบริหารจัดการมรดกทางวัฒนธรรมในรูปแบบ Dynamic Web Application

## 🛠️ ระบบการทำงาน (System Architecture)
เว็บไซต์นี้ทำงานแบบ **Serverless & Dynamic Database** โดยใช้หลักการดึงข้อมูลจากภายนอก:
- **Frontend:** Core HTML / Vanilla CSS / JavaScript (No framework dependencies)
- **Database:** Google Sheets (เชื่อมต่อผ่าน CSV Published URL)
- **Parsing:** Library **PapaParse** สำหรับแปลงไฟล์ CSV เป็น JSON Data

---

## 📊 การบริหารจัดการข้อมูล (Data Management)

### 1. การเชื่อมต่อ Google Sheets
ข้อมูลลวดลายทั้งหมดถูกควบคุมผ่าน Google Sheets เพื่อให้ผู้ที่ไม่ใช่โปรแกรมเมอร์สามารถแก้ไขได้:
1.  เปิด Google Sheet ที่ต้องการ
2.  ไปที่แท็บ `File` > `Share` > `Publish to the web`
3.  เลือกทั้งเอกสาร (Entire Document) และเลือกรูปแบบเป็น `Comma-separated values (.csv)`
4.  ก๊อปปี้ลิงก์ที่ได้ไปวางในไฟล์ `assets/js/index.js` ที่ตัวแปร `CSV_URL`

### 2. มาตรฐานคอลัมน์ (Column Headers)
ห้ามแก้ไขชื่อหัวคอลัมน์ใน Google Sheets เนื่องจากจะส่งผลต่อการดึงข้อมูล ระบบรองรับคอลัมน์หลักดังนี้:
- `Symbol ID`, `Title (TH)`, `Title (EN)`, `Category`, `Location`, `Confidence`, `Ethics` และลิงก์รูปภาพต่างๆ

---

## 📁 โครงสร้างโฟลเดอร์ไฟล์ (Folder Structure)

```text
/
├── index.html          # หน้าแรก (Hero & Showcase)
├── archive.html        # หน้าคลังข้อมูล (Full Database)
├── tspl_database.csv   # ไฟล์ฐานข้อมูลสำรอง (Offline Fallback)
├── assets/
│   ├── css/
│   │   └── index.css   # สไตล์หลักและระบบ Design System
│   ├── js/
│   │   └── index.js    # หัวใจสำคัญของระบบ (Data Loading, Search, Modal)
│   └── images/
│       └── database/   # คลังรูปภาพลวดลายทั้งหมด (แบ่งโฟลเดอร์ตาม ID)
```

---

## 🎨 มาตรฐานการออกแบบ (Design System)
- **Colors:** Red CI: `#FF4E45`, Navy Bg: `#0F172A`
- **Aspect Ratio:** รูปภาพหน้าปกต้องใช้สัดส่วน **4:3** เท่านั้น เพื่อความเสถียรของ UI

---

## 🚀 การอัปเดตเว็บไซต์ (Deployment)
1.  แกไขข้อมูลใน Google Sheets -> เว็บอัปเดตทันที
2.  แก้ไขโค้ด -> Commit & Push ขึ้น GitHub -> Vercel Deploy อัตโนมัติ

---
*จัดทำโดย: Antigravity AI Assistant*
