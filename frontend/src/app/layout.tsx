import { subset } from 'd3';
import '../../styles/globals.css';
import Navbar from './components/Navbar';
import { ApiProvider } from './context/ApiProvider';
import { GraphDataProvider } from './context/GraphDataProvider';
import { Geist, Geist_Mono, Manrope, Merriweather } from 'next/font/google';
import DotBackground from '@/components/DotBackground';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { Toaster } from 'react-hot-toast';

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
          <GraphDataProvider>
            <ThemeProvider
              attribute='class'
              defaultTheme='system'
              enableSystem
              disableTransitionOnChange
            >
              <Navbar />

              {children}

              <Toaster
                position='top-right'
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: 'var(--card)',
                    color: 'var(--card-foreground)',
                    border: '1px solid var(--border)',
                  },
                  success: {
                    iconTheme: {
                      primary: 'var(--primary)',
                      secondary: 'var(--primary-foreground)',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: 'var(--destructive)',
                      secondary: 'var(--destructive-foreground)',
                    },
                  },
                }}
              />
            </ThemeProvider>
          </GraphDataProvider>
        </ApiProvider>
      </body>
    </html>
  );
}
