import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Link from 'next/link';

export default function Home() {
  return (
    <div className='bg-background relative flex min-h-screen flex-col overflow-hidden'>
      {/* Blurry shapes background */}
      <div className='pointer-events-none absolute inset-0 -z-10'>
        <div className='bg-primary absolute left-[-10%] top-[-10%] h-[400px] w-[400px] rounded-full opacity-30 blur-3xl filter' />
        <div className='absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-blue-400 opacity-20 blur-2xl filter' />
        <div className='absolute left-[60%] top-[30%] h-[300px] w-[300px] rounded-full bg-pink-300 opacity-20 blur-2xl filter' />
      </div>
      <Navbar />
      <main className='flex flex-1 flex-col items-center justify-center px-4'>
        <Hero />
        <div className='mt-8 flex justify-center'>
          <Link href='/dashboard/select'>
            <button className='bg-primary hover:bg-primary/80 rounded-lg px-8 py-3 text-lg font-semibold text-white shadow-lg transition'>
              Get Started
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}
