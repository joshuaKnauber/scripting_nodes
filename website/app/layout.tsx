import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Script from 'next/script';
import { Provider } from '@/components/provider';
import { appName, siteDescription, siteUrl } from '@/lib/shared';
import './global.css';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: appName, template: `%s | ${appName}` },
  description: siteDescription,
  openGraph: { siteName: appName, type: 'website', images: '/og/image.png' },
  twitter: { card: 'summary_large_image' },
};

const inter = Inter({
  subsets: ['latin'],
});

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <Provider>{children}</Provider>
        {/* Plausible analytics (self-hosted, no cookies) */}
        <Script
          defer
          data-domain="scriptingnodes.com"
          src="https://nudge-events.up.railway.app/js/script.js"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
