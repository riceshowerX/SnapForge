import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  // 解决多 lockfile 警告，设置 workspace root
  outputFileTracingRoot: path.resolve(__dirname),
  
  // 允许的开发环境域名
  allowedDevOrigins: ['*.dev.coze.site'],
  
  // 图片域名配置
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lf-coze-web-cdn.coze.cn',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
