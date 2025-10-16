/**
 * RepoLens Frontend - Dotbackground Component
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

import { cn } from '@/lib/utils';

const DotBackground = ({ className }: React.ComponentProps<'div'>) => {
  return (
    <div className={cn('absolute inset-0', className)}>
      <div className='relative h-full w-full [&>div]:absolute [&>div]:h-full [&>div]:w-full [&>div]:bg-[radial-gradient(var(--border)_1px,transparent_1px)] [&>div]:[background-size:16px_16px]'>
        <div></div>
      </div>
    </div>
  );
};

export default DotBackground;
