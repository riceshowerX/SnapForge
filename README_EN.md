<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="public/logo.png">
  <source media="(prefers-color-scheme: dark)" srcset="public/logo.png">
  <img src="public/logo.png" width="120" height="120" alt="SnapForge" style="border-radius: 24px;">
</picture>

# SnapForge

### Professional Image Processing Platform

**A powerful modern image processing platform supporting batch processing, format conversion, filter effects, watermarks, intelligent duplicate detection, and complete image processing workflows**

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

[中文](README.md) · [Quick Start](#quick-start) · [Features](#features) · [Architecture](#architecture)

---

## Key Advantages

| Feature | Description |
|---------|-------------|
| 🚀 **High Performance** | Concurrent processing engine, support 1-10 images simultaneously |
| 🔒 **Secure & Reliable** | Magic Number validation, rate limiting, path traversal protection |
| 📦 **Batch Processing** | Process hundreds of images with auto queue management |
| 🎨 **Rich Filters** | 15+ built-in filters with custom color adjustments |
| 🧠 **Smart Deduplication** | Perceptual hash algorithm for quick similar/duplicate detection |
| 🌐 **Bilingual** | Chinese/English interface with one-click switch |

---

## Features

### Core Image Processing

| Feature | Description | Supported Formats |
|---------|-------------|-------------------|
| **Format Conversion** | Convert between popular formats with quality control | JPEG, PNG, WebP, AVIF, TIFF, GIF, BMP |
| **Resize** | Smart scaling with multiple fit modes | Fit/Fill/Stretch/Crop |
| **Smart Crop** | Custom crop areas with preset ratios | 1:1, 16:9, 4:3, 3:2, 2:1, Custom |
| **Rotate & Flip** | Arbitrary angle rotation, horizontal/vertical flip | - |
| **Filter Effects** | 15+ professional filters one-click apply | Grayscale, Vintage, Sharpen, Blur, Emboss, etc. |
| **Color Adjustment** | Fine-tune brightness/contrast/saturation | Range 0-10 |
| **Watermark** | Text/image watermarks with multiple position modes | 9-grid + Tile |
| **Border Decoration** | Custom border width, color, rounded corners | - |

### Advanced Features

- **Batch Processing** - Process hundreds of images with concurrency control
- **Processing Schemes** - Preset schemes one-click apply, custom scheme save/import/export
- **Duplicate Detection** - Perceptual hash algorithm with configurable similarity threshold
- **Statistics Dashboard** - Visual dashboard tracking processing trends, efficiency, success rate
- **Image Comparison** - Slider/overlay/side-by-side comparison modes with zoom
- **EXIF Information** - Complete display of shooting parameters, metadata

### User Experience

- **Multiple Upload** - Drag & drop, paste, and click to upload
- **Real-time Preview** - Processing effects visible instantly
- **Keyboard Shortcuts** - Ctrl+V paste, Ctrl+A select all, Delete remove
- **Batch Download** - One-click ZIP download
- **Theme Toggle** - Dark/Light mode auto-follows system
- **Responsive Design** - Perfect adaptation for desktop, tablet, and mobile

---

## Quick Start

### Requirements

| Environment | Requirement |
|-------------|-------------|
| **Node.js** | >= 18.0 |
| **pnpm** | >= 9.0 |

### Installation

```bash
# Clone the repository
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Open browser http://localhost:5000
```

### Production Deployment

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

---

## Architecture

### Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Framework** | Next.js (App Router) | 16.1.1 |
| **UI Library** | React | 19.2.3 |
| **Language** | TypeScript | 5.0 |
| **Styling** | Tailwind CSS + shadcn/ui | 4.0 |
| **State Management** | Zustand (Persisted) | - |
| **Image Processing** | Sharp (libvips) | - |

### Project Structure

```
SnapForge/
├── src/
│   ├── app/
│   │   ├── api/                  # API Routes
│   │   ├── layout.tsx             # Root layout
│   │   └── page.tsx               # Home page
│   ├── components/
│   │   ├── ui/                    # shadcn/ui base components
│   │   ├── ImageUploader.tsx       # Image upload
│   │   ├── ProcessConfigPanel.tsx # Processing config
│   │   ├── ProcessingPanel.tsx     # Processing panel
│   │   ├── ImageCompare.tsx        # Image comparison
│   │   ├── DuplicateDetector.tsx   # Duplicate detection
│   │   └── StatsDashboard.tsx      # Statistics dashboard
│   ├── lib/
│   │   ├── image-processor.ts      # Image processing core
│   │   ├── i18n.ts                # Internationalization
│   │   └── utils.ts               # Utilities
│   ├── store/                     # State management
│   └── types/                     # TypeScript types
├── public/                        # Static assets
├── package.json
├── tailwind.config.ts
└── README.md
```

---

## Security

- **Magic Number Validation** - File header byte verification
- **File Size Limit** - Max 50MB per file
- **Safe Filenames** - Path traversal character removal
- **Rate Limiting** - Abuse prevention

---

## Contributing

Issues and Pull Requests are welcome!

## License

[MIT License](LICENSE)

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/riceshowerX">riceshowerX</a>
</p>
</div>
