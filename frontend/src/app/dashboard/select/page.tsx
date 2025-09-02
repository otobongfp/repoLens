'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../../components/Navbar';
import {
  CodeIcon,
  PuzzleIcon,
  BrainIcon,
  BotIcon,
} from '../../components/LucideIcons';

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
    id: 'analyze',
    title: 'Analyze Any Open-Source Repo',
    description:
      'Upload or link a GitHub repo to get instant structure and insights.',
    icon: <CodeIcon className='text-primary' size={48} />,
    route: '/dashboard/analyze',
  },
  {
    id: 'components',
    title: 'Dismember Repo into Components',
    description:
      'Break down repos into technologies, algorithms, and a linked learning graph.',
    icon: <PuzzleIcon className='text-primary' size={48} />,
    route: '/dashboard/components',
  },
  {
    id: 'learning',
    title: 'Micro-Learning',
    description:
      'Pick a path, assess your knowledge, and follow a curated journey.',
    icon: <BrainIcon className='text-primary' size={48} />,
    route: '/dashboard/learning',
    disabled: true,
    comingSoon: true,
  },
  {
    id: 'ai-assistant',
    title: 'Ask the RepoLens AI',
    description: 'Chat with RepoLens AI about the repo and its inner workings.',
    icon: <BotIcon className='text-primary' size={48} />,
    route: '/dashboard/ai-assistant',
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
      className={`backdrop-blur-xs relative h-64 w-80 cursor-pointer rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl transition-all duration-300 ${
        feature.disabled
          ? 'cursor-not-allowed opacity-50'
          : 'hover:border-primary/30 hover:scale-105 hover:bg-white/10 hover:shadow-2xl'
      }`}
      onClick={handleClick}
    >
      {/* Coming Soon Badge */}
      {feature.comingSoon && (
        <div className='absolute -right-2 -top-2 rounded-full bg-orange-500 px-3 py-1 text-xs font-semibold text-white'>
          Coming Soon
        </div>
      )}

      {/* Icon */}
      <div className='mb-4'>{feature.icon}</div>

      {/* Title */}
      <h3 className='mb-3 text-xl font-bold text-white'>{feature.title}</h3>

      {/* Description */}
      <p className='text-sm leading-relaxed text-gray-300'>
        {feature.description}
      </p>

      {/* Hover Effect Overlay */}
      {!feature.disabled && (
        <div className='bg-linear-to-br from-primary/10 pointer-events-none absolute inset-0 rounded-2xl to-transparent opacity-0 transition-opacity duration-300 hover:opacity-100' />
      )}
    </div>
  );
}

export default function FeatureSelectPage() {
  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      {/* Background Effects */}
      <div className='pointer-events-none absolute inset-0 -z-10'>
        <div className='bg-primary absolute left-[-10%] top-[-10%] h-[400px] w-[400px] rounded-full opacity-20 blur-3xl filter' />
        <div className='absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-blue-400 opacity-15 blur-2xl filter' />
        <div className='absolute left-[60%] top-[30%] h-[300px] w-[300px] rounded-full bg-pink-300 opacity-15 blur-2xl filter' />
      </div>

      {/* Navbar */}
      <Navbar>
        <Link
          href='/'
          className='text-primary hover:text-primary/80 text-sm font-medium transition-colors'
        >
          ← Back to Landing
        </Link>
      </Navbar>

      {/* Main Content */}
      <main className='flex flex-1 flex-col items-center justify-center px-4 py-8'>
        {/* Header */}
        <div className='mb-12 text-center'>
          <h1 className='mb-4 text-4xl font-bold text-white md:text-5xl'>
            Choose Your Path
          </h1>
          <p className='max-w-2xl text-xl text-gray-300'>
            Select how you'd like to explore and understand code with RepoLens
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className='grid w-full max-w-4xl grid-cols-1 gap-8 md:grid-cols-2'>
          {features.map((feature) => (
            <div key={feature.id} className='flex justify-center'>
              <FeatureCard feature={feature} />
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className='mt-16 text-center'>
          <p className='text-sm text-gray-400'>
            Each tool is designed to help you understand code in different ways
          </p>
        </div>
      </main>
    </div>
  );
}
