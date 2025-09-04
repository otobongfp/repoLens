'use client';

import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Moon, Sun } from 'lucide-react';

export function ThemeToggle() {
  const { setTheme, theme } = useTheme();

  return (
    <Button
      variant='outline'
      size='icon'
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? (
        <Sun className='text-foreground size-[1.2rem] transition-all' />
      ) : (
        <Moon className='text-foreground size-[1.2rem] transition-all' />
      )}
      <span className='sr-only'>Toggle theme</span>
    </Button>
  );
}
