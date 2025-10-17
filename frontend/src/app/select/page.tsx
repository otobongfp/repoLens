'use client';

export const runtime = 'edge';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import {
  CodeIcon,
  PuzzleIcon,
  BrainIcon,
  BotIcon,
} from '../components/LucideIcons';
import {
  FeatureCard,
  FeatureCardContent,
  FeatureCardHeader,
  FeatureCardTitle,
  FeatureCardDescription,
  FeatureCardAction,
} from '@/components/ui/feature-card';
import DotBackground from '@/components/DotBackground';
import { Reveal } from '@/components/Reveal';
import { Fragment } from 'react';

interface FeatureCards {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  route: string;
  disabled?: boolean;
  comingSoon?: boolean;
  color?: string;
  slideDirection?: 'top' | 'bottom' | 'left' | 'right';
}

const features: FeatureCards[] = [
  {
    id: 'analyze',
    title: 'Analyze Any Open-Source Repo',
    description:
      'Upload or link a GitHub repo to get instant structure and insights.',
    icon: <CodeIcon className='text-primary' size={24} />,
    route: '/dashboard/analyze',
    color: 'chart-1',
    slideDirection: 'left',
  },
  {
    id: 'requirements',
    title: 'Match Requirements to Codebase',
    description:
      'Analyze how well code meets specific requirements and outline gaps, timelines,resource planning, etc.',
    icon: <PuzzleIcon className='text-primary' size={24} />,
    route: '/dashboard/requirements',
    color: 'chart-2',
    slideDirection: 'right',
  },
  {
    id: 'learning',
    title: 'Micro-Learning',
    description:
      'Pick a path, assess your knowledge, and follow a curated journey.',
    icon: <BrainIcon className='text-primary' size={24} />,
    route: '/dashboard/learning',
    disabled: true,
    comingSoon: true,
    color: 'chart-3',
    slideDirection: 'left',
  },
  {
    id: 'ai-assistant',
    title: 'Ask the RepoLens AI',
    description: 'Chat with RepoLens AI about the repo and its inner workings.',
    icon: <BotIcon className='text-primary' size={24} />,
    route: '/dashboard/ai-assistant',
    color: 'chart-4',
    slideDirection: 'right',
  },
];

function FeatureCards({ feature }: { feature: FeatureCards }) {
  const router = useRouter();

  const handleClick = () => {
    if (!feature.disabled) {
      router.push(feature.route);
    }
  };

  return (
    <div className='relative'>
      <Reveal width='100%' slideDirection={feature.slideDirection}>
        <FeatureCard
          className={`bg-card/50 hover:bg-card/80 h-64 w-72 cursor-pointer rounded-3xl border border-white/10 p-0 shadow-xl backdrop-blur-2xl transition-all duration-300 lg:h-64 lg:w-96 ${
            feature.disabled
              ? 'cursor-not-allowed opacity-50'
              : 'hover:border-primary/30 hover:shadow-2xl'
          }`}
          onClick={handleClick}
        >
          <FeatureCardContent className='relative flex h-full flex-col justify-between p-4'>
            {feature.comingSoon && (
              <div className='absolute top-4 right-4 z-10 rounded-full bg-orange-500 px-3 py-1 text-xs font-semibold text-white'>
                Coming Soon
              </div>
            )}

            <section className='bg-accent/40 w-min rounded-[8px] p-2'>
              {feature.icon}
            </section>

            <section>
              <FeatureCardTitle className='text-primary text-md mb-1 font-bold lg:text-xl'>
                {feature.title}
              </FeatureCardTitle>
              <FeatureCardDescription className='text-muted-foreground text-xs leading-relaxed'>
                {feature.description}
              </FeatureCardDescription>
            </section>

            {!feature.disabled && (
              <div className='from-primary/10 pointer-events-none absolute inset-0 rounded-2xl bg-linear-to-br to-transparent opacity-0 transition-opacity duration-300 hover:opacity-100' />
            )}
          </FeatureCardContent>
          <DotBackground className='mask-b-from-20%' />
        </FeatureCard>
      </Reveal>
    </div>
  );
}

export default function FeatureSelectPage() {
  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      <main className='mt-16 flex flex-1 flex-col items-center justify-center px-4 py-4'>
        <div className='mt-12 mb-12 text-center'>
          <Reveal width='100%' slideDirection='top'>
            <h1 className='text-foreground mb-2 font-serif text-3xl font-bold tracking-tighter md:text-5xl'>
              Choose Your Path
            </h1>
            <p className='text-muted-foreground max-w-xl text-xs md:text-base'>
              Select how you'd like to explore and understand code with RepoLens
            </p>
          </Reveal>
        </div>

        <div className='relative'>
          <div className='grid grid-cols-1 gap-16 md:grid-cols-2'>
            {features.map((feature) => (
              <Fragment key={feature.id}>
                <FeatureCards feature={feature} />
              </Fragment>
            ))}
          </div>
        </div>

        <div className='mt-8 text-center'>
          <p className='text-sm text-gray-400'>
            Each tool is designed to help you understand code in different ways
          </p>
        </div>
      </main>
    </div>
  );
}
