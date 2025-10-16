/**
 * RepoLens Frontend - Reveal Component
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

import { motion } from 'motion/react';

export interface RevealProps extends React.ComponentProps<'div'> {
  children: React.ReactNode;
  width?: 'fit-content' | '100%';
  delay?: number;
  slideDirection?: 'top' | 'bottom' | 'left' | 'right';
}

export const Reveal = ({
  children,
  width = 'fit-content',
  delay = 0.25,
  slideDirection = 'bottom',
}: RevealProps) => {
  const variants = (() => {
    switch (slideDirection) {
      case 'top':
        return {
          hidden: { opacity: 0, y: -75, x: 0 },
          visible: { opacity: 1, y: 0, x: 0 },
        };
      case 'left':
        return {
          hidden: { opacity: 0, y: 0, x: -75 },
          visible: { opacity: 1, y: 0, x: 0 },
        };
      case 'right':
        return {
          hidden: { opacity: 0, y: 0, x: 75 },
          visible: { opacity: 1, y: 0, x: 0 },
        };
      default:
        return {
          hidden: { opacity: 0, y: 75, x: 0 },
          visible: { opacity: 1, y: 0, x: 0 },
        };
    }
  })();

  return (
    <div
      style={{
        position: 'relative',
        width,
        overflow: 'hidden',
      }}
    >
      <motion.div
        variants={variants}
        initial='hidden'
        animate='visible'
        transition={{ duration: 0.5, delay }}
      >
        {children}
      </motion.div>
    </div>
  );
};
