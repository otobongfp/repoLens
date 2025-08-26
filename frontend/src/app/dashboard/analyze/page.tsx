"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AnalyzeDashboard() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the main dashboard which contains the analysis functionality
    router.replace("/dashboard");
  }, [router]);

  return (
    <div className="min-h-screen bg-sidebar flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-white">Redirecting to analysis dashboard...</p>
      </div>
    </div>
  );
}
