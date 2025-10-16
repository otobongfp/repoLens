/**
 * RepoLens Frontend - Ctabutton Component
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

import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

interface CTAButtonProps extends React.ComponentProps<'button'> {}

export const CTAButton = ({ className, children }: CTAButtonProps) => {
  return (
    <motion.button
      className={cn(
        'radial-gradient rounded-xs relative cursor-pointer px-8 py-4',
        className,
      )}
      initial={{ '--x': '100%', scale: 1 }}
      animate={{ '--x': '-100%' }}
      whileTap={{ scale: 0.97 }}
      transition={{
        repeat: Infinity,
        repeatType: 'loop',
        repeatDelay: 1,
        type: 'spring',
        stiffness: 20,
        damping: 15,
        mass: 2,
        scale: {
          type: 'spring',
          stiffness: 10,
          damping: 5,
          mass: 0.1,
        },
      }}
    >
      <span className='linear-mask relative block h-full w-full font-normal tracking-wide text-white'>
        {children}
      </span>
      <span className='linear-overlay rounded-xs absolute inset-0 block p-[2px]' />
    </motion.button>
  );
};
