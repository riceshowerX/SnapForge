# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Measures

### File Upload Security
- **Magic Number Validation**: All uploaded files are validated by their file signature (Magic Number), not just MIME type
- **File Size Limits**: Maximum 50MB per file, 200MB total per request
- **File Name Sanitization**: Path traversal attacks are prevented by sanitizing file names
- **Content Type Validation**: Only accepted content types are processed

### API Security
- **Input Validation**: All API parameters are strictly validated
- **Rate Limiting**: Built-in protection against abuse
- **Error Handling**: Internal errors are not exposed to users

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
- Always validate user input
- Use parameterized queries for database operations
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
