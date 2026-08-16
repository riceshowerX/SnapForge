'use client';

import { useEffect } from 'react';

// Q-04：global-error.tsx 必须独立实现并渲染 <html><body>（根布局不会包裹它）。
// 不 re-export error.tsx；不展示 error.message 原始内容。
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Global application error:', error);
  }, [error]);

  return (
    <html lang="zh-CN">
      <body
        style={{
          margin: 0,
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily:
            'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
          background: '#fafafa',
          color: '#1f2937',
          padding: '1rem',
        }}
      >
        <div style={{ maxWidth: 420, width: '100%', textAlign: 'center' }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              fontSize: 32,
            }}
          >
            ⚠️
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: '0 0 0.5rem' }}>
            Something went wrong
          </h1>
          <p
            style={{
              fontSize: 14,
              color: '#6b7280',
              margin: '0 0 0.25rem',
              lineHeight: 1.6,
            }}
          >
            The application encountered an unexpected error. Please refresh the
            page and try again.
          </p>
          {error.digest && (
            <p
              style={{
                fontSize: 12,
                color: '#9ca3af',
                margin: '0 0 1.5rem',
              }}
            >
              Error ID: {error.digest}
            </p>
          )}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button
              type="button"
              onClick={() => (window.location.href = '/')}
              style={{
                padding: '0.5rem 1.25rem',
                borderRadius: 8,
                border: '1px solid #d1d5db',
                background: '#ffffff',
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              Back to Home
            </button>
            <button
              type="button"
              onClick={reset}
              style={{
                padding: '0.5rem 1.25rem',
                borderRadius: 8,
                border: 'none',
                background: '#8b5cf6',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              Retry
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
