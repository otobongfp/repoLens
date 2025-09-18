import { subset } from 'd3';
import '../../styles/globals.css';
import Navbar from './components/Navbar';
import { ApiProvider } from './context/ApiProvider';
import { Geist, Geist_Mono, Manrope, Merriweather } from 'next/font/google';
import DotBackground from '@/components/DotBackground';
import { ThemeProvider } from '@/components/theme/ThemeProvider';

export const metadata = {
  title: 'Repolens',
  description: 'Improving opensource education with AI',
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
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
    <html lang='en' suppressHydrationWarning>
      <body
        className={`${geist.variable} ${geistMono.variable} ${manrope.variable} font-sans antialiased`}
      >
        <ApiProvider>
          <ThemeProvider
            attribute='class'
            defaultTheme='system'
            enableSystem
            disableTransitionOnChange
          >
            <Navbar />

            <div className='relative grid h-full grid-cols-1 lg:grid-cols-[2.5rem_auto_2.5rem] xl:grid-cols-[auto_2rem_1200px_2rem_auto]'>
              <div className='relative col-start-1 h-full w-full overflow-y-auto lg:col-start-2 xl:col-start-3'>
                {children}
              </div>

              {/* <div className='border-border relative -right-px col-start-1 row-span-full row-start-1 border-x bg-[image:repeating-linear-gradient(135deg,var(--border)_0,var(--border)_1px,transparent_0,transparent_50%)] bg-[size:10px_10px] xl:col-start-2'></div> */}

              {/* <div className='border-border relative -left-px col-start-3 row-span-full row-start-1 border-x bg-[image:repeating-linear-gradient(315deg,var(--border)_0,var(--border)_1px,transparent_0,transparent_50%)] bg-[size:10px_10px] xl:col-start-4'></div> */}
            </div>
          </ThemeProvider>
        </ApiProvider>
      </body>
    </html>
  );
}
