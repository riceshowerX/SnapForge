<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="public/logo.png">
  <source media="(prefers-color-scheme: dark)" srcset="public/logo.png">
  <img src="public/logo.png" width="120" height="120" alt="SnapForge" style="border-radius: 24px;">
</picture>

# SnapForge

### Professional Image Processing Platform

**A powerful modern image processing platform featuring batch processing, format conversion, filters, watermarks, smart deduplication, and complete image processing workflow**

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

[Live Demo](https://snapforge.dev.coze.site) · [快速开始](#快速开始) · [功能特性](#功能特性) · [技术架构](#技术架构)

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🚀 **High Performance** | Concurrent processing engine, supports 1-10 images simultaneously |
| 🔒 **Secure & Reliable** | Magic Number verification, rate limiting, path traversal protection |
| 📦 **Batch Processing** | Process hundreds of images at once with auto queue management |
| 🎨 **Rich Filters** | 15+ built-in filters with custom color adjustments |
| 🧠 **Smart Deduplication** | Perceptual hash algorithm for fast similar/duplicate detection |
| 💾 **Data Persistence** | Local storage for task history, cloud sync for processing schemes |

---

## Features Overview

### Core Image Processing

| Feature | Description | Supported Formats |
|---------|-------------|-------------------|
| **Format Conversion** | Convert between popular formats with quality control | JPEG, PNG, WebP, AVIF, TIFF, GIF, BMP |
| **Resize** | Smart scaling with multiple fit modes | Fit/Fill/Stretch/Crop |
| **Smart Crop** | Custom crop areas with preset ratios | 1:1, 16:9, 4:3, 3:2, 2:1, Custom |
| **Rotate & Flip** | Any-angle rotation, horizontal/vertical flip | - |
| **Filters** | 15+ professional filters one-click apply | Grayscale, Vintage, Sharpen, Blur, Emboss, etc. |
| **Color Adjustment** | Fine-tune brightness/contrast/saturation | Range 0-10 |
| **Watermark** | Text/image watermarks with 9-grid positioning | 9-grid + Tiled |
| **Border** | Customizable border width, color, rounded corners | - |

### Advanced Features

- **Batch Processing** - Process hundreds of images at once with concurrency control and error interruption options
- **Processing Schemes** - 5 preset schemes for one-click apply, custom scheme save/import/export
- **Duplicate Detection** - Perceptual hash algorithm with similarity threshold configuration (0.5-1.0)
- **Statistics Dashboard** - Visual dashboard tracking processing trends, efficiency, success rate, and feature usage ranking
- **Image Comparison** - Slider/overlay/side-by-side comparison modes with zoom and fullscreen viewing
- **EXIF Information** - Complete display of shooting parameters, focal length, aperture, ISO and other metadata

### User Experience

- **Multiple Upload Methods** - Drag & drop, paste, click to upload
- **Real-time Preview** - Instant processing effect visibility, no waiting
- **Keyboard Shortcuts** - Ctrl+V paste, Ctrl+A select all, Delete remove, Ctrl+Enter process
- **Batch Download** - One-click ZIP package download for all processed results
- **Theme Toggle** - Dark/light mode following system preference
- **Responsive Design** - Perfect adaptation for desktop, tablet, and mobile devices

---

## Screenshots

> 📸 Screenshots are available at [screenshots](./screenshots/) directory.
> 
> To add your own screenshots:
> 1. Visit the live demo at https://snapforge.dev.coze.site
> 2. Take screenshots of the main interface, configuration panel, etc.
> 3. Save them to the `screenshots/` directory as `main.png`, `config.png`, `compare.png`, `stats.png`

### Main Interface
![Main Interface](./screenshots/main.png)

### Processing Configuration
![Configuration Panel](./screenshots/config.png)

### Image Comparison
![Image Comparison](./screenshots/compare.png)

### Statistics Dashboard
![Statistics Dashboard](./screenshots/stats.png)

---

## Quick Start

### Requirements

| Environment | Requirement |
|-------------|-------------|
| **Node.js** | >= 18.0 |
| **pnpm** | >= 9.0 |
| **OS** | Linux, macOS, Windows |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# 2. Install dependencies
pnpm install

# 3. Start development server
pnpm dev

# 4. Open browser
open http://localhost:5000
```

### Production Deployment

```bash
# 1. Build production version
pnpm build

# 2. Start production server
pnpm start

# 3. Server runs at http://localhost:5000
```

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `5000` |

---

## Architecture

### Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Framework** | Next.js (App Router) | 16.1.1 |
| **UI Library** | React | 19.2.3 |
| **Language** | TypeScript | 5.0 |
| **Styling** | Tailwind CSS + shadcn/ui | 4.0 |
| **State Management** | Zustand (with persistence) | - |
| **Image Processing** | Sharp (libvips) | - |
| **Charts** | Recharts | - |
| **Zip Packaging** | JSZip | - |
| **Unique ID** | UUID | - |

### Project Structure

```
SnapForge/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── api/                     # API Routes
│   │   │   ├── upload/route.ts      # File upload endpoint
│   │   │   ├── process/route.ts     # Image processing endpoint
│   │   │   └── duplicates/route.ts  # Duplicate detection endpoint
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page
│   │   └── globals.css              # Global styles
│   │
│   ├── components/                   # React Components
│   │   ├── ui/                      # shadcn/ui base components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ... (more components)
│   │   │
│   │   ├── ImageUploader.tsx        # Image upload component
│   │   ├── ProcessConfigPanel.tsx   # Processing config panel
│   │   ├── ProcessingPanel.tsx       # Processing panel
│   │   ├── ImageCompare.tsx          # Image comparison
│   │   ├── ExifPanel.tsx            # EXIF info panel
│   │   ├── SchemeManager.tsx         # Scheme management
│   │   ├── StatsDashboard.tsx        # Statistics dashboard
│   │   ├── DuplicateDetector.tsx    # Duplicate detection
│   │   ├── ThemeToggle.tsx          # Theme toggle
│   │   └── ProcessingHistory.tsx    # Processing history
│   │
│   ├── lib/                         # Utilities
│   │   ├── image-processor.ts       # Image processing core
│   │   ├── utils.ts                 # Common utilities
│   │   ├── api-response.ts          # Unified API response
│   │   └── rate-limit.ts            # Rate limiting
│   │
│   ├── store/                       # State management
│   │   └── index.ts                 # Zustand Store
│   │
│   └── types/                        # TypeScript types
│       └── index.ts                  # Global type definitions
│
├── public/                           # Static assets
│   └── logo.png                      # Project logo
│
├── screenshots/                      # Screenshots
│
├── .coze                            # Coze config
├── .cozeproj                        # Coze project config
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
├── tailwind.config.ts              # Tailwind config
└── README.md                        # This file
```

---

## API Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/api/upload` | POST | Upload images | 30/min |
| `/api/process` | POST | Process images | 20/min |
| `/api/duplicates` | POST | Detect duplicates | 10/min |

---

## Security

- **Magic Number Verification** - Validates real file type by file header bytes
- **File Size Limit** - Max 50MB per file
- **Safe Filenames** - Removes path traversal characters and Unicode control characters
- **Unicode Normalization** - Prevents NFC/NFD normalization attacks
- **Rate Limiting** - Prevents abuse and ensures service stability

---

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/riceshowerX">riceshowerX</a>
</p>
</div>
