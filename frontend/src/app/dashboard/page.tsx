'use client';

import Navbar from '../components/Navbar';
import RepoInput from '../components/RepoInput';
import MainTabs from '../components/MainTabs';
import Sidebar from '../components/Sidebar';
import LoadingSpinner from '../components/LoadingSpinner';
import CacheManager from '../components/CacheManager';
import { GraphDataProvider, useGraphData } from '../context/GraphDataProvider';
import { useState } from 'react';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const { graph, isLoading, error } = useGraphData();

  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      <div className='bg-sidebar flex flex-1 overflow-hidden'>
        {/* Sidebar: hidden on mobile if toggled off */}
        <div
          className={`transition-all duration-300 ${
            sidebarOpen ? 'block' : 'hidden'
          } md:block`}
        >
          <Sidebar />
        </div>
        <main className='flex flex-1 flex-col items-center overflow-auto p-6'>
          <RepoInput />
          {isLoading && <LoadingSpinner />}
          {error && <div className='mt-4 text-red-500'>{error}</div>}
          {graph &&
            !isLoading &&
            (fullscreen ? (
              <div className='bg-background/95 fixed inset-0 z-50 flex items-center justify-center'>
                <div className='flex h-full w-full max-w-4xl flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 p-4 shadow-xl backdrop-blur-md'>
                  <MainTabs />
                </div>
              </div>
            ) : (
              <div className='mt-6 flex w-full max-w-4xl items-center justify-center'>
                <div className='w-full rounded-2xl border border-white/10 bg-white/5 p-4 shadow-xl backdrop-blur-md'>
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
