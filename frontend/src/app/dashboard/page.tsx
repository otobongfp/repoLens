'use client';

import Navbar from '../components/Navbar';
import RepoInput from '../components/RepoInput';
import MainTabs from '../components/MainTabs';
import Sidebar from '../components/Sidebar';
import LoadingSpinner from '../components/LoadingSpinner';
import CacheManager from '../components/CacheManager';
import { GraphDataProvider, useGraphData } from '../context/GraphDataProvider';
import { useState, useEffect } from 'react';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // Default to closed on mobile
  const [fullscreen, setFullscreen] = useState(false);
  const { graph, isLoading, error } = useGraphData();

  // Handle sidebar close event from mobile
  useEffect(() => {
    const handleCloseSidebar = () => setSidebarOpen(false);
    window.addEventListener('closeSidebar', handleCloseSidebar);
    return () => window.removeEventListener('closeSidebar', handleCloseSidebar);
  }, []);

  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      {/* Mobile sidebar toggle button */}
      <button
        className='bg-primary/90 fixed top-20 left-4 z-40 rounded-lg p-2 text-white shadow-lg md:hidden'
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <svg
          className='h-5 w-5'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M4 6h16M4 12h16M4 18h16'
          />
        </svg>
      </button>

      <div className='bg-sidebar flex flex-1 overflow-hidden'>
        {/* Sidebar: hidden on mobile if toggled off */}
        <div
          className={`transition-all duration-300 ${
            sidebarOpen ? 'block' : 'hidden'
          } md:block ${sidebarOpen ? 'fixed inset-0 z-30 md:relative md:z-auto' : ''}`}
        >
          <div
            className={`${sidebarOpen ? 'bg-black/50 md:bg-transparent' : ''} ${sidebarOpen ? 'fixed inset-0 md:static' : ''}`}
          >
            <div
              className={`${sidebarOpen ? 'absolute top-0 right-0 h-full w-80 md:relative md:w-auto' : ''}`}
            >
              <Sidebar />
            </div>
          </div>
        </div>
        <main className='flex flex-1 flex-col items-center overflow-auto p-4 sm:p-6'>
          <RepoInput />
          {isLoading && <LoadingSpinner />}
          {error && <div className='mt-4 text-red-500'>{error}</div>}
          {graph &&
            !isLoading &&
            (fullscreen ? (
              <div className='bg-background/95 fixed inset-0 z-50 flex items-center justify-center p-4'>
                <div className='flex h-full w-full max-w-4xl flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 p-4 shadow-xl backdrop-blur-md'>
                  <MainTabs />
                </div>
              </div>
            ) : (
              <div className='mt-6 flex w-full max-w-4xl items-center justify-center'>
                <div className='w-full rounded-2xl border border-white/10 bg-white/5 p-2 shadow-xl backdrop-blur-md sm:p-4'>
                  <MainTabs />
                </div>
              </div>
            ))}
        </main>
      </div>
      <CacheManager />
    </div>
  );
}

export default function AppPage() {
  return (
    <GraphDataProvider>
      <AppContent />
    </GraphDataProvider>
  );
}
