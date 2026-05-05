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
