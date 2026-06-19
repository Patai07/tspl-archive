# 🏛️ คู่มือแนวคิดการส่งต่อโครงการ TSPL (TSPL Handover & Integration Ideas)

เอกสารฉบับนี้รวบรวมไอเดียและแนวทางในการ**รวมระบบหน้าบ้าน (Frontend) และหลังบ้าน (Backend/Python Scripts)** เข้าด้วยกัน เพื่อให้ทีมพัฒนาชุดถัดไปสามารถทำงานต่อได้ง่าย และช่วยให้ลูกค้า (คุณพี่กบ) สามารถบริหารจัดการข้อมูลภาพและฐานข้อมูลได้ด้วยตัวเองโดยไม่ต้องติดตั้ง Python หรือรันสคริปต์ในเครื่องส่วนตัว (Zero Local Setup)

---

## 1. โครงสร้างปัจจุบัน (Current Architecture) และข้อจำกัดในการส่งต่อ

ปัจจุบันระบบถูกแยกออกเป็น 2 ส่วนหลัก:
1. **Frontend (หน้าบ้าน)**: เว็บไซต์ static (HTML/CSS/Vanilla JS) โฮสต์อยู่บน **Vercel** ดึงข้อมูลลวดลายจากไฟล์ `models_list.json` และดึงไฟล์ภาพจาก `assets/images/database/` ซึ่งอยู่ใน Git Repository
2. **Backend/Admin (หลังบ้าน)**: รันอยู่ในเครื่องส่วนตัว (Local Machine) ผ่านสคริปต์ Python ในโฟลเดอร์ `tools_web/` และมีระบบ Control Center (`dashboard.py`) ที่เปิดใช้งานผ่านการดับเบิลคลิกไฟล์ `.command` บน macOS เพื่อเชื่อมโยงระหว่าง Google Sheet + Google Drive และดึงไฟล์ภาพลงเครื่องเพื่อแปลงขนาดและประมวลผล ก่อนจะรัน Git Commit & Push ขึ้น GitHub เพื่อส่งต่อให้ Vercel โหลดไปใช้

### ⚠️ ความท้าทายในการส่งต่อให้ลูกค้าหรือทีมอื่น:
* **ต้องพึ่งพา Local Environment**: ลูกค้าต้องติดตั้ง Python, Git, และต้องเปิด Terminal หรือรันไฟล์ `.command` ในเครื่องของตัวเอง
* **ความเสี่ยงเรื่องพื้นที่และการ Deploy**: การเพิ่มไฟล์รูปภาพความละเอียดสูงเข้าไปใน Git Repository จะทำให้โฟลเดอร์โครงการมีขนาดใหญ่ขึ้นเรื่อยๆ จนอาจเกิดปัญหาขีดจำกัดของ Vercel หรือ Git ได้ในระยะยาว
* **ความเข้ากันได้ของระบบปฏิบัติการ**: ไฟล์ `.command` ออกแบบมาสำหรับ macOS หากทีมใหม่หรือลูกค้าใช้ Windows จะไม่สามารถกดรันได้ทันที ต้องปรับสคริปต์เป็น `.bat` หรือรันผ่าน PowerShell

---

## 2. ข้อเสนอ 3 แนวทางในการรวมระบบเพื่อส่งต่อ (Integration Scenarios)

เพื่อให้ระบบใช้งานง่ายที่สุดสำหรับลูกค้าและผู้พัฒนาต่อ มีแนวทางการปรับปรุงระบบดังนี้:

```mermaid
graph TD
    subgraph Option A: Modern Cloud-Native (แนะนำที่สุด)
        A1[Google Sheets & Drive] -->|Sync| A2[Web Admin Panel ใน Next.js]
        A2 -->|อัปโหลดรูปภาพ| A3[Cloud Storage เช่น Cloudflare R2 / AWS S3]
        A2 -->|บันทึก JSON/DB| A4[Database หรือ Serverless Cache]
        A3 -->|โหลดภาพ| A5[หน้าเว็บหลัก Next.js / Astro]
        A4 -->|โหลดข้อมูล| A5
    end
```

---

### แนวทางที่ A: ระบบ Web-App แบบ Cloud-Native (Next.js/Astro + Serverless Backend) 🌟 [แนะนำที่สุด]
ย้ายโค้ดทั้งหมด (ทั้งหน้าบ้านและหลังบ้าน) ไปเป็น Web Application ยุคใหม่ โดยเปลี่ยนหน้าเว็บ Static HTML เป็น Next.js หรือ Astro และรันระบบหลังบ้านเป็น Serverless API

* **วิธีการทำงาน**:
  1. พัฒนาหน้า **Admin Dashboard** เป็นหน้าเว็บเพจหนึ่งของเว็บไซต์ (ล็อกอินผ่านรหัสผ่านส่วนตัวหรือ Google Auth)
  2. เมื่อลูกค้าคลิกปุ่ม **"Sync Data & Optimize Images"** บนหน้าเว็บ:
     - ระบบ Serverless API ใน Next.js (Node.js หรือเรียกสคริปต์ Python บนคลาวด์) จะดาวน์โหลดภาพจาก Google Drive แปลงขนาด (Optimize) อัตโนมัติในหน่วยความจำชั่วคราว
     - บันทึกภาพที่ Optimize แล้วไปไว้บน **Cloud Storage** เช่น **Cloudflare R2** หรือ **AWS S3** (ค่าใช้จ่ายต่ำมากหรือฟรีสำหรับขนาดนี้) แทนที่จะเก็บไว้ใน Git
     - บันทึกข้อมูล JSON ลงใน Firebase/Supabase หรือเก็บเป็นไฟล์ใน Cloud Storage
  3. หน้าเว็บหลัก (Frontend) จะดึงข้อมูลและรูปภาพจาก Cloud Storage โดยตรง
* **ข้อดีสำหรับลูกค้า**:
  * **ไม่ต้องติดตั้งอะไรเลย**: จัดการทุกอย่างผ่านเว็บบราวเซอร์บนมือถือหรือคอมพิวเตอร์เครื่องไหนก็ได้
  * **ไม่ต้องกด Deploy**: ข้อมูลอัปเดตแบบ Real-time หรือภายในไม่กี่วินาทีหลังจากกด Sync บนเว็บ
* **ข้อดีสำหรับทีมพัฒนาต่อ**:
  * ใช้ Stack มาตรฐานระดับสากล (React/Next.js/Typescript) ดูแลง่าย ปลอดภัย มีเอกสารคู่มือพร้อมใช้งานในสากล

---

### แนวทางที่ B: การรวมระบบด้วย Docker Container (Docker Compose Stack)
จัดกลุ่มสคริปต์ Python (Flask Control Center) และหน้าเว็บ Static (รันผ่าน Nginx) ให้อยู่ใน Container เดียวกัน

* **วิธีการทำงาน**:
  1. เขียนไฟล์ `Dockerfile` และ `docker-compose.yml` เพื่อแพ็ครวม Flask App (`dashboard.py`) และ Static Web Server เข้าด้วยกัน
  2. ผู้ใช้หรือลูกค้าสามารถเอาไปรันบน Server ส่วนตัว (Local Server), Cloud VM (เช่น AWS EC2, DigitalOcean, Google Cloud) หรือแม้กระทั่งรันในเครื่องส่วนตัวโดยใช้โปรแกรม Docker Desktop
* **ข้อดีสำหรับลูกค้า**:
  * รันคำสั่งเดียว (`docker-compose up -d`) ระบบก็พร้อมทำงานได้ทันทีทั้งหน้าบ้านและหลังบ้านบนทุก OS (Windows/macOS/Linux)
* **ข้อดีสำหรับทีมพัฒนาต่อ**:
  * ขจัดปัญหาเรื่อง Dependency/Python Version ไม่ตรงกันอย่างเด็ดขาด เพราะทุกอย่างถูกควบคุมไว้ใน Container แล้ว

---

### แนวทางที่ C: ย้าย Control Center ไปที่ Streamlit Cloud + Vercel Webhook
แยกส่วนจัดการฐานข้อมูลไปไว้บนระบบคลาวด์ฟรีสำหรับ Python และใช้ Webhook ในการสั่งอัปเดตหน้าเว็บ

* **วิธีการทำงาน**:
  1. แปลงหน้าจอ Control Center ปัจจุบัน (`tools_web/dashboard.py` ซึ่งเป็น Flask) ให้เป็นแอป **Streamlit** (เป็น Python Web Framework ที่เขียนง่ายมาก)
  2. โฮสต์ Streamlit แอปนี้ไว้บน **Streamlit Community Cloud** (ฟรี) เพื่อเป็นห้องควบคุมหลังบ้านออนไลน์ให้ลูกค้าใช้งาน
  3. เมื่อลูกค้ากดปุ่มประมวลผลบน Streamlit Cloud:
     - สคริปต์จะดาวน์โหลดรูป แปลงรูป และเก็บไว้ใน Google Drive หรือ Cloud Storage
     - ส่งสัญญาณ (Deploy Hook) ไปยัง Vercel เพื่อสั่งให้หน้าเว็บหลักดึงข้อมูลไปแสดงผลใหม่
* **ข้อดีสำหรับลูกค้า**:
  * หน้าจอควบคุมอยู่บนเว็บออนไลน์ ไม่เสียค่าโฮสติ้ง และไม่ต้องเปิดคอมพิวเตอร์ทิ้งไว้เพื่อรันสคริปต์
* **ข้อดีสำหรับทีมพัฒนาต่อ**:
  * ทีมพัฒนาต่อไม่ต้องเขียน Frontend สำหรับ Admin ใหม่ทั้งหมด สามารถใช้ Python เขียน UI ของ Streamlit ได้โดยตรง

---

## 3. ขั้นตอนการเตรียมข้อมูลและทรัพยากรเพื่อส่งต่องาน (Handover Checklist)

หากจะเริ่มส่งต่องานให้ทีมอื่น ควรเตรียมสิ่งเหล่านี้ไว้ในที่เดียวกัน:

### 1. ข้อมูลสิทธิ์การเข้าถึง (Credentials & APIs)
* **Google Service Account (`service-account.json`)**: ไฟล์ JSON คีย์หลักที่ใช้เชื่อมต่อ Google Sheets และ Google Drive
* **Claude API Key / Anthropic Key**: คีย์สำหรับเรียกใช้งาน AI ในการสกัดวิเคราะห์ลวดลายวัฒนธรรม
* **GitHub Repository Access**: ลิงก์สำหรับให้ทีมใหม่โคลนโค้ดและส่งงานต่อ
* **Vercel Account / Webhook**: สำหรับจัดการโดเมนเนมและการตั้งค่า Deployment ของหน้าบ้าน

### 2. คู่มือข้อมูลการเชื่อมโยง (Data References)
* **Master Spreadsheet ID**: `1iJIr2vT3WeyavBi4_sw3In04yNNHF-GNbJ8zf8egdHs`
* **Google Drive Asset Root ID**: โฟลเดอร์ต้นทางของภาพและเอกสารทั้งหมด
* **Schema Definition**: โครงสร้างคอลัมน์ของ Google Sheet (โดยอ้างอิงเอกสาร `DATA_FLOW.md`)

### 3. คำอธิบายเครื่องมือชุดปัจจุบัน (Current Maintenance Tools)
* สคริปต์หลักที่อยู่ภายใต้ `tools_web/`:
  * `asset_manager.py`: เครื่องมือหลักในการ Map ID ลาย, ดึงลิงก์โฟลเดอร์ และดาวน์โหลดรูปภาพจาก Drive
  * `semiotic_extractor.py`: ระบบอ่านไฟล์คำอธิบายลวดลายแล้วนำเข้า Claude AI เพื่อแปลงโครงสร้างข้อมูลลง Haiku Sheet
  * `db_mirror.py`: เครื่องมือเทียบความถูกต้องและซิงก์ข้อมูลระหว่างชีต 1 (Staging) และชีต 2 (Production)
  * `optimize_images.py`: ปรับขนาดรูปภาพให้อยู่ในมาตรฐานเว็บที่โหลดเร็ว

---

### 📝 คำแนะนำสำหรับการตัดสินใจก้าวต่อไป
หากต้องการความง่ายที่สุดในการประมวลผลและการดูแลรักษาระยะยาว **"แนวทางที่ A (Next.js/Astro + Cloud Storage)"** ถือเป็นทิศทางที่ดีที่สุดสำหรับระบบมรดกวัฒนธรรมนี้ เนื่องจากข้อมูลภาพมีขนาดใหญ่ขึ้นเรื่อยๆ การนำภาพออกจาก Git Repository ไปไว้บน Cloud Storage จะช่วยให้เว็บไซต์โหลดได้เร็วขึ้นอย่างมาก และทีมพัฒนาชุดใหม่สามารถขยายฟังก์ชันการทำงาน เช่น การค้นหารูปภาพเชิงลึก (Image Search) หรือการทำ AI Chat ได้ง่ายยิ่งขึ้น
