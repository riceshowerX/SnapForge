<div align="center">

# <img src="public/logo.png" width="80" height="80" alt="SnapForge Logo"> SnapForge

### Professional Image Processing Platform

**A powerful modern image processing platform supporting batch processing, format conversion, filter effects, watermarks, intelligent duplicate detection, and complete image processing workflows**

[![Next.js](https://img.shields.io/badge/Next.js-16.1.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

[Live Demo](https://snapforge.dev.coze.site) · [中文](README.md) · [Quick Start](#quick-start) · [Features](#features) · [Technical Docs](#technical-documentation)

---

## 🎯 Key Advantages

| Feature | Description |
|---------|-------------|
| 🚀 **High Performance** | Concurrent processing engine, support 1-10 images simultaneously |
| 🔒 **Secure & Reliable** | Magic Number validation, rate limiting, path traversal protection |
| 📦 **Batch Processing** | Process hundreds of images with auto queue management |
| 🎨 **Rich Filters** | 15+ built-in filters with custom color adjustments |
| 🧠 **Smart Deduplication** | Perceptual hash algorithm for quick similar/duplicate detection |
| 💾 **Data Persistence** | Local storage for task history, scheme sync |

</div>

---

## ✨ Features

### 🖼️ Core Image Processing

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

### 🚀 Advanced Features

- **Batch Processing** - Process hundreds of images with concurrency control and error interruption options
- **Processing Schemes** - 5 preset schemes one-click apply, custom scheme save/import/export
- **Duplicate Detection** - Perceptual hash algorithm with configurable similarity threshold (0.5-1.0)
- **Statistics Dashboard** - Visual dashboard tracking processing trends, efficiency, success rate, and feature usage
- **Image Comparison** - Slider/overlay/side-by-side comparison modes with zoom and fullscreen support
- **EXIF Information** - Complete display of shooting parameters, focal length, aperture, ISO, etc.

### 💻 User Experience

- **Multiple Upload** - Drag & drop, paste, and click to upload
- **Real-time Preview** - Processing effects visible instantly
- **Keyboard Shortcuts** - Ctrl+V paste, Ctrl+A select all, Delete remove, Ctrl+Enter process
- **Batch Download** - One-click ZIP download all processed results
- **Theme Toggle** - Dark/Light mode auto-follows system
- **Responsive Design** - Perfect adaptation for desktop, tablet, and mobile

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

## 🚀 Quick Start

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
# 1. Build for production
pnpm build

# 2. Start production server
pnpm start

# 3. Server runs at http://localhost:5000
```

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server listening port | `5000` |

---

## 🏗️ Architecture

### Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Framework** | Next.js (App Router) | 16.1.1 |
| **UI Library** | React | 19.2.3 |
| **Language** | TypeScript | 5.0 |
| **Styling** | Tailwind CSS + shadcn/ui | 4.0 |
| **State Management** | Zustand (Persisted) | - |
| **Image Processing** | Sharp (libvips) | - |
| **Charts** | Recharts | - |
| **Batch Download** | JSZip | - |
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
│   │   ├── ProcessingPanel.tsx       # Processing panel (with concurrency)
│   │   ├── ImageCompare.tsx          # Image comparison component
│   │   ├── ExifPanel.tsx            # EXIF information panel
│   │   ├── SchemeManager.tsx         # Scheme management component
│   │   ├── StatsDashboard.tsx        # Statistics dashboard
│   │   ├── DuplicateDetector.tsx    # Duplicate detection component
│   │   ├── ThemeToggle.tsx          # Theme toggle
│   │   └── ProcessingHistory.tsx    # Processing history
│   │
│   ├── lib/                         # Utilities
│   │   ├── image-processor.ts       # Core image processing logic
│   │   ├── utils.ts                 # General utilities
│   │   ├── api-response.ts          # Unified API response format
│   │   └── rate-limit.ts            # Request rate limiting
│   │
│   ├── store/                       # State Management
│   │   └── index.ts                 # Zustand Store (Persisted)
│   │
│   └── types/                        # TypeScript Definitions
│       └── index.ts                 # Global types and interfaces
│
├── public/                           # Static Assets
│   └── logo.png                      # Project logo
│
├── scripts/                           # Build Scripts
│   ├── build.sh
│   ├── dev.sh
│   └── start.sh
│
├── package.json                       # Project configuration
├── tsconfig.json                      # TypeScript configuration
├── .coze                             # Coze deployment config
└── README.md                          # Project documentation
```

### Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      Image Processing Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│  1. Validate ──→ 2. Crop ──→ 3. Rotate ──→ 4. Scale ──→ 5. Effects │
│  6. Filter ──→ 7. Border ──→ 8. Watermark ──→ 9. Convert ──→ 10. Output │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 API Documentation

### Unified Response Format

All API responses use a unified JSON format:

```typescript
// Success Response
{
  "success": true,
  "data": { ... },
  "timestamp": 1709900000000
}

// Error Response
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  },
  "timestamp": 1709900000000
}
```

### Error Codes

| Error Code | Description |
|------------|-------------|
| `UNKNOWN_ERROR` | Unknown error |
| `INVALID_REQUEST` | Invalid request |
| `FILE_TOO_LARGE` | File too large |
| `INVALID_FILE_TYPE` | Invalid file type |
| `FILE_SIGNATURE_MISMATCH` | File content doesn't match declared type |
| `INVALID_CONFIG` | Invalid configuration |
| `PROCESSING_FAILED` | Processing failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

### POST /api/upload

Upload image and get preview information with metadata.

**Request**: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ | Image file, max 50MB |

**Rate Limit**: 30 requests/minute

**Response Example**:

```json
{
  "success": true,
  "data": {
    "name": "photo.jpg",
    "size": 2048000,
    "type": "image/jpeg",
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "hasAlpha": false,
    "preview": "data:image/jpeg;base64,..."
  },
  "timestamp": 1709900000000
}
```

---

### POST /api/process

Process a single image.

**Request**: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ | Image file, max 50MB |
| `config` | string | ✅ | JSON format processing configuration |
| `counter` | number | ❌ | Counter for batch naming |

**Rate Limit**: 20 requests/minute

**Response**: Processed image binary data

**Response Headers**:

```
Content-Type: image/[format]
Content-Disposition: attachment; filename="processed_1.jpg"
X-Image-Width: 1920
X-Image-Height: 1080
X-Image-Size: 1024000
```

---

### POST /api/duplicates

Detect duplicate or similar images.

**Request**: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | ✅ | Array of image files, max 100 |
| `threshold` | number | ❌ | Similarity threshold (0.5-1.0), default 0.9 |

**Rate Limit**: 10 requests/minute

**Response Example**:

```json
{
  "success": true,
  "data": {
    "groups": [
      {
        "id": "uuid-group-1",
        "images": [
          { "id": "uuid-1", "name": "photo1.jpg", "size": 2048, "type": "image/jpeg" },
          { "id": "uuid-2", "name": "photo2.jpg", "size": 2048, "type": "image/jpeg" }
        ],
        "similarity": 0.95,
        "hash": "perceptual_hash_value"
      }
    ],
    "totalScanned": 10,
    "duplicatesFound": 2
  },
  "timestamp": 1709900000000
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
| `Esc` | Close preview/modal |

---

## 🔒 Security Features

### File Security

| Feature | Description |
|---------|-------------|
| **Magic Number Validation** | Verify real file type via file header bytes, prevent spoofing |
| **File Size Limit** | Single file max 50MB, total request body max 100MB |
| **Secure Filename** | Remove path traversal chars, Unicode control chars, limit to 255 chars |
| **Unicode Normalization** | Prevent NFC/NFD normalization attacks |

### Request Security

| Feature | Description |
|---------|-------------|
| **Rate Limiting** | IP-based request throttling, separate limits per endpoint |
| **Parameter Validation** | Strict range validation for all config parameters |
| **Error Isolation** | No internal error details exposed to client |

### Data Security

| Feature | Description |
|---------|-------------|
| **Local Storage** | Data only stored in browser localStorage |
| **Data Stripping** | History auto-strips large binary data |
| **Capacity Management** | Auto cleanup old data to prevent storage overflow |

---

## ⚡ Performance Optimization

### Frontend Optimization

| Optimization | Implementation |
|--------------|----------------|
| **Large Image Preview** | >2MB images auto-generate 800x800 thumbnail |
| **Concurrent Processing** | Configurable 1-10 images simultaneous processing |
| **Memory Management** | Use ref to track Blob URLs, auto-release on unmount |
| **State Optimization** | Use zustand getState() to avoid unnecessary re-renders |
| **Batch Fetching** | Parallel image blob fetching, max 10 concurrent |

### Backend Optimization

| Optimization | Implementation |
|--------------|----------------|
| **Streaming Processing** | Use Sharp streaming API |
| **Lazy Loading** | On-demand import of heavy modules |
| **Cache Strategy** | Disable browser cache for fresh data |

---

## 🔧 Configuration Reference

### Processing Config Structure

```typescript
interface ProcessConfig {
  convert: {
    enabled: boolean;
    format: 'jpeg' | 'png' | 'webp' | 'avif';
    quality: number;      // 1-100
    progressive: boolean;
    optimize: boolean;
  };
  resize: {
    enabled: boolean;
    width: number;        // 1-20000
    height: number;       // 1-20000
    mode: 'contain' | 'cover' | 'stretch' | 'fill';
    onlyShrink: boolean;
  };
  crop: {
    enabled: boolean;
    x: number;
    y: number;
    width: number;        // 1-50000
    height: number;       // 1-50000
    aspectRatio: string;
    preset: 'custom' | 'square' | '16:9' | '4:3' | '3:2' | '2:1';
  };
  rotate: {
    enabled: boolean;
    angle: number;
    expand: boolean;
    fillColor: string;
    flip: boolean;
    flop: boolean;
  };
  filter: {
    enabled: boolean;
    type: FilterType;
    intensity: number;    // 0-10
  };
  effects: {
    enabled: boolean;
    brightness: number;   // 0-10
    contrast: number;     // 0-10
    saturation: number;   // 0-10
  };
  watermark: {
    enabled: boolean;
    text: string;
    position: WatermarkPosition;
    opacity: number;
    fontSize: number;
    color: string;
  };
  border: {
    enabled: boolean;
    width: number;        // 0-100
    color: string;
    radius: number;
  };
  compression: {
    enabled: boolean;
    level: number;        // 1-100
  };
  preserveMetadata: boolean;
}
```

### Preset Processing Schemes

| Scheme Name | Use Case | Main Config |
|-------------|----------|-------------|
| **Web Optimized** | Web images | WebP format, quality 85%, width 1920 |
| **Thumbnail** | Gallery preview | JPEG format, quality 75%, 400x400 |
| **Social Media** | Social platforms | JPEG format, quality 90%, 1080x1080 |
| **Watermark Protect** | Copyright protection | Add text watermark |
| **Print Ready** | Print quality | PNG format, quality 100%, 300 DPI |

---

## ❓ FAQ

### Q: Image upload failed?

**Possible Causes**:
1. File size exceeds 50MB
2. File format not supported
3. Network connection interrupted
4. Too many requests (rate limit triggered)

**Solutions**:
- Compress image size and retry
- Use supported format (JPEG, PNG, WebP, GIF, BMP, TIFF)
- Wait 1 minute and retry

### Q: Processing is slow?

**Possible Causes**:
1. Image file is too large
2. Multiple processing operations enabled
3. Concurrency setting too low

**Solutions**:
- Use preset schemes to reduce image size
- Reduce number of simultaneous processing options
- Increase concurrency in settings (default 3)

### Q: Duplicate detection not accurate?

**Possible Causes**:
1. Similarity threshold set too high
2. Images were compressed or format converted

**Solutions**:
- Lower similarity threshold (default 0.9, can reduce to 0.7-0.8)
- For screenshots or re-compressed images, use lower threshold

### Q: Dark mode not working?

**Solutions**:
- Confirm browser supports prefers-color-scheme
- Click theme toggle button in top-right corner

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Development Guidelines

```bash
# 1. Install dependencies
pnpm install

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Write code (auto ESLint + TypeScript check)
pnpm lint
pnpm ts-check

# 4. Commit (follow Conventional Commits)
git commit -m "feat: add new processing filter"

# 5. Push and create PR
git push origin feature/my-feature
```

### Commit Message Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation update
style:    Code formatting (no functional change)
refactor: Code refactoring
perf:     Performance improvement
test:     Test related
chore:    Build/tool related
```

---

## 📝 Changelog

### [v1.1.0] - 2024-04

#### New Features
- ✨ Concurrent processing engine, support 1-10 images simultaneously
- ✨ Unified API response format and error code specification
- ✨ Request rate limiting to prevent abuse
- ✨ Enhanced filename security (Unicode normalization)

#### Improvements
- 🚀 Batch image fetching optimization (parallel + cache)
- 🚀 Use zustand getState() for render performance optimization
- 🐛 Fixed SchemeManager hydration mismatch
- 🐛 Fixed ImageCompare dragging state staleness

#### Security Enhancements
- 🔒 Added request rate limiting (separate limits per endpoint)
- 🔒 Enhanced path traversal protection (Unicode control char filtering)

### [v1.0.0] - 2024-01

- ✨ Initial release
- 🖼️ Complete image processing (convert, crop, filters, watermark, etc.)
- 🎨 Professional UI design
- 📊 Statistics dashboard
- 🔧 Processing scheme management
- 🔍 Duplicate image detection

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

Special thanks to these open-source projects:

- [Next.js](https://nextjs.org/) - React Framework
- [Sharp](https://sharp.pixelmatter.com/) - High-performance Image Processing
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS Framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI Components
- [Zustand](https://zustand-demo.pmnd.rs/) - Lightweight State Management

---

<div align="center">

**Made with ❤️ by [riceshowerX](https://github.com/riceshowerX)**

**If you find this project helpful, please give a ⭐ to show your support!**

[![GitHub stars](https://img.shields.io/github/stars/riceshowerX/SnapForge?style=social)](https://github.com/riceshowerX/SnapForge)

</div>
