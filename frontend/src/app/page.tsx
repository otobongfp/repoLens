/**
 * RepoLens Frontend - Page
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

import Hero from './components/Hero';

export default function Home() {
  return (
    <div className='bg-background relative flex min-h-screen flex-col overflow-auto overflow-x-hidden'>
      <main className='relative z-10 flex flex-1 flex-col items-center px-4'>
        <Hero />
      </main>
    </div>
  );
}
