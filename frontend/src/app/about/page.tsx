'use client';

export const runtime = 'edge';

import Link from 'next/link';
import {
  ArrowLeft,
  Github,
  BookOpen,
  Users,
  Target,
  Lightbulb,
  Code,
  Zap,
} from 'lucide-react';
import { Reveal } from '@/components/Reveal';

export default function AboutPage() {
  return (
    <div className='bg-background min-h-screen select-text'>
      <main className='relative mx-auto mt-4 max-w-6xl px-4 py-16 sm:px-6 lg:px-8'>
        {/* Back Button */}
        <div className='mb-8'>
          <Reveal>
            <Link
              href='/'
              className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition'
            >
              <ArrowLeft className='h-4 w-4' />
              Back to Home
            </Link>
          </Reveal>
        </div>

        {/* Hero Section */}
        <div className='mb-16'>
          <div className='text-center'>
            <Reveal>
              <h1 className='text-foreground mb-6 text-3xl font-bold sm:text-4xl lg:text-5xl'>
                About <span className='text-primary'>RepoLens</span>
              </h1>
            </Reveal>
          </div>

          <Reveal delay={0.2}>
            <p className='text-muted-foreground text-left text-base sm:text-lg'>
              RepoLens empowers developers and teams by providing AI-driven
              tools for intuitive code exploration, seamless requirements
              alignment, and accessible micro-learning. We simplify onboarding,
              enhance codebase understanding, and foster education, enabling
              confident contributions to open-source and private projects while
              extending learning opportunities to underserved communities
              worldwide.
            </p>
          </Reveal>
        </div>

        {/* Mission Section */}
        <div className='mb-16'>
          <Reveal>
            <div className='border-border bg-card rounded-2xl border p-8 shadow-lg'>
              <div className='mb-6 flex items-center gap-4'>
                <div className='bg-primary/10 rounded-lg p-3'>
                  <Target className='text-primary h-8 w-8' />
                </div>
                <h2 className='text-card-foreground text-2xl font-bold sm:text-3xl'>
                  Our Vision
                </h2>
              </div>
              <p className='text-muted-foreground text-lg leading-relaxed'>
                To create a world where software is universally understandable,
                bridging the gap between code, collaboration, and education.
                RepoLens aspires to be the definitive platform for product teams
                to explore, validate, and learn from software systems, while
                empowering global communities with AI-driven education for a
                more inclusive future.
              </p>
            </div>
          </Reveal>
        </div>

        {/* Features Grid */}
        <div className='mb-16'>
          <Reveal>
            <h2 className='text-foreground mb-12 text-center text-2xl font-bold sm:text-3xl'>
              What Makes RepoLens Special
            </h2>
          </Reveal>

          <div className='grid items-stretch gap-6 md:grid-cols-2 lg:grid-cols-3'>
            <Reveal delay={0.1}>
              <div className='border-border bg-card flex min-h-[300px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Code className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Code Understanding Reimagined
                </h3>
                <p className='text-muted-foreground flex-1'>
                  RepoLens goes beyond syntax & static analysis; it builds a
                  graph of your repo, uncovering structure, dependencies, and
                  relationships that are often invisible. This makes exploring
                  any codebase feel intuitive, whether it's your first
                  contribution or your hundredth.
                </p>
              </div>
            </Reveal>

            <Reveal delay={0.2}>
              <div className='border-border bg-card flex min-h-[300px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Target className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Requirements Meet Reality
                </h3>
                <p className='text-muted-foreground flex-1'>
                  Most tools stop at code analysis. RepoLens is different: it
                  connects requirements to implementation, using AI to check
                  alignment, highlight gaps, and improve trust in software
                  systems. It's not just about code, it's about whether the code
                  does what it's meant to do.
                </p>
              </div>
            </Reveal>

            <Reveal delay={0.3}>
              <div className='border-border bg-card flex min-h-[300px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Lightbulb className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Learning Built In
                </h3>
                <p className='text-muted-foreground flex-1'>
                  RepoLens isn't only for maintainers, it's a platform for
                  continuous education. Through micro-learning and AI-powered
                  explanations, developers and even non-technical learners can
                  onboard faster, ask questions in natural language, and build
                  lasting understanding of complex systems.
                </p>
              </div>
            </Reveal>
          </div>
        </div>

        {/* Presentation Section */}
        <div className='mb-16'>
          <Reveal>
            <div className='border-border bg-card rounded-2xl border p-8 shadow-lg'>
              <div className='mb-6 flex items-center gap-4'>
                <div className='bg-primary/10 rounded-lg p-3'>
                  <Users className='text-primary h-8 w-8' />
                </div>
                <h2 className='text-card-foreground text-2xl font-bold sm:text-3xl'>
                  RepoLens at OSCAFEST 2025
                </h2>
              </div>

              <div className='grid gap-8 lg:grid-cols-2 lg:items-center'>
                <div>
                  <div className='mb-4 overflow-hidden rounded-xl shadow-lg'>
                    <img
                      src='/Presentation_OSCAFEST.jpg'
                      alt='Otobong Peter presenting RepoLens at OSCAFEST 2025'
                      className='h-auto w-full object-cover'
                    />
                  </div>
                </div>

                <div>
                  <h3 className='text-card-foreground mb-4 text-xl font-semibold sm:text-2xl'>
                    Otobong Peter
                  </h3>
                  <p className='text-muted-foreground mb-4 text-base leading-relaxed sm:text-lg'>
                    Presenting RepoLens at Open Source Conference Africa
                    Festival 2025
                  </p>
                  <p className='text-muted-foreground mb-6 leading-relaxed'>
                    RepoLens was showcased at OSCAFEST 2025, demonstrating how
                    AI-powered code analysis can revolutionize how developers
                    understand and explore complex codebases. The presentation
                    highlighted our mission to make software development more
                    accessible and educational for developers worldwide.
                  </p>
                  <div className='flex flex-wrap gap-4'>
                    <Link
                      href='https://github.com/otobongfp/repolens'
                      target='_blank'
                      rel='noopener noreferrer'
                      className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition'
                    >
                      <Github className='h-4 w-4' />
                      View on GitHub
                    </Link>
                    <Link
                      href='https://lilac-island-c10.notion.site/Repolens-Wiki-275f71e0e2f58094962bc668fb48fb96'
                      target='_blank'
                      rel='noopener noreferrer'
                      className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition'
                    >
                      <BookOpen className='h-4 w-4' />
                      Read our Wiki
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>

        {/* Vision Section */}
        {/* <div className='mb-16'>
          <Reveal>
            <div className='border-border bg-card rounded-2xl border p-8 shadow-lg'>
              <div className='mb-6 flex items-center gap-4'>
                <div className='bg-primary/10 rounded-lg p-3'>
                  <Lightbulb className='text-primary h-8 w-8' />
                </div>
                <h2 className='text-card-foreground text-2xl font-bold sm:text-3xl'>
                  Our Vision
                </h2>
              </div>
              <p className='text-muted-foreground text-lg leading-relaxed'>
                We envision a future where understanding any codebase is as
                simple as reading a book. RepoLens will continue to evolve,
                incorporating cutting-edge AI technologies and user feedback to
                create the most intuitive and powerful code exploration platform
                available. Our goal is to eliminate the barriers between
                developers and the code they need to understand, making software
                development more collaborative and efficient.
              </p>
            </div>
          </Reveal>
        </div> */}

        {/* CTA Section */}
        <div className='flex flex-col items-center justify-center text-center'>
          <Reveal>
            <h2 className='text-foreground mb-4 text-2xl font-bold sm:text-3xl'>
              Ready to Explore?
            </h2>
            <p className='text-muted-foreground mb-6 text-base sm:text-lg'>
              Start analyzing your first repository and experience the power of
              RepoLens.
            </p>
            <Link
              href='/dashboard/select'
              className='bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center gap-2 rounded-lg px-6 py-3 text-lg font-semibold transition'
            >
              Get Started
              <ArrowLeft className='h-5 w-5 rotate-180' />
            </Link>
          </Reveal>
        </div>
      </main>
    </div>
  );
}
