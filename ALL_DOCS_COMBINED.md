# Documentation Index

| File | Purpose guessed from content | Notes |
|---|---|---|
| README.md | Project overview, system architecture, workflow guide, and development stability guidelines | Root-level project doc |
| CI/CI_Guidelines.md | Corporate Identity guidelines — fonts, colors, logos, icons, motion rules, and responsive layout strategy | Links to Graphics_Toolkit.md for full token details |
| CI/Graphics_Toolkit.md | Design token reference — full color palette, typography scale, spacing, grid system, UI components, animation rules, and technical SVG assets | Single source of truth for design tokens |
| CI/tspl-icons-sprite.md | SVG icon sprite usage guide and full index of all 91 icons in the TSPL icon set | References icons stored in CI/icons/ |
| pipeline_line/README.md | LINE image archive pipeline — step-by-step usage, file descriptions, API cost estimates, and output format | Updated พ.ค. 2569 |
| tools_debug/README.md | Debug scripts reference — purpose of each debug tool and when to use them | Not part of main pipeline — diagnostic use only |
| tools_web/README.md | Web tools and database management scripts — deploy, clear sheet, extractor, mirror, optimizer descriptions and warnings | Updated พ.ค. 2569 |

===== FILE: README.md =====

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

===== FILE: CI/CI_Guidelines.md =====

# TSPL (Thai Symbol Pattern Lab) - Corporate Identity (CI)

## 1. Fonts (Typography)
The following fonts are used across the website:
- **IBM Plex Sans Thai** (Primary Thai font)
- **Noto Sans Thai** (Secondary Thai font)
- **Space Grotesk** (Primary English/Number font)
- **Cutive Mono** (Special Use font for Sila Jaruek pattern, ancient scripts, and technical data)

## 2. Color Palette (Color Codes)

### Primary Colors
- **TSPL Gold / Accent Red:** `#FF4E45` (Used for primary accents, buttons, and highlights)
- **TSPL Blue / Dark Navy:** `#0F172A` (Used for primary text, backgrounds, and deep elements)

### Secondary & Accent Colors
- **Heritage Gold:** `#D4AF37` (Used for special typography and ancient script themes)
- **Dark Navy Variant:** `#0F2C59` (Used for borders and deep backgrounds)

### Backgrounds & Neutrals
- **Main Background:** `#FCFCFC`
- **Apple UI Background:** `#FBFBFD`
- **Blueprint Grid Light:** `#F8FAFC`
- **Blueprint Grid Dark:** `#060F22`
- **Preloader Gradient:** `#010509` to `#040C1A` to `#060F20`

### Greyscale / UI Elements
- **White:** `#FFFFFF`
- **Light Greys:** `#F1F1F1`, `#E5E7EB`, `#F3F4F6`, `#F9FAFB`, `#EEEEEE`
- **Dark Greys:** `#1A1A1A`, `#9CA3AF`

## 3. Logos & Images
Standalone assets and brand images are organized in the following directories:

### Logos (`CI/logos/`)
- `กศร.svg`: The primary vector logo (Thai Symbol Pattern Lab).
- `nu_logo.png`: Associated institutional logo (Naresuan University).

### Key Images (`CI/images/`)
- `Profile_Pic.jpg`: Primary profile or project lead imagery.

## 4. Fonts (Typography)
We have provided two types of font files:

### 1. Web Fonts (`CI/fonts/*.woff2`)
These are high-performance files used specifically for the website.

### 2. Desktop Fonts (`CI/fonts/TTF_for_PC_Mac/*.ttf`)
These are **TrueType Fonts (TTF)** intended for installation on your computer. Use these for:
- **Graphic Design:** Canva, Photoshop, Illustrator, Figma.
- **Documents:** Microsoft Word, PowerPoint, Keynote.

**How to Install:**
1. Open the folder `CI/fonts/TTF_for_PC_Mac/`.
2. Select all `.ttf` files.
3. **On Mac:** Right-click and select "Open" (or double-click) and click **"Install Font"**.
4. **On Windows:** Right-click and select **"Install"**.

- **IBM Plex Sans Thai**: Primary Thai font.
- **Noto Sans Thai**: Secondary Thai font.
- **Space Grotesk**: Primary English/Number font.

## 5. Icons (Iconography)
While the website uses the **[Phosphor Icons](https://phosphoricons.com/)** library via a web CDN for convenience, all specific SVG icon files used (and recommended) have been saved locally in the `CI/icons/` directory.

### Icon Styles
- **Regular/Line**: Default style.
- **Bold**: High-emphasis style.
- **Fill**: Solid/filled style.

### Extended Icon Library
Included icons for future expansion:
- **Lab & Analysis**: `flask`, `database`, `microscope`, `chart-pie`
- **Heritage & Symbols**: `flower-lotus`, `sparkle`
- **Actions & Sharing**: `download-simple`, `share-network`
- **Social Media**: `facebook-logo`, `instagram-logo`

## 6. Motion & Interaction Strategy
To maintain the "High-Tech / Archival" feel, use the following animation rules:
- **Hover Transitions:** Use `0.3s` with an `Ease-out` curve for buttons and cards.
- **Page Transitions:** Use `0.5s` `Ease-in-out` for a smooth, editorial fade.
- **Cinematic Pulse:** Use `1.2s` `Linear` loops for scanning lines or radar effects.
- **Feedback:** Use `0.6s` `Ease-out` for glowing status indicators.

## 7. Visual Hierarchy & Opacity
Control the depth of the interface by strictly following these opacity rules:
- **Background Layer (Blueprint):** Maintain at **5%** opacity. It should be felt, not read.
- **Overlay Layer (Scan Lines):** Use **10-20%** opacity with "Screen" blending.
- **Focus Layer (Frames/Data):** Use **80-100%** opacity for current research data.
- **Ambient Layer (Particles):** Keep at **20%** to avoid visual noise.

## 8. Responsive Layout Strategy
Always design with these grid tokens in mind:
- **Desktop (12 Columns):** 80px margin, 24px gutter.
- **Tablet (8 Columns):** 40px margin, 20px gutter.
- **Mobile (4 Columns):** 24px margin, 16px gutter.

---
*For a complete list of specific hex codes, font sizes, and spacing values, please refer to the [Graphics Toolkit](Graphics_Toolkit.md).*

===== FILE: CI/Graphics_Toolkit.md =====

# TSPL Graphics Toolkit & Design Tokens

This document serves as the single source of truth for all design tokens, technical assets, and color profiles for the Thai Symbol Pattern Lab (TSPL) project.

---

## 1. Color System (Total Palette)
| Category | Name | HEX | RGB | CMYK | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary** | TSPL Red | `#FF4E45` | `255, 78, 69` | `0, 69, 73, 0` | CTA, Highlight, Core Identity |
| **Primary** | TSPL Navy | `#0F172A` | `15, 23, 42` | `64, 45, 0, 84` | Main Background, Primary Text |
| **Secondary**| Heritage Gold| `#D4AF37` | `212, 175, 55` | `0, 17, 74, 17` | Heritage Accents, Symbols |
| **Secondary**| Dark Navy Var| `#0F2C59` | `15, 44, 89` | `83, 51, 0, 65` | Borders, Depth, UI Layers |
| **Neutral** | White | `#FFFFFF` | `255, 255, 255`| `0, 0, 0, 0` | Main Text (Dark Mode), BG |
| **Neutral** | Light Grey | `#F1F1F1` | `241, 241, 241`| `0, 0, 0, 5` | UI Backgrounds |
| **Neutral** | Mid Grey | `#E5E7EB` | `229, 231, 235`| `3, 2, 0, 8` | Dividers, Secondary Borders |
| **Neutral** | Dark Grey | `#1A1A1A` | `26, 26, 26` | `0, 0, 0, 90` | Text Secondary |
| **System** | Blueprint Blue| `#4D8EFF` | `77, 142, 255` | `70, 44, 0, 0` | Grid Lines, Tech Elements |
| **Background**| Main BG | `#FCFCFC` | `252, 252, 252`| `0, 0, 0, 1` | Main Paper Background |

---

## 2. Typography Scale
| Type | Font Family | Weight | Size (px) | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1** | Space Grotesk | Bold | 64 | 72 | Hero Titles |
| **H2** | Space Grotesk | SemiBold| 40 | 48 | Section Titles |
| **H3** | IBM Plex Sans Thai| Medium | 28 | 36 | Sub Titles |
| **Body L**| IBM Plex Sans Thai| Regular | 18 | 28 | Main Content |
| **Body M**| IBM Plex Sans Thai| Regular | 16 | 24 | Standard Content |
| **Body S**| Noto Sans Thai | Regular | 14 | 22 | Long Text / Descriptions |
| **Caption**| Noto Sans Thai | Regular | 12 | 18 | Small Text / Metadata |
| **Mono** | Cutive Mono / Space | Regular | 12 | 16 | Data Points / Loading Labels |

---

## 3. Spacing & Layout
### Spacing Tokens
| Token | Value | Usage |
| :--- | :--- | :--- |
| **XS** | 8px | Micro spacing, icon labels |
| **S** | 16px | Small gaps, item internal padding |
| **M** | 24px | Default spacing, component gaps |
| **L** | 32px | Section inner padding |
| **XL** | 64px | Section gaps, major vertical rhythm |
| **XXL**| 96px | Large separation between modules |

### Grid System
| Device | Columns | Margin | Gutter | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Desktop**| 12 | 80px | 24px | Main layout for research portal |
| **Tablet** | 8 | 40px | 20px | Responsive tablet view |
| **Mobile** | 4 | 24px | 16px | Compact mobile layout |

---

## 4. UI Components & Elements
### Icon Styles
| Style | Weight | Size (px) | Color | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Default** | Regular | 24 | `#0F172A` | Normal UI Interaction |
| **Active** | Bold | 24 | `#FF4E45` | Active Navigation / CTA |
| **Highlight**| Fill | 24 | `#FF4E45` | Critical Alerts / Important |
| **Disabled** | Regular | 24 | `#9CA3AF` | Inactive states |
| **Large** | Regular | 32 | `#0F172A` | Hero section icons |
| **Small** | Regular | 16 | `#0F172A` | Inline with text |

### Component Definitions
| Component | Variant | Background | Border | Text Color | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Button** | Primary | `#FF4E45` | None | `#FFFFFF` | Main Call to Action |
| **Button** | Secondary | Transparent | `#0F172A` | `#0F172A` | Outline / Secondary Action |
| **Button** | Ghost | Transparent | None | `#0F172A` | Low emphasis actions |
| **Card** | Default | `#FFFFFF` | `#E5E7EB` | `#0F172A` | Standard content blocks |
| **Card** | Dark | `#0F172A` | None | `#FFFFFF` | Highlighted cards |
| **Divider** | Default | `#E5E7EB` | None | - | Visual separation |

---

## 5. Motion & Visual Rules
### Animation Durations
- **Hover Effects:** `0.3s` (Ease-out)
- **Page Transitions:** `0.5s` (Ease-in-out)
- **Scan Line Pulse:** `1.2s` (Linear)
- **Glow Animation:** `0.6s` (Ease-out)

### Opacity & Hierarchy
- **Blueprint Grid:** `5%` opacity (Background layer)
- **Scan Line:** `10-20%` opacity (Hero / Symbols)
- **Technical Frame:** `100%` opacity (CTA / Focus)
- **Data Points:** `80%` opacity (1-3 points per layout max)
- **Particles:** `20%` opacity (Ambient background)

---

## 6. Technical Assets (SVG)
### Blueprint Grid
```xml
<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'>
  <g stroke='#4D8EFF' stroke-width='0.7' opacity='0.05'>
    <line x1='-4' y1='0' x2='4' y2='0'/>
    <line x1='0' y1='-4' x2='0' y2='4'/>
  </g>
</svg>
```

### Cinematic Effects
Assets are available in `CI/patterns/scan_effects.svg`.
- **Scan Beam:** Set to **"Screen"** or **"Linear Dodge (Add)"** in design software.
- **Flash Flare:** Set to **"Linear Dodge (Add)"**.

===== FILE: CI/tspl-icons-sprite.md =====

# TSPL Icon Sprite Sheet

## ใช้งาน

วาง SVG sprite นี้ไว้ในหน้าเว็บของคุณ แล้วเรียกใช้ icon ด้วย:

```html
<svg width="24" height="24" fill="currentColor">
  <use href="/CI/tspl-icons-sprite.svg#arrow-right"/>
</svg>
```

หรือกำหนดสีและขนาดตามต้องการ:

```html
<svg width="32" height="32" fill="#3B82F6">
  <use href="/CI/tspl-icons-sprite.svg#flask-bold"/>
</svg>
```

## รายชื่อ Icons ทั้งหมด (91 icons)

| Icon | ชื่อ |
|------|------|
| ![arrow-right-bold](icons/arrow-right-bold.svg) | `arrow-right-bold` |
| ![arrow-right](icons/arrow-right.svg) | `arrow-right` |
| ![arrow-up-bold](icons/arrow-up-bold.svg) | `arrow-up-bold` |
| ![arrow-up-right-bold](icons/arrow-up-right-bold.svg) | `arrow-up-right-bold` |
| ![arrow-up-right](icons/arrow-up-right.svg) | `arrow-up-right` |
| ![article-bold](icons/article-bold.svg) | `article-bold` |
| ![article-fill](icons/article-fill.svg) | `article-fill` |
| ![article](icons/article.svg) | `article` |
| ![bezier-curve-bold](icons/bezier-curve-bold.svg) | `bezier-curve-bold` |
| ![bezier-curve](icons/bezier-curve.svg) | `bezier-curve` |
| ![book-open-fill](icons/book-open-fill.svg) | `book-open-fill` |
| ![books-fill](icons/books-fill.svg) | `books-fill` |
| ![books](icons/books.svg) | `books` |
| ![camera-bold](icons/camera-bold.svg) | `camera-bold` |
| ![camera](icons/camera.svg) | `camera` |
| ![caret-down-bold](icons/caret-down-bold.svg) | `caret-down-bold` |
| ![caret-down](icons/caret-down.svg) | `caret-down` |
| ![caret-left-bold](icons/caret-left-bold.svg) | `caret-left-bold` |
| ![caret-right-bold](icons/caret-right-bold.svg) | `caret-right-bold` |
| ![caret-right](icons/caret-right.svg) | `caret-right` |
| ![chart-pie-bold](icons/chart-pie-bold.svg) | `chart-pie-bold` |
| ![chart-pie-fill](icons/chart-pie-fill.svg) | `chart-pie-fill` |
| ![chart-pie](icons/chart-pie.svg) | `chart-pie` |
| ![check-circle-fill](icons/check-circle-fill.svg) | `check-circle-fill` |
| ![clock-countdown-fill](icons/clock-countdown-fill.svg) | `clock-countdown-fill` |
| ![clock-countdown](icons/clock-countdown.svg) | `clock-countdown` |
| ![cloud-arrow-up-fill](icons/cloud-arrow-up-fill.svg) | `cloud-arrow-up-fill` |
| ![cloud-arrow-up](icons/cloud-arrow-up.svg) | `cloud-arrow-up` |
| ![database-bold](icons/database-bold.svg) | `database-bold` |
| ![database-fill](icons/database-fill.svg) | `database-fill` |
| ![database](icons/database.svg) | `database` |
| ![download-simple-bold](icons/download-simple-bold.svg) | `download-simple-bold` |
| ![download-simple](icons/download-simple.svg) | `download-simple` |
| ![envelope-simple-fill](icons/envelope-simple-fill.svg) | `envelope-simple-fill` |
| ![facebook-logo-fill](icons/facebook-logo-fill.svg) | `facebook-logo-fill` |
| ![facebook-logo](icons/facebook-logo.svg) | `facebook-logo` |
| ![faders-horizontal-bold](icons/faders-horizontal-bold.svg) | `faders-horizontal-bold` |
| ![faders-horizontal](icons/faders-horizontal.svg) | `faders-horizontal` |
| ![fingerprint-bold](icons/fingerprint-bold.svg) | `fingerprint-bold` |
| ![fingerprint-fill](icons/fingerprint-fill.svg) | `fingerprint-fill` |
| ![fingerprint](icons/fingerprint.svg) | `fingerprint` |
| ![flask-bold](icons/flask-bold.svg) | `flask-bold` |
| ![flask-fill](icons/flask-fill.svg) | `flask-fill` |
| ![flask](icons/flask.svg) | `flask` |
| ![flower-lotus-bold](icons/flower-lotus-bold.svg) | `flower-lotus-bold` |
| ![flower-lotus](icons/flower-lotus.svg) | `flower-lotus` |
| ![globe-fill](icons/globe-fill.svg) | `globe-fill` |
| ![globe-hemisphere-east-bold](icons/globe-hemisphere-east-bold.svg) | `globe-hemisphere-east-bold` |
| ![globe-hemisphere-east](icons/globe-hemisphere-east.svg) | `globe-hemisphere-east` |
| ![identification-badge-fill](icons/identification-badge-fill.svg) | `identification-badge-fill` |
| ![info-fill](icons/info-fill.svg) | `info-fill` |
| ![info](icons/info.svg) | `info` |
| ![instagram-logo-fill](icons/instagram-logo-fill.svg) | `instagram-logo-fill` |
| ![instagram-logo](icons/instagram-logo.svg) | `instagram-logo` |
| ![intersect-bold](icons/intersect-bold.svg) | `intersect-bold` |
| ![intersect-three-bold](icons/intersect-three-bold.svg) | `intersect-three-bold` |
| ![intersect-three-fill](icons/intersect-three-fill.svg) | `intersect-three-fill` |
| ![intersect-three](icons/intersect-three.svg) | `intersect-three` |
| ![leaf-bold](icons/leaf-bold.svg) | `leaf-bold` |
| ![list-bold](icons/list-bold.svg) | `list-bold` |
| ![list](icons/list.svg) | `list` |
| ![magnifying-glass-fill](icons/magnifying-glass-fill.svg) | `magnifying-glass-fill` |
| ![map-pin-fill](icons/map-pin-fill.svg) | `map-pin-fill` |
| ![microscope-bold](icons/microscope-bold.svg) | `microscope-bold` |
| ![microscope-fill](icons/microscope-fill.svg) | `microscope-fill` |
| ![microscope](icons/microscope.svg) | `microscope` |
| ![paint-brush-bold](icons/paint-brush-bold.svg) | `paint-brush-bold` |
| ![palette-bold](icons/palette-bold.svg) | `palette-bold` |
| ![pencil-line-bold](icons/pencil-line-bold.svg) | `pencil-line-bold` |
| ![prohibit-fill](icons/prohibit-fill.svg) | `prohibit-fill` |
| ![prohibit](icons/prohibit.svg) | `prohibit` |
| ![scroll-bold](icons/scroll-bold.svg) | `scroll-bold` |
| ![scroll-fill](icons/scroll-fill.svg) | `scroll-fill` |
| ![scroll](icons/scroll.svg) | `scroll` |
| ![seal-check-fill](icons/seal-check-fill.svg) | `seal-check-fill` |
| ![seal-check](icons/seal-check.svg) | `seal-check` |
| ![selection-all-bold](icons/selection-all-bold.svg) | `selection-all-bold` |
| ![selection-all](icons/selection-all.svg) | `selection-all` |
| ![share-network-bold](icons/share-network-bold.svg) | `share-network-bold` |
| ![share-network](icons/share-network.svg) | `share-network` |
| ![shield-check-bold](icons/shield-check-bold.svg) | `shield-check-bold` |
| ![sketch-logo](icons/sketch-logo.svg) | `sketch-logo` |
| ![sparkle-bold](icons/sparkle-bold.svg) | `sparkle-bold` |
| ![sparkle](icons/sparkle.svg) | `sparkle` |
| ![stack-bold](icons/stack-bold.svg) | `stack-bold` |
| ![stack](icons/stack.svg) | `stack` |
| ![warning-circle-fill](icons/warning-circle-fill.svg) | `warning-circle-fill` |
| ![x-bold](icons/x-bold.svg) | `x-bold` |
| ![x-circle-fill](icons/x-circle-fill.svg) | `x-circle-fill` |
| ![x-circle](icons/x-circle.svg) | `x-circle` |
| ![x](icons/x.svg) | `x` |

===== FILE: pipeline_line/README.md =====

# 📦 pipeline_line — ระบบ LINE Image Archive

โฟลเดอร์นี้เก็บ Pipeline ทั้งหมดสำหรับดึง จัดระเบียบ และ Archive ภาพลวดลายที่พี่กบส่งมาทาง LINE

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
ดับเบิ้ลคลิก: line_review.command
```
เปิดหน้าเว็บ http://localhost:5555 (จอสีดำ) แสดงรูปที่สถานะ PENDING
- **A** = Approve (ผ่าน)
- **R** = Reject (ปัดตก)
- **Space / →** = ข้ามไปรูปถัดไป
- ปุ่ม **🤖 ให้ Haiku ดูอีกรอบ** = ส่งรูปให้ AI วิเคราะห์ใหม่ (เสีย Token นิดหน่อย)

---

### ขั้นตอนที่ 3 — สร้าง Asset_Map สรุปผลทั้งหมด
```
ดับเบิ้ลคลิก: line_finalize.command
```
นำรูปที่ APPROVED ทั้งหมดไปเทียบกับ tspl_database แล้วสร้างตาราง **Asset_Map** ใน Spreadsheet
ระบบจะใช้ทั้ง **ชื่อที่ Haiku อ่านได้** + **Timestamp การส่งไฟล์** เพื่อจับคู่ให้แม่นยำที่สุด

---

## 📁 รายละเอียดไฟล์แต่ละตัว

| ไฟล์ | หน้าที่ |
|------|---------|
| `run_pipeline.command` | **ปุ่มหลัก** รัน sync + classify รวดเดียวจบ |
| `line_sync.py` / `.command` | ดึงไฟล์รูปและเอกสารจาก Google Drive มาใส่ LINE_Sync sheet |
| `line_classify.py` / `.command` | ส่งรูปให้ Claude Haiku Vision วิเคราะห์และเขียนผลลง LINE_Review |
| `line_review.py` / `.command` | เปิด web UI สำหรับ Human-in-the-loop review |
| `line_finalize.py` / `.command` | สร้าง Asset_Map โดย match รูปเข้า tspl_database |
| `line_match.py` / `.command` | *(เวอร์ชันเก่า ก่อนใช้ AI — ไม่จำเป็นต้องใช้แล้ว)* |

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

===== FILE: tools_debug/README.md =====

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

===== FILE: tools_web/README.md =====

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
