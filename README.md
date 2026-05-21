# 🏛️ Thai Symbol Pattern Lab (TSPL) - Digital Archive Project

**TSPL (Thai Symbol Pattern Lab)** คือ โครงการระบบบริหารจัดการและจัดเก็บมรดกทางวัฒนธรรมลายไทยดิจิทัล (Digital Archive) ซึ่งรวบรวมลวดลายสถาปัตยกรรมและศิลปกรรมไทยจำนวน 180 รายการ เพื่อการถอดรหัสอัตลักษณ์ สกัดรอยมรดกไทย และแปลงให้อยู่ในรูปแบบของ "สินทรัพย์ดิจิทัล" (Digital Assets) ที่พร้อมใช้งาน

## 📌 จุดประสงค์หลักของระบบ (Core Objectives)
1. **เก็บรวบรวมและจัดหมวดหมู่ (Taxonomy & Archiving):** รวบรวมลวดลายจากหลักฐานชั้นต้น (ล้านนา, อยุธยา ฯลฯ) และจัดระบบข้อมูลทางสัญวิทยา
2. **วิเคราะห์เชิงโครงสร้าง (Structural Analysis):** แยกองค์ประกอบของลายออกเป็น "หน่วยคำทัศน์" (Visual Morphemes) เพื่อให้ง่ายต่อความเข้าใจและการนำไปประยุกต์ใช้
3. **ความพร้อมในการใช้งาน (Vector Readiness):** ให้บริการไฟล์ภาพลวดลายในรูปแบบเวกเตอร์ (SVG) สำหรับการต่อยอดใน Creative Economy
4. **ความตระหนักรู้ด้านจริยธรรม (Cultural Ethics):** ระบุระดับความเหมาะสมในการนำไปใช้งาน (เช่น ลายทั่วไป, ลายพิธีกรรม, ลายศักดิ์สิทธิ์) และข้อควรระวัง (Protocol)

## ⚙️ สถาปัตยกรรมระบบ (System Architecture)
- **Frontend / UI:** พัฒนาด้วย HTML, CSS และ Vanilla JavaScript เน้นดีไซน์พรีเมียมแบบ Cinematic / Technical Interface
- **Database:** ใช้ Google Sheets เป็น Headless CMS / Database (ดึงข้อมูลผ่าน CSV ให้อัปเดตแบบ Real-time)
- **Data Attributes:** ระดับความน่าเชื่อถือของลาย (Verified, Reconstructed, Fragment, Hypothetical), สถานที่พบ และบริบทแวดล้อม

---

## 📌 มาตรฐานหมวดหมู่ (Master Categories)
ระบบได้แบ่งหมวดหมู่ลวดลายออกเป็น 4 กลุ่มหลัก:
1.  **Nature & Botany** (พรรณพฤกษาและธรรมชาติ) - รหัสย่อ: `NAT`
2.  **Fauna & Mythical** (สรรพสัตว์และสัตว์หิมพานต์) - รหัสย่อ: `FAU`
3.  **Geometric & Synthetic** (เรขาคณิตและลวดลายประดิษฐ์) - รหัสย่อ: `GEO`
4.  **Sacred & Belief** (สัญลักษณ์ความเชื่อและสิ่งศักดิ์สิทธิ์) - รหัสย่อ: `SAC`

---

## ⚡ วิธีการอัปเดตข้อมูลแบบใหม่ (New Workflow)

### 🟢 TSPL Control Center
ศูนย์บัญชาการหลักสำหรับจัดการทุกอย่างในที่เดียว:
- **Launcher:** ดับเบิลคลิก `TSPL_CONTROL_CENTER.command` ในโฟลเดอร์หลัก
- **URL:** [http://localhost:5556](http://localhost:5556)

### ขั้นตอนการทำงาน:
1. **สแกนข้อมูล (Haiku Scan):** ใน Dashboard กดปุ่ม **RUN** เพื่อให้ AI อ่านเอกสารจาก Drive ลงชีต `Haiku_Scan_Master` อัตโนมัติ (ระบบจะสแกนเฉพาะไฟล์ใหม่)
2. **จัดการรูปภาพ (Assets):** 
   - กดปุ่ม **SYNC** (Link Assets) เพื่อจับคู่รูปกับฐานข้อมูล
   - กดปุ่ม **OPT** (Optimize) เพื่อบีบอัดรูปภาพ (ไฟล์ PNG จะขึ้นตัวหนังสือสีเหลืองเตือนใน Console)
3. **สำรองข้อมูล (Backup):** กดปุ่ม **SAVE** เพื่อเซฟข้อมูลจาก Google Sheets ลงเครื่อง (Local JSON)
4. **อัปเดตเว็บ (Deploy):** กดปุ่ม **LIVE** เพื่อส่งข้อมูลและรูปภาพทั้งหมดขึ้น Vercel

---

## 📂 การจัดเก็บไฟล์ (Asset Organization)
ทุกลวดลายจะมีโฟลเดอร์รหัสส่วนตัวอยู่ใน `assets/images/database/` แยกตามหมวดหมู่:
```text
/assets/images/database/[Category_Folder]/[Pattern-ID]/
├── main.jpg        # รูปภาพหลัก
├── context.jpg     # รูปภาพบริบท
├── detail.jpg      # รูปภาพซูมรายละเอียด
└── vectors/
    └── vector.svg  # ไฟล์เวกเตอร์
```

---

## 🛡️ กฎการพัฒนา (Stability Guidelines)
- **ห้ามเปลี่ยนชื่อคอลัมน์ใน Google Sheets:** เพราะโค้ดผูกกับชื่อคอลัมน์อย่างตายตัว
- **เครื่องหมายแบ่งข้อมูล:** Morphemes ใช้ `|` และ Tags ใช้ `,` เสมอ
- **Console Interface:** ระบบ Console จะใช้สีเขียว Technical และเน้นสีเหลืองสำหรับไฟล์ PNG เพื่อให้ง่ายต่อการตรวจสอบ

---
*บันทึกโดย: Phu Thongyan +66 62 635 5629 | อัปเดตล่าสุด: 17 พฤษภาคม 2026*
