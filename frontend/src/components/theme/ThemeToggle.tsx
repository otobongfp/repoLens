/**
 * RepoLens Frontend - Themetoggle Component
 * 
 * Copyright (C) 2024 RepoLens Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
