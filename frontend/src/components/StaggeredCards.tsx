/**
 * RepoLens Frontend - Staggeredcards Component
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

import React from 'react';

export interface StaggeredCardsProps {
  children: React.ReactNode;
}

const StaggeredCards: React.FC<StaggeredCardsProps> = ({ children }) => {
  return (
    <div className='relative origin-center -translate-x-3 rotate-6 p-6 duration-500 hover:rotate-0'>
      <span className='border-primary bg-card/10 hover:bg-card/15 absolute inset-0 border border-dashed'></span>
      <p className='text-muted-foreground'>{children}</p>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute left-[-2px] top-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute right-[-2px] top-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute bottom-[-2px] left-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute bottom-[-2px] right-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
    </div>
  );
};

export default StaggeredCards;
