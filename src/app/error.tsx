'use client';

import { useEffect, useCallback } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/store';
import { t } from '@/lib/i18n';

// Q-04：不展示 error.message 原始内容（可能含内部路径等敏感信息），
// 仅展示通用文案 + digest，便于排查。
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { language } = useAppStore();

  const tr = useCallback(
    (key: Parameters<typeof t>[1], params?: Record<string, string | number>) =>
      t(language, key, params),
    [language]
  );

  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
          <AlertCircle className="w-8 h-8 text-destructive" />
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">{tr('errorTitle')}</h2>
          <p className="text-sm text-muted-foreground">{tr('errorGeneric')}</p>
          {error.digest && (
            <p className="text-xs text-muted-foreground/70 mt-2">
              {tr('errorDigest')}: {error.digest}
            </p>
          )}
        </div>
        <div className="flex gap-3 justify-center">
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/')}
          >
            {tr('errorHome')}
          </Button>
          <Button onClick={reset}>
            <RefreshCw className="w-4 h-4 mr-2" />
            {tr('errorRetry')}
          </Button>
        </div>
      </div>
    </div>
  );
}
