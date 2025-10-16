/**
 * RepoLens Frontend - Main Layout Component
 *
 * Copyright (C) 2024 RepoLens Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import '../../styles/globals.css';
import ConditionalNavbar from './components/ConditionalNavbar';
import { ApiProvider } from './context/ApiProvider';
import { GraphDataProvider } from './context/GraphDataProvider';
import { AuthProvider } from './context/AuthProvider';
import { Geist, Geist_Mono, Manrope, Merriweather } from 'next/font/google';
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
          <AuthProvider>
            <GraphDataProvider>
              <ThemeProvider
                attribute='class'
                defaultTheme='system'
                enableSystem
                disableTransitionOnChange
              >
                <ConditionalNavbar />

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
          </AuthProvider>
        </ApiProvider>
      </body>
    </html>
  );
}
