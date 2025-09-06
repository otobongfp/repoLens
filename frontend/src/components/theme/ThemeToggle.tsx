'use client';

import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Moon, Sun } from 'lucide-react';
import {
  useThemeAnimation,
  ThemeAnimationType,
} from '@space-man/react-theme-animation';

export function ThemeToggle() {
  const { theme, ref, toggleTheme } = useThemeAnimation({
    duration: 1000,
    animationType: ThemeAnimationType.CIRCLE,
  });

  return (
    <Button variant='outline' size='icon' onClick={toggleTheme} ref={ref}>
      {theme === 'light' ? (
        <Sun className='text-foreground size-[1.2rem] transition-all' />
      ) : (
        <Moon className='text-foreground size-[1.2rem] transition-all' />
      )}
      <span className='sr-only'>Toggle theme</span>
    </Button>
  );
}
