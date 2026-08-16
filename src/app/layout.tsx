import type { Metadata, Viewport } from 'next';
import { ThemeProvider } from 'next-themes';
import { Inspector } from 'react-dev-inspector';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'SnapForge - 专业图像处理平台',
    template: '%s | SnapForge',
  },
  description:
    'SnapForge 是一个强大、优雅且开源的图像处理平台，提供格式转换、智能重命名、批量处理、重复检测等功能。',
  keywords: [
    'SnapForge',
    '图像处理',
    '批量处理',
    '格式转换',
    '图片压缩',
    '水印',
    '重复检测',
    '开源',
  ],
  authors: [{ name: 'riceshowerX', url: 'https://github.com/riceshowerX' }],
  generator: 'Next.js',
  icons: {
    icon: '/favicon.ico',
  },
  openGraph: {
    title: 'SnapForge - 专业图像处理平台',
    description:
      '高效、专业、美观的批量图片处理平台。格式转换、智能重命名、批量处理，一切尽在掌控。',
    // Q-05：修正历史遗留的 streamlit 站点地址，改为 GitHub 仓库
    url: 'https://github.com/riceshowerX/SnapForge',
    siteName: 'SnapForge',
    locale: 'zh_CN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SnapForge - 专业图像处理平台',
    description: '高效、专业、美观的批量图片处理平台',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const isDev = process.env.NODE_ENV === 'development';

  return (
    // Q-05：lang 由客户端组件（page.tsx effect）按语言动态更新
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={`antialiased min-h-screen`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {isDev && <Inspector />}
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
