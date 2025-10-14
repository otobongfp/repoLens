'use client';
import { SearchCode } from 'lucide-react';
import { useApi } from '../context/ApiProvider';
import Link from 'next/link';
import { ThemeToggle } from '@/components/theme/ThemeToggle';

export default function Navbar() {
  const { useLocalBackend } = useApi();

  return (
    <nav className='border-border bg-background fixed z-50 flex h-16 w-full items-center justify-center border px-4 text-white sm:px-6'>
      <section className='flex w-full max-w-5xl items-center justify-between xl:max-w-[1200px]'>
        <Link href='/'>
          <span className='text-primary font-manrope mr-2 text-xl font-bold tracking-tight sm:mr-4 sm:text-2xl'>
            R<span className='text-sm sm:text-lg'>EP</span>
            <SearchCode className='mx-[1px] ml-[2px] inline' size={16} />L
            <span className='text-sm sm:text-lg'>ENS</span>
          </span>
          <span className='sr-only'>Go to repolens homepage</span>
        </Link>
        <section className='flex items-center gap-2 sm:gap-4'>
          <span
            className={
              useLocalBackend
                ? 'ml-2 hidden rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800 sm:ml-4 sm:block sm:px-3'
                : 'text-destructive ml-2 hidden rounded-full bg-red-100 px-2 py-1 text-xs font-semibold sm:ml-4 sm:block sm:px-3'
            }
          >
            {useLocalBackend ? 'Local Backend' : 'Cloud API'}
          </span>
          <span
            className={
              useLocalBackend
                ? 'ml-2 rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800 sm:ml-4 sm:hidden'
                : 'text-destructive ml-2 rounded-full bg-red-100 px-2 py-1 text-xs font-semibold sm:ml-4 sm:hidden'
            }
          >
            {useLocalBackend ? 'Local' : 'Cloud'}
          </span>
          <ThemeToggle />
        </section>
      </section>
    </nav>
  );
}
