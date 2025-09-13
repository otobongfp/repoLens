'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AnalyzeDashboard() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the main dashboard which contains the analysis functionality
    router.replace('/dashboard');
  }, [router]);

  return (
    <div className='bg-sidebar flex min-h-screen items-center justify-center'>
      <div className='text-center'>
        <div className='border-primary mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2'></div>
        <p className='text-white'>Redirecting to analysis dashboard...</p>
      </div>
    </div>
  );
}
