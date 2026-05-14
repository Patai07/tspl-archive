# DATA_FLOW.md

## 1. Overview
The TSPL data pipeline is designed to systematically ingest raw cultural data, structure it using AI, validate it, and publish it to a live digital archive. The journey begins with raw files in Google Drive, passes through an AI extraction layer into a staging environment (Haiku Sheet), undergoes human review, and is finally committed to the production database (Master Sheet), which dynamically feeds the Vercel-hosted frontend.

## 2. Source Data
Google Drive serves as the primary repository for all source materials. This includes original photographs, context images, vector files, and document files (e.g., `.docx`) containing detailed descriptions and cultural context for each pattern. The structure in Drive dictates the initial categorization.

## 3. AI Extraction Layer
The `semiotic_extractor.py` script acts as the data processing engine. It reads the source documents from Google Drive and utilizes Claude AI (specifically the Haiku model) to analyze and extract structured semiotic data, such as visual morphemes, cultural connotations, and ethical protocols.

## 4. Haiku Sheet / Extraction Sheet
- **Receives extracted data:** The AI extractor writes its output directly to this staging sheet.
- **Used for review and validation:** It acts as a buffer where data can be checked before going live.
- **Not the live database:** The frontend website does not read from this sheet.
- **May contain incomplete data:** Because the extraction is automated, data here might be raw, incomplete, or require refinement.

## 5. Review and Validation
Before any data becomes visible to the public, it must be reviewed. The data in the Haiku Sheet should be manually checked for accuracy, formatting, and completeness to ensure high-quality standards are met before it is transferred to the production environment.

## 6. Master Sheet / Production Sheet
- **Live database for the website:** This is the single source of truth for the production website.
- **Read by the website through published CSV:** The data is exposed to the frontend via a Google Sheets published CSV link.
- **Must remain schema-stable:** The structure of this sheet is critical. Do not rename, reorder, or remove columns, as the frontend code heavily relies on the exact layout.

## 7. Website Consumption
- **The website reads data from Google Sheets CSV:** The live site fetches the published CSV to render the database and detail pages dynamically.
- **`index.js` depends on exact column headers:** The JavaScript logic maps data based on specific column names (e.g., `Symbol ID`, `Title (TH)`). Any deviation will cause the site to break or display empty fields.
- **Google cache may take around 5 minutes:** Updates made to the Master Sheet are not instantly reflected on the live site due to Google's CSV caching mechanism. Allow up to 5 minutes for changes to propagate.

## 8. Deployment
- **Assets and frontend are deployed to Vercel:** The HTML/CSS/JS files, along with the processed image and vector assets in `assets/images/database/`, are hosted on Vercel.
- **Images should be optimized before deployment:** Large image files must be processed using `optimize_images.py` to ensure they meet the <500KB constraint and 4:3 aspect ratio, preventing excessive storage use on Vercel.
- **`deploy.command` affects production:** Running this script pushes the current local state to the live Vercel environment.

## 9. Risk Points
- **Renaming columns:** Will immediately break the frontend data mapping in `index.js`.
- **Changing separators:** Modifying the `|` (pipe) separator for morphemes or the `,` (comma) separator for tags will break the UI rendering logic.
- **Running `clear_sheet.command`:** A highly destructive action that permanently deletes data.
- **Deploying unoptimized images:** Can lead to slow load times and exceed Vercel's hosting limits.
- **Mixing Haiku Sheet and Master Sheet:** Risk of exposing unverified, raw AI output directly to the live production website.
