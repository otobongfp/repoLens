"use client";

import Link from "next/link";
import Navbar from "../../components/Navbar";

export default function LearningDashboard() {
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
        <div className="text-center max-w-2xl">
          <div className="text-6xl mb-6">🎓</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Micro-Learning
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Pick a path, assess your knowledge, and follow a curated journey
            through code.
          </p>

          <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-orange-400 mb-2">
              Coming Soon
            </h2>
            <p className="text-gray-300">
              We're building an intelligent learning system that will help you
              master code through personalized paths and assessments.
            </p>
          </div>

          {/* Feature Preview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Knowledge Assessment
              </h3>
              <p className="text-sm text-gray-300">
                Take quizzes to assess your current knowledge and identify
                learning gaps
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="text-3xl mb-3">🛤️</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Learning Paths
              </h3>
              <p className="text-sm text-gray-300">
                Follow curated learning paths based on your goals and current
                skill level
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Progress Tracking
              </h3>
              <p className="text-sm text-gray-300">
                Track your learning progress and celebrate milestones
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="text-3xl mb-3">🤝</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Community Learning
              </h3>
              <p className="text-sm text-gray-300">
                Learn with others and share knowledge in a collaborative
                environment
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
