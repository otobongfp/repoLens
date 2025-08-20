"use client";

import Link from "next/link";
import Navbar from "../../components/Navbar";
import { PuzzleIcon } from "../../components/LucideIcons";

export default function ComponentsDashboard() {
  return (
    <div className="min-h-screen bg-[#1a1f2b] flex flex-col">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[400px] h-[400px] bg-[#1db470] opacity-20 rounded-full filter blur-3xl" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-400 opacity-15 rounded-full filter blur-2xl" />
        <div className="absolute top-[30%] left-[60%] w-[300px] h-[300px] bg-pink-300 opacity-15 rounded-full filter blur-2xl" />
      </div>

      <Navbar>
        <Link
          href="/dashboard/select"
          className="text-primary hover:text-primary/80 transition-colors text-sm font-medium"
        >
          ← Back to Features
        </Link>
      </Navbar>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8">
        {/* Coming Soon Content */}
        <div className="text-center max-w-3xl">
          <div className="mb-6">
            <PuzzleIcon className="text-primary mx-auto" size={64} />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Dismember Repo into Components
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Break down repositories into technologies, algorithms, and create a
            linked learning graph
          </p>

          <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-green-400 mb-2">
              Advanced Repository Analysis
            </h2>
            <p className="text-gray-300 mb-4">
              This feature will provide deep analysis of codebases, breaking
              them down into their fundamental components, identifying
              technologies, algorithms, and creating interconnected learning
              paths.
            </p>
            <div className="text-left space-y-2 text-sm text-gray-300">
              <p>
                • <strong>Technology Stack Detection:</strong> Automatically
                identify frameworks, libraries, and tools used
              </p>
              <p>
                • <strong>Algorithm Recognition:</strong> Detect and categorize
                algorithms and data structures
              </p>
              <p>
                • <strong>Component Mapping:</strong> Map relationships between
                different parts of the codebase
              </p>
              <p>
                • <strong>Learning Graph Generation:</strong> Create
                interconnected learning paths based on dependencies
              </p>
              <p>
                • <strong>Complexity Analysis:</strong> Identify complex areas
                and suggest learning priorities
              </p>
            </div>
          </div>

          {/* Back to Features */}
          <div className="mt-12">
            <Link
              href="/dashboard/select"
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/80 transition-colors font-semibold"
            >
              ← Back to Features
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
