import { Inter } from 'next/font/google';
import Script from 'next/script';
import { Provider } from '@/components/provider';
import './global.css';

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
