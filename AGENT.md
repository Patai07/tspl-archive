# AGENT.md

## 1. Project Summary
Thai Symbol Pattern Lab (TSPL) is a digital archive project that manages and stores Thai cultural symbols, architectural patterns, and art forms. It collects raw data from primary sources, uses AI to extract structural and semiotic metadata (visual morphemes, cultural meaning, ethics), and provides these as vector-ready digital assets for cultural preservation and creative economy applications.

## 2. Architecture
- **Frontend stack:** HTML, Vanilla JavaScript, and CSS (Tailwind CSS), focusing on a premium cinematic, blueprint-style interface.
- **Hosting:** Vercel.
- **Database:** Google Sheets acts as a Headless CMS. The live website reads data from a published CSV URL to update in real-time.
- **Asset storage:** Local file system structure (`assets/images/database/`) organized by category and pattern ID, deployed along with the frontend.
- **Main scripts/tools:** Python automation scripts (e.g., `semiotic_extractor.py`, `optimize_images.py`) and bash commands (`deploy.command`) for data ingestion, processing, and deployment.

## 3. Critical Data Flow
Google Drive
→ Claude / Haiku extraction (`semiotic_extractor.py`)
→ Haiku Sheet / Extraction Sheet
→ Review / validation (Manual)
→ Master Sheet / Production Sheet
→ Published CSV
→ Vercel website

## 4. Sheet Roles

### Haiku Sheet / Extraction Sheet
- Used for AI extraction output.
- Can contain raw or incomplete data.
- `semiotic_extractor.py` writes here.
- Not the live website database.

### Master Sheet / Production Sheet
- Used by the live website.
- Production-sensitive.
- Do not rename, reorder, or remove columns.
- Do not write raw extracted data directly here.
- Any schema change may break `index.js` and the live website.

## 5. Non-Negotiable Rules
- Do not change Google Sheet column headers without explicit confirmation.
- Do not change API or CSV output assumptions without checking frontend usage.
- Do not modify Production/Master Sheet without confirmation.
- Do not run `deploy.command` unless explicitly requested.
- Do not run `clear_sheet.command` unless explicitly requested.
- Do not remove or rewrite preloader / page transition logic.
- Do not remove `.lang-th` typography handling.
- Do not refactor working code unless requested.

## 6. Script Risk Map

- **`deploy.command` = High risk**
  - **What it does:** Deploys the website to Vercel.
  - **What it may affect:** The live production website.
  - **When it is safe to run:** Only when local changes are fully tested and ready for production.
  - **Confirmation:** Required.

- **`clear_sheet.command` = High risk**
  - **What it does:** Clears data from a specified Google Sheet.
  - **What it may affect:** Deletes database records permanently.
  - **When it is safe to run:** Only during safe resets or debug testing on non-production data.
  - **Confirmation:** Required.

- **`semiotic_extractor.py` = Medium risk**
  - **What it does:** Reads Google Drive documents, uses Claude AI to extract semiotic data, and writes to the Haiku Sheet.
  - **What it may affect:** Appends rows to the Haiku Sheet, consumes API tokens.
  - **When it is safe to run:** When processing new data batches.
  - **Confirmation:** Required.

- **`run_extractor.command` = Medium risk**
  - **What it does:** Wrapper to execute `semiotic_extractor.py`.
  - **What it may affect:** Appends rows to the Haiku Sheet, consumes API tokens.
  - **When it is safe to run:** When processing new data batches.
  - **Confirmation:** Required.

- **`optimize_images.py` = Medium risk**
  - **What it does:** Resizes and compresses images to <500KB and 4:3 aspect ratio.
  - **What it may affect:** Overwrites local image files in the assets directory.
  - **When it is safe to run:** Before deploying new image assets to production.
  - **Confirmation:** Recommended.

- **`db_mirror.py` = Low/Medium risk**
  - **What it does:** Backs up Google Sheets data to local CSV files.
  - **What it may affect:** Overwrites local backup files.
  - **When it is safe to run:** Anytime a backup is needed.
  - **Confirmation:** Not strictly required, but good practice.

- **`fix_footer_links.py` = Medium risk**
  - **What it does:** Edits footer links across HTML files.
  - **What it may affect:** HTML files across the project.
  - **When it is safe to run:** When updating global navigation/links.
  - **Confirmation:** Required.

- **`tools_debug` scripts (`debug_match.py`, `debug_time.py`) = Low risk**
  - **What it does:** Read-only diagnostic tools.
  - **What it may affect:** Nothing (read-only).
  - **When it is safe to run:** Anytime for troubleshooting.
  - **Confirmation:** Not required.

## 7. Frontend Stability Rules
- New HTML pages must link `assets/css/index.css` and `assets/js/index.js`.
- Do not remove `#preloader`.
- Do not break `initPageTransitions()`.
- Preserve IBM Plex Sans Thai, Noto Sans Thai, Space Grotesk, and Cutive Mono usage.
- Preserve `.lang-th` class behavior.

## 8. Google Sheet Data Rules
- Column headers are fixed.
- Morphemes use pipe separator `|`.
- Tags use comma separator `,`.
- Published CSV cache may take about 5 minutes to update.
- Empty or missing fields must be handled safely.
- Required fields should be validated before production use.

## 9. Asset Rules
- Main asset path pattern: `assets/images/database/[Category_Folder]/[Pattern-ID]/`
- Expected files:
  - `main.jpg`
  - `context.jpg`
  - `detail.jpg`
  - `vectors/vector.svg`
- Images should be optimized before Vercel deployment.
- Vector files should remain SVG.

## 10. Before Making Changes
For every meaningful change, the agent must first explain:
- What will change
- Why it is needed
- Files affected
- Sheets affected
- Risk level: Low / Medium / High
- How to test
- How to rollback

## 11. Unknowns / Needs Confirmation
- Exact Master Sheet column list.
- Exact Haiku Sheet column list.
- Published CSV URL location.
- Environment variable names.
- Whether API routes exist or the site only uses CSV.
- Current deployment workflow details.
