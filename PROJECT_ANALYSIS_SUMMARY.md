# 🏛️ TSPL Digital Archive - Project Analysis Summary for AI
This document is prepared specifically for an external AI to analyze, refactor, or build upon the **Thai Symbol Pattern Lab (TSPL) Digital Archive** project. It outlines the project objectives, architecture, data flows, database schemas, codebase structures, recent refinements, and future integration plans.

---

## 1. Project Identity & Overview
* **Project Name**: Thai Symbol Pattern Lab (TSPL) Digital Archive
* **Core Objective**: A cultural archiving system that indexes, digitizes, analyzes, and publishes traditional Thai artistic and architectural patterns (currently 158 resolved items out of 180 planned).
* **Target Audience**: Researchers, graphic designers, and cultural preservationists who need high-fidelity vector assets (`.svg`) along with structural (visual morphemes) and ethical protocol descriptions.
* **Master Categories**:
  1. `Nature & Botany` (พรรณพฤกษาและธรรมชาติ) -> Code: `NAT`
  2. `Fauna & Mythical` (สรรพสัตว์และสัตว์หิมพานต์) -> Code: `FAU`
  3. `Geometric & Synthetic` (เรขาคณิตและลวดลายประดิษฐ์) -> Code: `GEO`
  4. `Sacred & Belief` (สัญลักษณ์ความเชื่อและสิ่งศักดิ์สิทธิ์) -> Code: `SAC`

---

## 2. Current Architecture & Stack

```
+------------------------------------+
|          Google Drive              | (Raw Photos, .docx descriptions)
+------------------------------------+
                  |
                  v (Claude AI Extractor via semiotic_extractor.py)
+------------------------------------+
|    Google Sheet Staging (Haiku)    |
+------------------------------------+
                  |
                  v (Manual review & db_mirror.py)
+------------------------------------+
|    Google Sheet Production (Master)|
+------------------------------------+
                  |
                  +-----------------------+
                  | (Published CSV Link)  | (Local sync via asset_manager.py)
                  v                       v
+------------------------------------+ +------------------------------------+
|          Vercel Frontend           | |   Local Flask Admin Control Center  |
|      (HTML/CSS/Vanilla JS)         | |        (localhost:5556)             |
+------------------------------------+ +------------------------------------+
```

### Frontend (Client-side)
* **Hosting**: Vercel (Auto-deploy on GitHub push)
* **Stack**: Vanilla HTML5, Vanilla CSS3 (custom layouts & transitions), Vanilla JavaScript (ES6+).
* **Data Ingestion**: The frontend does **not** query a database server. Instead, it directly fetches the published CSV URL of the Google Sheet at runtime, parses it using JavaScript, and dynamically renders the grid and filter controls.
* **Design Theme**: Futuristic blueprint / high-tech technical archiving grid combined with traditional Thai heritage gold and deep navy colors (`#0F172A`, `#FF4E45`, `#D4AF37`).

### Database & Asset Management (Backend CMS)
* **Google Sheets**: Serves as the primary Headless CMS.
  * *Sheet ID*: `1iJIr2vT3WeyavBi4_sw3In04yNNHF-GNbJ8zf8egdHs`
  * *Staging Sheet*: `Haiku` (where AI writes raw extraction outputs).
  * *Production Sheet*: `tspl_database` (stable production schema used by Vercel).
* **Google Drive**: Hosts folders named after patterns containing:
  * `main.jpg`, `context.jpg`, `detail.jpg`, `vectors/vector.svg`, and descriptions.
* **Local Scripts (`tools_web/`)**:
  * `asset_manager.py`: Connects to Google Drive, maps folder structures via fuzzy mapping, maps pattern IDs, downloads and saves assets locally to `assets/images/database/`.
  * `dashboard.py`: A local **Flask app (port 5556)** serving as an Admin UI Dashboard for the client to run Python scripts without using the command line. Launched via `TSPL_CONTROL_CENTER.command` on macOS.
  * `optimize_images.py`: Compresses images to `<500KB` and pads/blurs vertical images to fit a stable `4:3` aspect ratio to prevent slow load times and Vercel storage limits.
  * `db_mirror.py`: Synchronizes records between the staging sheet and production sheet.

---

## 3. Database Schema Reference (Master Sheet Columns)

The live JavaScript mapping (`assets/js/index.js`) depends strictly on these headers. Do not rename or reorder columns without modifying the frontend parse script:

| Column | Name | Type / Format | Description |
| :--- | :--- | :--- | :--- |
| 1 | `Symbol ID` | Text (e.g., `TSP-LST-NAT-001`) | Primary key. Format: `TSP-LST-[CAT]-[Num]` |
| 2 | `Title (TH)` | Text | Thai name of the pattern (e.g., `ลายเครือวัลย์`) |
| 3 | `Title (EN)` | Text | English name of the pattern (e.g., `Kruea Wan Pattern`) |
| 4 | `Category` | Text | Category name matching one of the 4 Master Categories |
| 5 | `Location` | Text | Historical site where the pattern was found |
| 6 | `Confidence` | Text (`Verified`, `Reconstructed`, `Fragment`, `Hypothetical`) | Reliability status badge |
| 7 | `Ethics` | Text (`low`, `medium`, `high`) | Cultural sensitivity level |
| 8 | `Connotation (TH)`| Text | Semiotic/cultural meaning in Thai |
| 9 | `Connotation (EN)`| Text | Semiotic/cultural meaning in English |
| 10 | `Protocol Preserve`| Text | Guidelines on what to maintain when replicating |
| 11 | `Protocol Do Not` | Text | Restrictions on what should not be altered |
| 12 | `Morphemes (TH)` | Pipe-separated (`|`) Text | Structural visual components in Thai (e.g., `ม่านประดับ\|ก้านเถา`) |
| 13 | `Morphemes (EN)` | Pipe-separated (`|`) Text | Structural visual components in English |
| 14 | `Tags` | Comma-separated (`,`) Text | Keywords for search and filtering |
| 15 | `Image Main` | Local path | Path to primary grid thumbnail image |
| 16 | `Image Vector` | Local path | Path to downloadable SVG file |
| 17 | `Image Context` | Local path | Path to context/location photograph |
| 18 | `Image Mid` | Local path | Mid-shot image (optional) |
| 19 | `Image Detail` | Local path | High-detail closeup image (optional) |

---

## 4. Key Codebase Components

* **`index.html` & `archive.html`**:
  - Main display interface containing the search bar, filter tabs (Category, Reliability/Confidence, Location, Vector availability), and the main responsive grid layout.
* **`assets/js/index.js`**:
  - The single source of truth for frontend logic.
  - Fetches the published Google Sheet CSV link.
  - Generates the pattern cards dynamically.
  - Handles real-time search queries and category filter counts.
  - Implements the detail modal displaying semiotic details, ethics protocols, context maps, and interactive SVG downloads.
* **`tools_web/asset_manager.py`**:
  - Core Python ingestion script using `google-api-python-client` and `gspread`.
  - Downloads images from Google Drive folders, maps them to IDs using fuzzy match matching, and writes them to local directories.
* **`tools_web/dashboard.py`**:
  - Starts a local web server (port 5556) that allows the client to trigger tasks like "Download Assets", "Run AI Extractor", "Sync Sheets", and "Deploy" visually.

---

## 5. Recent Refinements & Optimizations (Current State)

When analyzing the code, take note of the following recent improvements which should be preserved:
1. **Full-Bleed Image Layout**: Grid card images now display in full crop (`object-cover w-full h-full`) with a scale animation on hover (`group-hover:scale-110 duration-500`) to create a premium cinematic feel.
2. **Brighter Confidence Badges**: Replaced dark overlays on cards with brighter semi-transparent badges (`bg-white/80 backdrop-blur-md text-[#0F172A]`) for improved readability.
3. **Responsive Mobile 2-Column Grid**: Optimizations applied to `index.html` and `archive.html` grids:
   - On mobile screens, it displays 2 columns (`grid-cols-2`) instead of 1.
   - Text sizes on mobile cards are scaled down (`text-[10px]` to `text-xs`) and padding reduced to prevent text collisions.
4. **Native Browser Lazy Loading**:
   - The Infinite Scroll IntersectionObserver pagination was removed due to scrolling lag on high-resolution displays.
   - Now, all 158 pattern cards are rendered simultaneously, leveraging native HTML attributes: `loading="lazy"` and `decoding="async"` on images. This ensures 60fps scrolling and instant responsive filtering.
5. **Dynamic Category Counts**:
   - Filter tab headers dynamically calculate the number of matching patterns in each category and display them as parenthesized Arabic numerals, e.g., `Nature & Botany (45)`.

---

## 6. Handover & Cloud-Integration Ideas

The local machine dependency (Python, `.command` files, macOS specific configurations, local asset storage in Git) is a potential bottleneck. The proposed cloud integration scenarios are:

### Scenario A: Next.js/Astro Web App + Cloudflare R2 (Recommended)
1. **Migration**: Rewrite the static HTML files to a single full-stack Next.js (React) application.
2. **Serverless APIs**: Port the local Python script tasks to Node.js / Serverless API routes (e.g. `gspread` Node package).
3. **Decoupled Asset Storage**: When the client clicks "Sync" in the web admin panel:
   - The backend downloads files from Google Drive and uploads them directly to an S3-compatible cloud storage (like **Cloudflare R2**).
   - This keeps the Git repository tiny and avoids Vercel deployment size limits.
4. **Admin Dashboard**: Create a secure, web-based admin console `/admin` within the web app, eliminating the need for local Flask apps or double-clicking command files.

### Scenario B: Containerized Docker Stack
1. **Deployment**: Wrap the static Nginx server and the Python Flask backend into a single `docker-compose.yml` stack.
2. **Advantages**: Guarantees identical runtime environments on Windows, Linux, or macOS.

### Scenario C: Streamlit Web Admin Portal
1. **UI**: Port the Flask Control Center to a pure-Python Streamlit App hosted on Streamlit Community Cloud (free).
2. **Integration**: Upon syncing, Streamlit writes directly to Google Sheets and fires Vercel deploy hooks.

---

## 7. Guidelines for the Analyzing AI

When proposing changes, fixing bugs, or implementing new features on this codebase, always ensure that:
1. **SEO Semantic Integrity**: Maintain proper HTML5 semantic structures and unique testing IDs.
2. **Consistent Color Palette**: Strictly follow the design system tokens (`#FF4E45` Accent Red, `#0F172A` Deep Navy, and `#D4AF37` Heritage Gold).
3. **Data Robustness**: Always write safe data access rules. Check if row contents are empty or missing before parsing. Do not assume all 19 columns always contain data.
4. **No Breakages to Transitions**: The preloader overlay (`#preloader`) and page fade transitions (`initPageTransitions`) inside `assets/js/index.js` must remain intact.
5. **No Placeholders**: If visual mockups are generated or needed, use working assets or functional code rather than mock variables.
