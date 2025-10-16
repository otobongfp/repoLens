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
        <div className='mt-4 mb-8'>
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
              RepoLens is an Opensource AI-powered requirements engineering and
              codebase analysis platform that analyzes repositories to provide
              clear, actionable insights for developers, product leaders and
              teams. By combining advanced code analysis, requirement mapping,
              and intelligent project management, RepoLens helps developers
              understand complex codebases, identify technical debt, and ensure
              code quality across projects.
            </p>
          </Reveal>

          <Reveal delay={0.3}>
            <p className='text-muted-foreground mt-4 text-left text-base sm:text-lg'>
              <strong>Here's how it works:</strong> Imagine you're joining a new
              project with thousands of files. Instead of spending weeks
              manually exploring the codebase, you simply upload your
              requirements document and connect your GitHub repository to
              RepoLens. Within minutes, you get a comprehensive analysis showing
              how each requirement maps to specific code modules, identify
              potential gaps between what's specified and what's implemented,
              and receive AI-powered insights about code quality, dependencies,
              and areas that need attention. You can further estimate timelines,
              security risks, etc
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
                To bridge the gap between requirements and implementation,
                making every codebase instantly understandable and maintainable.
                RepoLens empowers developers, product leaders, and teams to make
                informed decisions through AI-powered analysis, ensuring that
                what's built aligns with what's needed.
              </p>
            </div>
          </Reveal>
        </div>

        {/* Features Grid */}
        <div className='mb-16'>
          <Reveal>
            <h2 className='text-foreground mb-12 text-center text-2xl font-bold sm:text-3xl'>
              Why Use RepoLens?
            </h2>
          </Reveal>

          <div className='grid items-stretch gap-6 md:grid-cols-2 lg:grid-cols-3'>
            <Reveal delay={0.1}>
              <div className='border-border bg-card flex h-[350px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Code className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Advanced Code Analysis
                </h3>
                <p className='text-muted-foreground flex-1'>
                  RepoLens provides comprehensive codebase analysis using Neo4j
                  graph database to map code relationships, dependencies, and
                  structure. Our AI-powered analysis engine identifies patterns,
                  technical debt, and provides actionable insights for code
                  improvement.
                </p>
              </div>
            </Reveal>

            <Reveal delay={0.2}>
              <div className='border-border bg-card flex h-[350px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Target className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Requirements Mapping
                </h3>
                <p className='text-muted-foreground flex-1'>
                  Connect business requirements to code implementation with our
                  intelligent mapping system. RepoLens analyzes requirements
                  documents and maps them to actual code, ensuring alignment
                  between what's specified and what's implemented.
                </p>
              </div>
            </Reveal>

            <Reveal delay={0.3}>
              <div className='border-border bg-card flex h-[350px] flex-col rounded-xl border p-6 shadow-sm transition hover:shadow-md'>
                <div className='bg-primary/10 mb-4 w-fit rounded-lg p-3'>
                  <Zap className='text-primary h-6 w-6' />
                </div>
                <h3 className='text-card-foreground mb-3 text-lg font-semibold sm:text-xl'>
                  Multi-Tenant Project Management
                </h3>
                <p className='text-muted-foreground flex-1'>
                  Manage multiple projects with our robust multi-tenant
                  architecture. Create, analyze, and track projects from GitHub
                  repositories or local sources with comprehensive project
                  lifecycle management and team collaboration features.
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
                    AI-powered codebase analysis can revolutionize how
                    developers understand and maintain complex codebases. The
                    presentation highlighted our mission to make code analysis
                    more accessible and provide actionable insights for
                    developers and teams worldwide.
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
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>

        {/* CTA Section */}
        <div className='flex flex-col items-center justify-center text-center'>
          <Reveal>
            <h2 className='text-foreground mb-4 text-2xl font-bold sm:text-3xl'>
              Ready to Explore?
            </h2>
            <p className='text-muted-foreground mb-6 text-base sm:text-lg'>
              Start analyzing your first repository and experience the power of
              AI-driven codebase analysis with RepoLens.
            </p>
            <div className='flex flex-col items-center gap-4'>
              <Link
                href='/select'
                className='bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center gap-2 rounded-lg px-6 py-3 text-lg font-semibold transition'
              >
                Get Started
                <ArrowLeft className='h-5 w-5 rotate-180' />
              </Link>

              <Link
                href='https://github.com/otobongfp/repolens'
                target='_blank'
                rel='noopener noreferrer'
                className='border-border bg-card text-card-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition'
              >
                <Github className='h-4 w-4' />
                View Source Code on GitHub
              </Link>
            </div>
          </Reveal>
        </div>
      </main>
    </div>
  );
}
