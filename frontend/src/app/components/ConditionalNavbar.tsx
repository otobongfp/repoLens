'use client';

import { usePathname } from 'next/navigation';
import Navbar from './Navbar';

export default function ConditionalNavbar() {
  const pathname = usePathname();

  // Only hide navbar on dashboard pages (not select page)
  const isDashboardPage = pathname.startsWith('/dashboard');

  if (isDashboardPage) {
    return null;
  }

  return <Navbar />;
}
