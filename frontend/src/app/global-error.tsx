'use client';

import Link from 'next/link';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  return (
    <html>
      <body>
        <div className='bg-background flex min-h-screen items-center justify-center px-4'>
          <div className='w-full max-w-2xl text-center'>
            {/* Error Icon */}
            <div className='mb-8'>
              <div className='bg-destructive/10 mx-auto flex h-20 w-20 items-center justify-center rounded-full'>
                <AlertTriangle className='text-destructive h-10 w-10' />
              </div>
            </div>

            {/* Error Title */}
            <h1 className='text-foreground mb-4 text-3xl font-bold'>
              Application Error
            </h1>

            {/* Error Description */}
            <p className='text-muted-foreground mb-8 text-lg'>
              A critical error occurred in the application. Please try
              refreshing the page or contact support if the problem persists.
            </p>

            {/* Action Buttons */}
            <div className='flex flex-col justify-center gap-4 sm:flex-row'>
              <button
                onClick={reset}
                className='bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center gap-2 rounded-lg px-6 py-3 text-base font-semibold transition'
              >
                <RefreshCw className='h-4 w-4' />
                Try Again
              </button>

              <Link
                href='/'
                className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-6 py-3 text-base font-semibold transition'
              >
                <Home className='h-4 w-4' />
                Go Home
              </Link>
            </div>

            {/* Help Text */}
            <p className='text-muted-foreground mt-8 text-sm'>
              If this problem persists, please{' '}
              <Link
                href='https://github.com/otobongfp/repolens/issues'
                target='_blank'
                rel='noopener noreferrer'
                className='text-primary hover:underline'
              >
                report it on GitHub
              </Link>
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
