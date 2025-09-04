import { subset } from 'd3';
import '../../styles/globals.css';
import Navbar from './components/Navbar';
import { ApiProvider } from './context/ApiProvider';
import { Geist, Geist_Mono, Manrope, Merriweather } from 'next/font/google';
import DotBackground from '@/components/DotBackground';

export const metadata = {
  title: 'Repolens',
  description: 'Improving opensource education with AI',
};

const geist = Geist({
  variable: '--font-geist',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

const manrope = Manrope({
  variable: '--font-manrope',
  subsets: ['latin'],
});

const merrriweather = Merriweather({
  subsets: ['latin'],
  weight: '400',
  preload: false,
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en'>
      <body
        suppressHydrationWarning={true}
        className={`${geist.variable} ${geistMono.variable} ${manrope.variable} font-sans antialiased`}
      >
        <ApiProvider>
          <Navbar />

          <div className='relative grid h-full grid-cols-[2.5rem_auto_2.5rem] xl:grid-cols-[auto_2rem_1200px_2rem_auto]'>
            <div className='relative col-start-2 h-full w-full overflow-y-auto xl:col-start-3'>
              <div
                aria-hidden='true'
                className='absolute inset-0 isolate hidden opacity-65 contain-strict lg:block'
              >
                <div className='w-140 h-320 -translate-y-87.5 absolute left-0 top-0 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsla(0,0%,85%,.08)_0,hsla(0,0%,55%,.02)_50%,hsla(0,0%,45%,0)_80%)]'></div>
                <div className='h-320 absolute left-0 top-0 w-60 -rotate-45 rounded-full bg-[radial-gradient(50%_50%_at_50%_50%,hsla(0,0%,85%,.06)_0,hsla(0,0%,45%,.02)_80%,transparent_100%)] [translate:5%_-50%]'></div>
                <div className='h-320 -translate-y-87.5 absolute left-0 top-0 w-60 -rotate-45 bg-[radial-gradient(50%_50%_at_50%_50%,hsla(0,0%,85%,.04)_0,hsla(0,0%,45%,.02)_80%,transparent_100%)]'></div>
              </div>
              {children}
            </div>

            {/* <div className='border-border relative -right-px col-start-1 row-span-full row-start-1 border-x bg-[image:repeating-linear-gradient(135deg,var(--border)_0,var(--border)_1px,transparent_0,transparent_50%)] bg-[size:10px_10px] xl:col-start-2'></div> */}

            {/* <div className='border-border relative -left-px col-start-3 row-span-full row-start-1 border-x bg-[image:repeating-linear-gradient(315deg,var(--border)_0,var(--border)_1px,transparent_0,transparent_50%)] bg-[size:10px_10px] xl:col-start-4'></div> */}
          </div>
        </ApiProvider>
      </body>
    </html>
  );
}
