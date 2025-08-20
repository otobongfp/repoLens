"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "../../components/Navbar";
import {
  CodeIcon,
  PuzzleIcon,
  BrainIcon,
  BotIcon,
} from "../../components/LucideIcons";

interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  route: string;
  disabled?: boolean;
  comingSoon?: boolean;
}

const features: FeatureCard[] = [
  {
    id: "analyze",
    title: "Analyze Any Open-Source Repo",
    description:
      "Upload or link a GitHub repo to get instant structure and insights.",
    icon: <CodeIcon className="text-primary" size={48} />,
    route: "/dashboard/analyze",
  },
  {
    id: "components",
    title: "Dismember Repo into Components",
    description:
      "Break down repos into technologies, algorithms, and a linked learning graph.",
    icon: <PuzzleIcon className="text-primary" size={48} />,
    route: "/dashboard/components",
  },
  {
    id: "learning",
    title: "Micro-Learning",
    description:
      "Pick a path, assess your knowledge, and follow a curated journey.",
    icon: <BrainIcon className="text-primary" size={48} />,
    route: "/dashboard/learning",
    disabled: true,
    comingSoon: true,
  },
  {
    id: "ai-assistant",
    title: "Ask the RepoLens AI",
    description: "Chat with RepoLens AI about the repo and its inner workings.",
    icon: <BotIcon className="text-primary" size={48} />,
    route: "/dashboard/ai-assistant",
  },
];

function FeatureCard({ feature }: { feature: FeatureCard }) {
  const router = useRouter();

  const handleClick = () => {
    if (!feature.disabled) {
      router.push(feature.route);
    }
  };

  return (
    <div
      className={`relative w-80 h-64 p-6 rounded-2xl shadow-xl border border-white/10 bg-white/5 backdrop-blur-sm cursor-pointer transition-all duration-300 ${
        feature.disabled
          ? "opacity-50 cursor-not-allowed"
          : "hover:scale-105 hover:shadow-2xl hover:bg-white/10 hover:border-primary/30"
      }`}
      onClick={handleClick}
    >
      {/* Coming Soon Badge */}
      {feature.comingSoon && (
        <div className="absolute -top-2 -right-2 bg-orange-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
          Coming Soon
        </div>
      )}

      {/* Icon */}
      <div className="mb-4">{feature.icon}</div>

      {/* Title */}
      <h3 className="text-xl font-bold mb-3 text-white">{feature.title}</h3>

      {/* Description */}
      <p className="text-sm text-gray-300 leading-relaxed">
        {feature.description}
      </p>

      {/* Hover Effect Overlay */}
      {!feature.disabled && (
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/10 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      )}
    </div>
  );
}

export default function FeatureSelectPage() {
  return (
    <div className="min-h-screen bg-[#1a1f2b] flex flex-col">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[400px] h-[400px] bg-[#1db470] opacity-20 rounded-full filter blur-3xl" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-400 opacity-15 rounded-full filter blur-2xl" />
        <div className="absolute top-[30%] left-[60%] w-[300px] h-[300px] bg-pink-300 opacity-15 rounded-full filter blur-2xl" />
      </div>

      {/* Navbar */}
      <Navbar>
        <Link
          href="/"
          className="text-primary hover:text-primary/80 transition-colors text-sm font-medium"
        >
          ← Back to Landing
        </Link>
      </Navbar>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Choose Your Path
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl">
            Select how you'd like to explore and understand code with RepoLens
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
          {features.map((feature) => (
            <div key={feature.id} className="flex justify-center">
              <FeatureCard feature={feature} />
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-16 text-center">
          <p className="text-gray-400 text-sm">
            Each tool is designed to help you understand code in different ways
          </p>
        </div>
      </main>
    </div>
  );
}
