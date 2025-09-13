import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { CTAButton } from '@/components/CTAButton';
import { Reveal } from '@/components/Reveal';

export default function Hero() {
  return (
    <section className='mt-16 flex w-full flex-col items-center justify-center gap-8'>
      <div className='hidden'>
        <Link
          href='#link'
          className='hover:bg-background dark:hover:border-t-border bg-muted group mx-auto mt-8 flex w-fit items-center gap-4 rounded-full border p-1 pl-4 shadow-md shadow-zinc-950/5 transition-colors duration-300 dark:border-t-white/5 dark:shadow-zinc-950'
        >
          <span className='text-foreground text-sm'>
            Introducing Support for AI Models
          </span>
          <span className='dark:border-background block h-4 w-0.5 border-l bg-white dark:bg-zinc-700'></span>
          <div className='bg-background group-hover:bg-muted size-6 overflow-hidden rounded-full duration-500'>
            <div className='flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0'>
              <span className='flex size-6'>
                <ArrowRight className='m-auto size-3' />
              </span>
              <span className='flex size-6'>
                <ArrowRight className='m-auto size-3' />
              </span>
            </div>
          </div>
        </Link>
      </div>

      <section className='relative flex h-96 w-full flex-col justify-end'>
        <Reveal width='100%' slideDirection='bottom'>
          <div className='relative w-full p-6'>
            <div className='absolute left-0 top-4 h-0.5 w-full bg-[linear-gradient(to_right,_transparent_0%,_var(--border)_9.27%,_var(--border)_90.7%,_transparent_100%)]'></div>
            <div className='absolute left-4 top-0 h-full w-0.5 bg-[linear-gradient(to_bottom,_transparent_0%,_var(--border)_9.27%,_var(--border)_90.7%,_transparent_100%)]'></div>
            <section className='relative flex h-36 flex-col items-center justify-center gap-2 bg-transparent py-24 text-center backdrop-blur-sm'>
              <h1 className='text-foreground font-serif text-4xl font-extrabold md:text-5xl'>
                Understand Any Codebase in Seconds
              </h1>

              <p className='text-muted-foreground text-md max-w-xl text-center'>
                Paste a GitHub repo URL, visualize its structure, and ask AI
                anything about the code. RepoLens makes onboarding and code
                exploration effortless.
              </p>
              <div
                className='mask-b-from-20% absolute -z-10 h-full w-full'
                style={{
                  backgroundColor: 'var(--background)',
                  background: `
                radial-gradient(circle, transparent 20%, var(--background) 20%, var(--background) 80%, transparent 80%, transparent),
                radial-gradient(circle, transparent 20%, var(--background) 20%, var(--background) 80%, transparent 80%, transparent),
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, var(--background) 1px)
                `,
                  backgroundPosition: `0 0, 0 0, 0 -1px, -1px 0`,
                  backgroundSize: '20px 20px',
                }}
              />
            </section>
            <div className='absolute right-4 top-0 h-full w-0.5 bg-[linear-gradient(to_bottom,_transparent_0%,_var(--border)_9.27%,_var(--border)_90.7%,_transparent_100%)]'></div>
            <div className='absolute bottom-4 left-0 h-px w-full bg-[linear-gradient(to_right,_transparent_0%,_var(--border)_9.27%,_var(--border)_90.7%,_transparent_100%)]'></div>
          </div>
        </Reveal>
      </section>

      <div className='flex items-center justify-center gap-4'>
        <Reveal delay={0.5}>
          <Link href='/dashboard/select' className='group'>
            <CTAButton className='text-md font-medium capitalize'>
              Get Started
            </CTAButton>
          </Link>
        </Reveal>
      </div>

      <section className='isolate'>
        <div className='relative overflow-hidden px-2'>
          <div
            aria-hidden
            className='bg-linear-to-b to-background absolute inset-0 z-10 from-transparent from-35%'
          />
          <Reveal delay={0.75}>
            <div className='inset-shadow-2xs ring-background dark:inset-shadow-white/20 bg-background relative mx-auto max-w-6xl overflow-hidden rounded-2xl border p-1 shadow-lg shadow-zinc-950/15 ring-1'>
              <img
                className='bg-background relative hidden rounded-[12px] dark:block'
                src='/RepoLensDark.webp'
                alt='app screen'
                width='2700'
                height='1440'
              />
              <img
                className='z-2 border-border/25 relative rounded-[12px] border dark:hidden'
                src='/RepoLensLight.webp'
                alt='app screen'
                width='2700'
                height='1440'
              />
            </div>
          </Reveal>
        </div>
      </section>
    </section>
  );
}
