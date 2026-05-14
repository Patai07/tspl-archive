# 🏛️ Thai Symbol Pattern Lab (TSPL) - Digital Archive Project

**TSPL (Thai Symbol Pattern Lab)** คือ โครงการระบบบริหารจัดการและจัดเก็บมรดกทางวัฒนธรรมลายไทยดิจิทัล (Digital Archive) ซึ่งรวบรวมลวดลายสถาปัตยกรรมและศิลปกรรมไทยจำนวน 180 รายการ เพื่อการถอดรหัสอัตลักษณ์ สกัดรอยมรดกไทย และแปลงให้อยู่ในรูปแบบของ "สินทรัพย์ดิจิทัล" (Digital Assets) ที่พร้อมใช้งาน

## 📌 จุดประสงค์หลักของระบบ (Core Objectives)
1. **เก็บรวบรวมและจัดหมวดหมู่ (Taxonomy & Archiving):** รวบรวมลวดลายจากหลักฐานชั้นต้น (ล้านนา, อยุธยา ฯลฯ) และจัดระบบข้อมูลทางสัญวิทยา
2. **วิเคราะห์เชิงโครงสร้าง (Structural Analysis):** แยกองค์ประกอบของลายออกเป็น "หน่วยคำทัศน์" (Visual Morphemes) เพื่อให้ง่ายต่อความเข้าใจและการนำไปประยุกต์ใช้
3. **ความพร้อมในการใช้งาน (Vector Readiness):** ให้บริการไฟล์ภาพลวดลายในรูปแบบเวกเตอร์ (SVG) สำหรับการต่อยอดใน Creative Economy
4. **ความตระหนักรู้ด้านจริยธรรม (Cultural Ethics):** ระบุระดับความเหมาะสมในการนำไปใช้งาน (เช่น ลายทั่วไป, ลายพิธีกรรม, ลายศักดิ์สิทธิ์) และข้อควรระวัง (Protocol)

## ⚙️ สถาปัตยกรรมระบบ (System Architecture)
- **Frontend / UI:** พัฒนาด้วย HTML, CSS (Tailwind CSS) และ Vanilla JavaScript เน้นดีไซน์พรีเมียมแบบ Cinematic, สไตล์ Blueprint/Technical Interface ผสมผสานกลิ่นอายแบบ Sila Jaruek (ศิลาจารึก)
- **Database:** ใช้ Google Sheets เป็น Headless CMS / Database (ดึงข้อมูลผ่าน CSV ให้อัปเดตแบบ Real-time)
- **Data Attributes:** ระดับความน่าเชื่อถือของลาย (Verified, Reconstructed, Fragment, Hypothetical), สถานที่พบ, บริบทแวดล้อม และชุดคำค้นหา (Tags)

---

## 📌 มาตรฐานหมวดหมู่ (Master Categories)
เพื่อให้ข้อมูลสอดคล้องกับงานวิจัยล่าสุด ระบบได้แบ่งหมวดหมู่ลวดลายออกเป็น 4 กลุ่มหลัก:
1.  **Nature & Botany** (พรรณพฤกษาและธรรมชาติ) - รหัสย่อ: `NAT`
2.  **Fauna & Mythical** (สรรพสัตว์และสัตว์หิมพานต์) - รหัสย่อ: `FAU`
3.  **Geometric & Synthetic** (เรขาคณิตและลวดลายประดิษฐ์) - รหัสย่อ: `GEO`
4.  **Sacred & Belief** (สัญลักษณ์ความเชื่อและสิ่งศักดิ์สิทธิ์) - รหัสย่อ: `SAC`

---

## 📂 การจัดเก็บไฟล์ (Asset Organization)
ทุกลวดลายจะมีโฟลเดอร์รหัสส่วนตัวอยู่ใน `assets/images/database/` โดยจะแยกตามโฟลเดอร์หมวดหมู่หลักดังนี้:

```text
/assets/images/database/[Category_Folder]/[Pattern-ID]/
├── main.jpg        # รูปภาพหลักสำหรับแสดงผลหน้าตาราง
├── context.jpg     # รูปภาพบริบท/สถานที่จริง
├── detail.jpg      # รูปภาพซูมรายละเอียด
└── vectors/
    └── vector.svg  # ไฟล์ลายเส้นเวกเตอร์ (แสดงลายนิ่งและให้ดาวน์โหลด)

ตัวอย่างพาธ: assets/images/database/01_Nature/TSP-LST-NAT-001/main.jpg
```

---

## ⚡ วิธีการอัปเดตข้อมูลแบบใหม่ (New Workflow)

### 1. จัดเตรียมข้อมูลต้นทาง (Google Drive)
- ข้อมูลทั้งหมดจะถูกจัดการที่โฟลเดอร์ Google Drive หลักที่ถูกจัดเรียงตามหมวดหมู่ (ไม่ต้องผ่าน LINE Bot)
- ในโฟลเดอร์ของทุกลาย จะประกอบด้วยรูปภาพและเอกสารคำอธิบายลาย (เช่น `.docx`)

### 2. การสกัดข้อมูล (Semiotic Extraction)
- เปิดหน้า **System Control Dashboard**
- กดรันเครื่องมือ **✍️ Semiotic Extractor** หรือรันไฟล์ `tools_web/run_extractor.command`
- ระบบ AI (Claude) จะเข้าไปอ่านเอกสารใน Drive และสกัดข้อมูลลง Google Sheets ให้อัตโนมัติ

### 3. การดึงรูปภาพและปรับขนาด (Asset Sync & Optimization)
- ใน Dashboard กดปุ่ม **📥 Download Assets** เพื่อดึงรูปใหม่ลงมายังโฟลเดอร์โปรเจกต์ (`assets/images/database/`)
- **ข้อควรระวังเรื่องขนาดไฟล์:** ก่อน Deploy ขึ้นระบบ ให้ใช้คำสั่งรันสคริปต์เพิ่มลดขนาดภาพ:
  `python3 tools_web/optimize_images.py`
  *(สคริปต์จะทำการบีบอัดรูปภาพให้เล็กกว่า 500KB และแปลงภาพแนวตั้งให้เป็นสัดส่วน 4:3 พร้อมพื้นหลังเบลอ เพื่อไม่ให้เปลืองพื้นที่ Vercel)*

### 4. การอัปเดตขึ้น Server (Deployment)
- กด **🚀 Deploy to Production** ในหน้า Dashboard หรือดับเบิลคลิกไฟล์ `deploy.command`
- ระบบจะส่งไฟล์ทั้งหมดขึ้น Vercel และเปิดให้ใช้งานจริงภายใน 1-2 นาที

---

## 🎨 มาตรฐานเชิงเทคนิค
- **Image Aspect Ratio:** 4:3 (แนะนำ)
- **Vector Format:** .svg (ต้องวางในโฟลเดอร์ `/vectors/`)
- **Download System:** หน้าเว็บจะทำการ Rename ไฟล์เวกเตอร์ตอนดาวน์โหลดให้อัตโนมัติเป็น `TSPL_[ID]_[Title].svg`

---

## 🛡️ กฎการพัฒนาเพื่อให้ระบบเสถียร (Development & Stability Guidelines)
เพื่อให้การทำงานหลังจากนี้ (รวมถึงเมื่อให้ AI ช่วยเขียนโค้ด) มีความราบรื่นและไม่กระทบโครงสร้างเดิม กรุณายึดหลักการดังนี้:

### 1. การจัดการข้อมูล (Data Integrity & Database)
- **ห้ามเปลี่ยนชื่อคอลัมน์ (Column Headers) ใน Google Sheets เด็ดขาด:** โค้ดใน `index.js` ผูกกับชื่อคอลัมน์อย่างตายตัว (เช่น `Symbol ID`, `Title (TH)`, `Morphemes (TH)`) หากเปลี่ยน จะทำให้หน้าเว็บพังหรือข้อมูลว่างเปล่า
- **เครื่องหมายแบ่งข้อมูล:** ในช่อง Morphemes และ Tags หากมีหลายคำ ให้ใช้เครื่องหมาย `|` (Pipe) สำหรับ Morphemes และ `,` (Comma) สำหรับ Tags เสมอ
- **อัปเดตแบบ Real-time:** ระบบดึงข้อมูลจาก Published CSV Link ตอนที่ User เปิดหน้าเว็บ ดังนั้นหากแก้ Sheet แล้ว ให้รอ Google อัปเดตแคชประมาณ 5 นาที

### 2. การจัดการหน้าเว็บ (Frontend & UI Stability)
- **ระบบ Transition & Preloader:** ห้ามลบหรือแก้ไข Logic ของ `#preloader` และ `initPageTransitions()` ใน `index.js` เพราะมันทำหน้าที่สร้างความสมูทในการเปลี่ยนหน้า (Cinematic Fade)
- **การเพิ่มหน้าใหม่ (New Pages):** หากสร้างไฟล์ `.html` ใหม่ ต้องลิงก์ไฟล์ `assets/css/index.css` และ `assets/js/index.js` เสมอ เพื่อให้แถบ Nav, Preloader และ Grid system ทำงานต่อเนื่อง
- **ฟอนต์และ Typography:** ระบบใช้ฟอนต์ไทย `IBM Plex Sans Thai` สลับกับ `Space Grotesk` ห้ามลบ Class `.lang-th` เพราะมี CSS ป้องกันปัญหา "สระลอย" (Diacritic clipping) จัดการไว้อยู่

### 3. การใช้ Script ภายใน (Scripts & Automation)
- หากมี Script อย่าง `run_extractor.command` หรือ `.py` ในโฟลเดอร์ ให้ทราบว่ามันคือเครื่องมือสำหรับ Export/Backup ข้อมูล (Local Processing) แต่ตัวเว็บ **Production** จะวิ่งตรงไปหา Google Sheets เสมอ

---
*บันทึกโดย: Phu Thongyan +66 62 635 5629
