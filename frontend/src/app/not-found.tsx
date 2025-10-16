'use client';

export const runtime = 'edge';

import Link from 'next/link';
import { Search, Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className='bg-background flex min-h-screen items-center justify-center px-4'>
      <div className='w-full max-w-2xl text-center'>
        {/* 404 Icon */}
        <div className='mb-8'>
          <div className='bg-muted mx-auto flex h-20 w-20 items-center justify-center rounded-full'>
            <Search className='text-muted-foreground h-10 w-10' />
          </div>
        </div>

        {/* 404 Title */}
        <h1 className='text-foreground mb-4 text-6xl font-bold'>404</h1>
        <h2 className='text-foreground mb-4 text-2xl font-semibold'>
          Page Not Found
        </h2>

        {/* Description */}
        <p className='text-muted-foreground mb-8 text-lg'>
          Sorry, we couldn't find the page you're looking for. It might have
          been moved, deleted, or you entered the wrong URL.
        </p>

        {/* Action Buttons */}
        <div className='flex flex-col justify-center gap-4 sm:flex-row'>
          <Link
            href='/'
            className='bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center gap-2 rounded-lg px-6 py-3 text-base font-semibold transition'
          >
            <Home className='h-4 w-4' />
            Go Home
          </Link>

          <button
            onClick={() => window.history.back()}
            className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-6 py-3 text-base font-semibold transition'
          >
            <ArrowLeft className='h-4 w-4' />
            Go Back
          </button>
        </div>

        {/* Help Text */}
        <p className='text-muted-foreground mt-8 text-sm'>
          Looking for something specific? Try our{' '}
          <Link
            href='/dashboard/select'
            className='text-primary hover:underline'
          >
            project dashboard
          </Link>{' '}
          or{' '}
          <Link href='/about' className='text-primary hover:underline'>
            learn more about RepoLens
          </Link>
        </p>
      </div>
    </div>
  );
}
