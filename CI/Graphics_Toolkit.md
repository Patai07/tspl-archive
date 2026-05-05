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
