'use client';
import { useRepolensApi } from '../utils/api';
import Link from 'next/link';

export default function Navbar({ children }: { children?: React.ReactNode }) {
  const { isLocal } = useRepolensApi();

  return (
    <nav className='border-border bg-background fixed z-50 flex w-full items-center justify-center border px-6 py-4 text-white'>
      <section className='flex w-full max-w-5xl items-center justify-between xl:max-w-[1200px]'>
        <Link href='/'>
          <span className='text-primary mr-4 text-2xl font-bold tracking-tight'>
            RepoLens
          </span>
        </Link>
        <span
          className={
            isLocal
              ? 'ml-4 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800'
              : 'ml-4 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800'
          }
        >
          {isLocal ? 'Connected to Local Agent' : 'Agent Not Connected'}
        </span>
        {children}
      </section>
    </nav>
  );
}
