<div align="center">

<img src="public/logo.png" width="120" height="120" alt="SnapForge" style="border-radius: 24px; box-shadow: 0 6px 28px rgba(0,0,0,.10);" />

# SnapForge

**Image processing, perfected — Batch Processing · Format Conversion · Filters · Watermarks · Smart Dedup**

A fully local, modern image processing workbench. No sign-up, no cloud upload — every image is processed on your own machine by the **Sharp engine**, keeping your data 100% private.

[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=flat-square&logo=github&label=Stars)](https://github.com/riceshowerX/SnapForge/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/riceshowerX/SnapForge?style=flat-square&label=Last%20Commit)](https://github.com/riceshowerX/SnapForge/commits/main)
[![License](https://img.shields.io/github/license/riceshowerX/SnapForge?style=flat-square)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-000000.svg?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB.svg?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC.svg?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)

[中文](README.md) · [Highlights](#-highlights) · [Features](#-features) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Tech Stack](#-tech-stack) · [Security](#-security) · [Contributing](#-contributing)

</div>

---

## 🎯 Highlights

| | |
|---|---|
| 🏠 **Local-First** | All processing happens on your machine (Sharp engine). Images never leave your device — privacy is 100% under your control |
| ⚡ **Batch Efficient** | Process hundreds of images at once with adjustable 1–10 way concurrency and live progress |
| 🛡️ **Hardened Security** | SSRF protection, magic-number validation, decompression-bomb defense, rate limiting — production-grade practices |
| 🚀 **Zero Config** | Start in seconds, bilingual UI (中文 / English), dark / light themes, fully responsive |

---

## ✨ Features

### 🖼️ Core Image Processing

| Feature | Description | Formats |
|---------|-------------|---------|
| **Format Conversion** | Convert between major formats with quality & compression control | JPEG, PNG, WebP, AVIF, TIFF, GIF, BMP |
| **Resize** | Smart scaling: fit / fill / stretch / crop modes | - |
| **Smart Crop** | Custom crop region with presets: 1:1, 16:9, 4:3, 3:2, etc. | - |
| **Rotate & Flip** | Arbitrary rotation angle, vertical / horizontal flip (actually applied) | - |
| **Filters** | 15+ professional filters: grayscale, vintage, sharpen, blur, emboss, etc. | - |
| **Color Adjust** | Fine-tune brightness / contrast / saturation | - |
| **Watermark** | Text / image watermark, 9-position grid + tile mode (rotation & spacing) | - |
| **Border** | Custom border width, color, corner radius | - |
| **Preserve Metadata** | Keep EXIF / ICC metadata on output (toggleable) | - |
| **Target Compression** | Binary-search compression toward a target size (KB), ideal for web | JPEG, WebP |

### 🧠 Smart Capabilities

- **Batch Processing** — hundreds of images at once, configurable concurrency (1–10) & stop-on-error
- **Processing Schemes** — one-click presets (Web Optimized, Watermark Protect, etc.), custom schemes with save / import / export (runtime-validated import)
- **Smart Dedup** — perceptual hashing detects similar / duplicate images, configurable threshold, real similarity scores
- **Stats Dashboard** — real metrics: processing trends, success rate, average time, space saved
- **EXIF Viewer** — client-side exifr parsing, full camera / lens / ISO / exposure details
- **Processing History** — last 20 local records, reusable configurations

### 🎨 UX Details

- **Multiple Upload** — drag & drop, paste (Ctrl+V), click; 4-way concurrent upload
- **Live Preview** — thumbnails & raw data stored separately (IndexedDB), instant feedback
- **Hotkeys** — `Ctrl+V` paste, `Ctrl+A` select all, `Delete` remove, `Ctrl+Enter` process
- **Batch Download** — one-click ZIP; rename templates with `{counter}` to avoid collisions
- **i18n** — Chinese / English toggle covering all UI text & preset names
- **Theme** — dark / light mode following system preference
- **Responsive** — desktop, tablet and mobile

---

## 🚀 Quick Start

### Requirements

| Environment | Requirement |
|-------------|-------------|
| **Node.js** | >= 18.0 (20+ recommended) |
| **pnpm** | >= 9.0 (`only-allow pnpm` is enforced) |

### Install & Run

```bash
# 1. Clone the repository
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# 2. Install dependencies
pnpm install

# 3. Start the dev server (default port 5000)
pnpm dev

# 4. Open your browser
#    http://localhost:5000
```

### Production Deployment

```bash
pnpm build   # Build for production
pnpm start   # Start the production server (default port 5000)
```

### Code Quality

```bash
pnpm lint       # ESLint
pnpm ts-check   # TypeScript type check
```

---

## 🔌 API Reference

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/api/upload` | POST | Upload an image (multipart/form-data, field `file`) | 30 req/min |
| `/api/process` | POST | Process an image with config (`file` + `config` JSON) | 20 req/min |
| `/api/duplicates` | POST | Detect duplicate / similar images (`files` multiple) | 10 req/min |

All endpoints return a unified response format:

```json
{
  "success": true,
  "data": {},
  "timestamp": 1755330000000
}
```

Errors include `error.code` / `error.message` (e.g. `INVALID_FILE_TYPE`, `RATE_LIMIT_EXCEEDED`).

---

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| Framework | Next.js (App Router) | 16.1.1 |
| UI | React | 19.2.3 |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS + shadcn/ui | 4.x |
| State | Zustand (persisted) | 5.0 |
| Imaging | Sharp (libvips) | 0.34 |
| Client ZIP | JSZip | 3.10 |
| EXIF | exifr | 7.1 |
| Forms / Validation | react-hook-form + zod | 4.3 |
| Charts | Recharts | 2.15 |

---

## 📁 Project Structure

```
SnapForge/
├── src/
│   ├── app/
│   │   ├── api/                  # API routes (upload / process / duplicates)
│   │   ├── layout.tsx            # Root layout (dynamic language)
│   │   ├── page.tsx              # Home (single-page workbench)
│   │   └── error.tsx             # Error boundaries
│   ├── components/
│   │   ├── ui/                   # shadcn/ui primitives
│   │   ├── ImageUploader.tsx     # Upload (drag / paste / concurrent)
│   │   ├── ProcessingPanel.tsx   # Batch processing panel
│   │   ├── DuplicateDetector.tsx # Smart deduplication
│   │   ├── ExifPanel.tsx         # EXIF viewer
│   │   ├── SchemeManager.tsx     # Scheme management (validated import)
│   │   ├── StatsDashboard.tsx    # Statistics dashboard
│   │   └── ProcessingHistory.tsx # Processing history
│   ├── lib/
│   │   ├── image-processor.ts    # Sharp processing pipeline
│   │   ├── file-validation.ts    # Unified file type / size / name validation
│   │   ├── config-schema.ts      # zod config schema + deep merge
│   │   ├── blob-store.ts         # IndexedDB raw blob storage
│   │   ├── request-guard.ts      # API request guard (Content-Length)
│   │   ├── rate-limit.ts         # Rate limiting (real IP + capacity cap)
│   │   ├── api-response.ts       # Unified API response format
│   │   └── i18n.ts               # i18n dictionary (zh / en)
│   ├── store/                    # Zustand state (persisted)
│   └── types/                    # TypeScript definitions
├── public/                       # Static assets
├── scripts/                      # dev / build / start scripts
├── AGENTS.md                     # Development conventions
├── SECURITY.md                   # Security policy
└── package.json
```

---

## ⚙️ Configuration

| Item | Description |
|------|-------------|
| Dev / Prod port | 5000 (`scripts/dev.sh`, `scripts/start.sh`) |
| Max file size | 50 MB (`MAX_FILE_SIZE` in `src/lib/file-validation.ts`) |
| Upload formats | JPEG / PNG / WebP / GIF (SVG / PDF rejected to reduce attack surface) |
| Large image policy | raw data (>2MB) stored in IndexedDB, 800×800 thumbnail for preview |
| Rate limits | `/api/upload` 30/min · `/api/process` 20/min · `/api/duplicates` 10/min |
| Language | toggle 中文 / English in the top-right, preference persisted to localStorage |
| History | max 20 records, stored compactly via `stripLargeData()` |

---

## 🔒 Security

- **SSRF Protection** — watermark remote URLs restricted to http/https, all private / reserved ranges (incl. IPv6) blocked after DNS resolution, fetch timeout + redirect re-validation
- **Magic Number Validation** — real type verified from file header bytes, client MIME never trusted
- **Decode Guardrails** — explicit `limitInputPixels` + `failOn: 'error'` on every sharp entry (decompression bombs)
- **Request Guard** — strict Content-Length check (missing / oversized → 413)
- **Hardened Rate Limiting** — keyed by real connection IP (forged headers ignored), bounded store
- **Filename Sanitization** — path traversal, Windows reserved device names, control chars, Unicode NFC
- **Runtime Config Validation** — zod schema, invalid params → friendly 400 instead of 500

---

## 🤝 Contributing

Issues and Pull Requests are welcome! How to contribute:

1. **Fork** the repo and create a feature branch: `git checkout -b feature/your-feature`
2. **Develop** — follow the conventions in `AGENTS.md` (React hooks, i18n, naming, security)
3. **Verify** — `pnpm lint` and `pnpm ts-check` must pass before submitting
4. **Commit** — follow Conventional Commits style (`feat:` / `fix:` / `refactor:`)
5. **Open a PR** — clearly describe your changes and how they were verified

> 💡 New contributor? The pure functions in `src/lib/` (`file-validation.ts`, `config-schema.ts`) are great first contributions.

### Roadmap

- [ ] More filters & AI enhancements (super-resolution, denoising)
- [ ] Persistent batch queue with resume support
- [ ] Command-line (CLI) version
- [ ] PWA offline support

---

## 📄 License

[MIT License](LICENSE) — Copyright © 2026 [riceshowerX](https://github.com/riceshowerX)

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/riceshowerX">riceshowerX</a> · Local-first · Privacy-first</sub>
</p>
