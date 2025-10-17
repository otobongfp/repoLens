'use client';

export const runtime = 'edge';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../context/AuthProvider';
import LoadingSpinner from '../../../components/LoadingSpinner';
import toast from 'react-hot-toast';

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { handleOAuthCallback } = useAuth();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      try {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
          toast.error('Google authentication failed');
          router.push('/');
          return;
        }

        if (!code) {
          toast.error('No authorization code received');
          router.push('/');
          return;
        }

        await handleOAuthCallback('google', code);
        toast.success('Successfully signed in with Google!');
        router.push('/dashboard');
      } catch (error) {
        console.error('Google callback error:', error);
        toast.error('Authentication failed');
        router.push('/');
      } finally {
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [searchParams, handleOAuthCallback, router]);

  if (isProcessing) {
    return (
      <div className='bg-background flex min-h-screen items-center justify-center'>
        <div className='text-center'>
          <LoadingSpinner />
          <p className='mt-4 text-white'>Completing Google authentication...</p>
        </div>
      </div>
    );
  }

  return null;
}
