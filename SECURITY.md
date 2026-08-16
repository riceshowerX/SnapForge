# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Measures

### File Upload Security
- **Magic Number Validation**: All uploaded files are validated by their file signature (Magic Number), not just MIME type — the client MIME type is never trusted
- **File Size Limits**: Maximum 50MB per file; upload/process request bodies capped at 55MB, duplicates at 105MB (rejected with 413 before parsing)
- **File Name Sanitization**: Path traversal, Windows reserved device names (CON, NUL, COM1...), control characters, full-width separators and Unicode NFC normalization are all handled
- **Content Type Validation**: Only JPEG / PNG / WebP / GIF are accepted; SVG / PDF and other vector formats are rejected to reduce the attack surface
- **Decode Guardrails**: Every sharp entry point sets explicit `limitInputPixels` (64M) and `failOn: 'error'` to mitigate decompression bombs

### API Security
- **SSRF Protection**: Watermark remote image URLs are restricted to http/https; all private / reserved IP ranges (including IPv6 and IPv4-mapped) are blocked after DNS resolution; fetches have a 5s timeout, manual redirect handling (max 2 hops) with re-validation on every hop
- **Input Validation**: All API parameters are validated at runtime with a zod schema (nested numeric ranges); invalid config returns a friendly 400, never a 500
- **Rate Limiting**: Keyed by the real connection IP (forged `X-Forwarded-For` headers are ignored); bounded in-memory store with capacity limit and probabilistic cleanup
- **Error Handling**: Internal errors are never exposed to users; error pages show generic messages plus a digest

### Dependency Security
We use pnpm overrides to ensure all dependencies use secure versions:

```json
{
  "pnpm": {
    "overrides": {
      "axios": "^1.8.4",
      "cross-spawn": "^7.0.6",
      "path-to-regexp": "^6.3.0",
      "postcss": "^8.4.49",
      "semver": "^7.7.4"
    }
  }
}
```

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainer at the GitHub security advisory
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Possible impact
   - Suggested fix (if any)

We will respond within 48 hours and provide a timeline for the fix.

## Security Best Practices

### For Developers
- Always validate user input (use the shared zod schema & file-validation utilities)
- Keep dependencies updated
- Review code for potential XSS, CSRF, and injection vulnerabilities

### For Users
- Only upload images from trusted sources
- Be cautious when processing images from unknown origins
- Report any suspicious behavior

## Known Security Considerations

### Image Processing
- This application uses `sharp` (libvips) for image processing
- Large images may consume significant memory
- Malformed images are rejected before processing

### Data Privacy
- All processing happens locally on your server
- No data is sent to external services
- No tracking or analytics are included by default

## Dependency Audit

Run security audit locally:
```bash
pnpm audit
```

Update dependencies:
```bash
pnpm update
```

Check for outdated packages:
```bash
pnpm outdated
```
