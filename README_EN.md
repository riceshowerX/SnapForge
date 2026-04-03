<div align="center">

# <img src="public/logo.png" width="60" height="60" alt="SnapForge Logo"> SnapForge

**Professional Image Processing Platform**

A modern professional image processing platform supporting batch processing, format conversion, filter effects, watermarks, and more

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[中文文档](README.md) · [Live Demo](#) · [Features](#-features) · [Quick Start](#-quick-start) · [Architecture](#-architecture)

</div>

---

## ✨ Features

### 🖼️ Core Image Processing

| Feature | Description |
|---------|-------------|
| **Format Conversion** | Support for JPEG, PNG, WebP, AVIF, TIFF, GIF and other mainstream formats |
| **Resize** | Smart scaling with multiple modes (fit, fill, stretch, crop) |
| **Smart Crop** | Custom crop areas with preset ratios (1:1, 16:9, 4:3, etc.) |
| **Rotate & Flip** | Arbitrary angle rotation, horizontal/vertical flip support |
| **Filter Effects** | Grayscale, vintage, sharpen, blur, emboss, edge detection and 10+ filters |
| **Color Adjustment** | Fine-tune brightness, contrast, saturation, sharpness |
| **Watermark** | Text/image watermarks with position, opacity, and tile mode support |
| **Border Decoration** | Custom border width, color, and rounded corners |

### 🚀 Advanced Features

- **Batch Processing** - Process hundreds of images at once with automatic queue management
- **Processing Schemes** - One-click preset application, custom scheme save/import/export
- **Duplicate Detection** - Smart perceptual hash algorithm for quick similar/duplicate image identification
- **Statistics Dashboard** - Visual dashboard tracking processing trends and efficiency
- **Image Comparison** - Slider/overlay/side-by-side three comparison modes
- **EXIF Information** - Complete display of shooting parameters and metadata

### 💻 User Experience

- **Drag & Drop Upload** - Support for drag, paste, and click upload methods
- **Real-time Preview** - Processing effects visible instantly
- **Keyboard Shortcuts** - Ctrl+V paste, Ctrl+A select all, Delete to remove
- **Batch Download** - One-click ZIP download of all processed results
- **Dark Mode** - Eye-friendly theme auto-switching
- **Responsive Design** - Perfect adaptation for desktop and mobile devices

---

## 📸 Screenshots

<details>
<summary>Click to expand screenshots</summary>

### Main Interface
![Main Interface](./screenshots/main.png)

### Processing Config Panel
![Config Panel](./screenshots/config.png)

### Image Comparison
![Image Comparison](./screenshots/compare.png)

### Statistics Dashboard
![Statistics Dashboard](./screenshots/stats.png)

</details>

---

## 🛠️ Quick Start

### Requirements

- Node.js 18.0 or higher
- pnpm 9.0 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/riceshowerX/SnapForge.git
cd SnapForge

# Install dependencies
pnpm install
```

### Development Mode

```bash
# Start development server
pnpm dev
```

Open [http://localhost:5000](http://localhost:5000) to view the application.

### Production Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

---

## 🏗️ Architecture

### Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | Next.js 16 (App Router) |
| **UI Library** | React 19 |
| **Language** | TypeScript 5 |
| **Styling** | Tailwind CSS 4 + shadcn/ui |
| **State Management** | Zustand |
| **Image Processing** | Sharp (libvips) |
| **Charts** | Recharts |
| **Batch Download** | JSZip |

### Project Structure

```
SnapForge/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API Routes
│   │   │   ├── upload/        # File upload endpoint
│   │   │   ├── process/       # Image processing endpoint
│   │   │   └── duplicates/    # Duplicate detection endpoint
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui base components
│   │   ├── ImageUploader.tsx # Image upload component
│   │   ├── ProcessConfigPanel.tsx # Config panel
│   │   ├── ProcessingPanel.tsx    # Processing panel
│   │   ├── ImageCompare.tsx      # Image comparison
│   │   ├── ExifPanel.tsx         # EXIF panel
│   │   ├── SchemeManager.tsx     # Scheme manager
│   │   └── StatsDashboard.tsx    # Statistics dashboard
│   ├── lib/                   # Utilities
│   │   ├── image-processor.ts # Core image processing
│   │   └── utils.ts          # General utility functions
│   ├── store/                 # State management
│   │   └── index.ts          # Zustand Store
│   └── types/                 # TypeScript definitions
│       └── index.ts          # Global types
├── public/                    # Static assets
└── package.json              # Project configuration
```

### Core Modules

#### Image Processing Flow

```mermaid
graph LR
    A[Upload Image] --> B[Validate Format]
    B --> C[Read Metadata]
    C --> D[Apply Config]
    D --> E[Process Image]
    E --> F[Output Result]
```

#### Processing Pipeline

1. **Crop** → 2. **Rotate** → 3. **Scale** → 4. **Effects** → 5. **Filters** → 6. **Border** → 7. **Watermark** → 8. **Format Conversion**

---

## 📖 API Documentation

### POST /api/upload

Upload image and get preview information

**Request**: `multipart/form-data`
- `file`: Image file

**Response**:
```json
{
  "name": "image.jpg",
  "size": 1024000,
  "type": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "preview": "data:image/jpeg;base64,..."
}
```

### POST /api/process

Process a single image

**Request**: `multipart/form-data`
- `file`: Image file
- `config`: JSON format processing configuration

**Response**: Processed image binary data

### POST /api/duplicates

Detect duplicate/similar images

**Request**: `multipart/form-data`
- `files[]`: Multiple image files
- `threshold`: Similarity threshold (0.5-1.0)

**Response**:
```json
{
  "groups": [
    {
      "id": "group-1",
      "images": [...],
      "similarity": 0.95
    }
  ],
  "totalScanned": 10,
  "duplicatesFound": 3
}
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| `Ctrl + V` | Paste image from clipboard |
| `Ctrl + A` | Select/deselect all images |
| `Delete` | Delete selected images |
| `Ctrl + Enter` | Start processing |

---

## 🔒 Security Features

- **File Type Validation** - Verify real file type via Magic Number
- **File Size Limit** - Prevent large file attacks
- **Input Validation** - Strict validation of all API parameters
- **Secure Filenames** - Prevent path traversal attacks
- **Error Handling** - No exposure of internal implementation details

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Development Guidelines

- Use ESLint and TypeScript for code checking
- Follow Conventional Commits specification
- New features require corresponding tests

---

## 📝 Changelog

### v1.0.0 (2024-01)

- ✨ Initial release
- 🖼️ Complete image processing features
- 🎨 Professional UI design
- 📊 Statistics dashboard
- 🔧 Processing scheme management

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by [riceshowerX](https://github.com/riceshowerX)**

</div>
