"use client";

import Navbar from "../components/Navbar";
import RepoInput from "../components/RepoInput";
import MainTabs from "../components/MainTabs";
import Sidebar from "../components/Sidebar";
import LoadingSpinner from "../components/LoadingSpinner";
import { useState } from "react";

export default function AppPage() {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar>
        <button
          className="md:hidden p-2 text-primary focus:outline-none"
          onClick={() => setSidebarOpen((v) => !v)}
          aria-label="Toggle sidebar"
        >
          <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
            <rect y="4" width="24" height="2" rx="1" fill="currentColor" />
            <rect y="11" width="24" height="2" rx="1" fill="currentColor" />
            <rect y="18" width="24" height="2" rx="1" fill="currentColor" />
          </svg>
        </button>
      </Navbar>
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar: hidden on mobile if toggled off */}
        <div
          className={`transition-all duration-300 ${
            sidebarOpen ? "block" : "hidden"
          } md:block`}
        >
          <Sidebar graph={graph} />
        </div>
        <main className="flex-1 flex flex-col items-center p-6 overflow-auto">
          <RepoInput
            setGraph={setGraph}
            setLoading={setLoading}
            setError={setError}
          />
          {loading && <LoadingSpinner />}
          {error && <div className="text-red-500 mt-4">{error}</div>}
          {graph &&
            !loading &&
            (fullscreen ? (
              <div className="fixed inset-0 z-50 bg-background/95 flex items-center justify-center">
                <div className="w-full max-w-4xl rounded-2xl bg-white/5 backdrop-blur-md shadow-xl p-4 border border-white/10 h-full flex flex-col items-center justify-center">
                  <MainTabs graph={graph} />
                </div>
              </div>
            ) : (
              <div className="w-full max-w-4xl flex justify-center items-center mt-6">
                <div className="w-full rounded-2xl bg-white/5 backdrop-blur-md shadow-xl p-4 border border-white/10">
                  <MainTabs graph={graph} />
                </div>
              </div>
            ))}
        </main>
      </div>
    </div>
  );
}
