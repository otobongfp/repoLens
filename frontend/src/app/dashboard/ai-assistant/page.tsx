"use client";

import Link from "next/link";
import Navbar from "../../components/Navbar";
import { BotIcon } from "../../components/LucideIcons";

export default function AIAssistantDashboard() {
  return (
    <div className="min-h-screen bg-sidebar flex flex-col">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[400px] h-[400px] bg-primary opacity-20 rounded-full filter blur-3xl" />
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
            <BotIcon className="text-primary mx-auto" size={64} />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ask the RepoLens AI
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Chat with RepoLens AI about repositories and get intelligent
            insights
          </p>

          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-blue-400 mb-2">
              AI-Powered Code Analysis
            </h2>
            <p className="text-gray-300 mb-4">
              This feature will allow you to have natural conversations with
              RepoLens AI about any codebase. Ask questions, get explanations,
              and receive intelligent insights about code structure, patterns,
              and best practices.
            </p>
            <div className="text-left space-y-2 text-sm text-gray-300">
              <p>
                • <strong>Natural Language Q&A:</strong> Ask questions about
                code in plain English
              </p>
              <p>
                • <strong>Code Explanation:</strong> Get detailed explanations
                of functions, classes, and algorithms
              </p>
              <p>
                • <strong>Best Practices:</strong> Receive suggestions for
                improving code quality
              </p>
              <p>
                • <strong>Security Analysis:</strong> Identify potential
                security issues and vulnerabilities
              </p>
              <p>
                • <strong>Refactoring Suggestions:</strong> Get AI-powered
                recommendations for code improvements
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
