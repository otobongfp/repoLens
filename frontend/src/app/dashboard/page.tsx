'use client';

export const runtime = 'edge';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to analyze page by default
    router.replace('/dashboard/analyze');
  }, [router]);

  return (
    <div className='bg-sidebar flex min-h-screen items-center justify-center'>
      <div className='text-center'>
        <div className='border-primary mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2'></div>
        <p className='text-white'>Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
