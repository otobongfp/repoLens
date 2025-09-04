'use client';
import { SearchCode } from 'lucide-react';
import { useRepolensApi } from '../utils/api';
import Link from 'next/link';
import { ThemeToggle } from '@/components/theme/ThemeToggle';

export default function Navbar({ children }: { children?: React.ReactNode }) {
  const { isLocal } = useRepolensApi();

  return (
    <nav className='border-border bg-background fixed z-50 flex w-full items-center justify-center border px-6 py-4 text-white'>
      <section className='flex w-full max-w-5xl items-center justify-between xl:max-w-[1200px]'>
        <Link href='/'>
          <span className='text-primary font-manrope mr-4 text-2xl font-bold tracking-tight'>
            R<span className='text-lg'>EP</span>
            <SearchCode className='mx-[1px] ml-[2px] inline' size={20} />L
            <span className='text-lg'>ENS</span>
          </span>
        </Link>
        <section className='flex items-center gap-4'>
          <span
            className={
              isLocal
                ? 'ml-4 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800'
                : 'text-destructive ml-4 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold'
            }
          >
            {isLocal ? 'Connected to Local Agent' : 'Agent Not Connected'}
          </span>
          <ThemeToggle />
        </section>
      </section>
    </nav>
  );
}
