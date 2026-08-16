'use client';

import { useEffect, useState, useCallback } from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/store';
import { t } from '@/lib/i18n';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const { language } = useAppStore();
  const [mounted, setMounted] = useState(false);

  const tr = useCallback(
    (key: Parameters<typeof t>[1]) => t(language, key),
    [language]
  );

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    setMounted(true);
  }, []);
  /* eslint-enable react-hooks/set-state-in-effect */

  if (!mounted) {
    return (
      <Button variant="ghost" size="icon" className="h-8 w-8">
        <Sun className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          {theme === 'light' ? (
            <Sun className="h-4 w-4" />
          ) : theme === 'dark' ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Monitor className="h-4 w-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[120px]">
        <DropdownMenuItem onClick={() => setTheme('light')} className="text-xs">
          <Sun className="mr-2 h-3.5 w-3.5" />
          {tr('light')}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')} className="text-xs">
          <Moon className="mr-2 h-3.5 w-3.5" />
          {tr('dark')}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme('system')}
          className="text-xs"
        >
          <Monitor className="mr-2 h-3.5 w-3.5" />
          {tr('system')}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
