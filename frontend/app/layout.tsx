import { Fira_Code, Instrument_Serif, Sora } from 'next/font/google';
import { headers } from 'next/headers';
import { ThemeProvider } from '@/components/app/theme-provider';
import { NoiseOverlay } from '@/components/design-system/NoiseOverlay';
import { ExodiaNav } from '@/components/nav/ExodiaNav';
import { Footer } from '@/components/Footer';
import { cn } from '@/lib/shadcn/utils';
import { getAppConfig, getStyles } from '@/lib/utils';
import '@/styles/globals.css';

const sora = Sora({
  variable: '--font-sora',
  subsets: ['latin'],
  display: 'swap',
});

const instrumentSerif = Instrument_Serif({
  variable: '--font-instrument-serif',
  subsets: ['latin'],
  weight: '400',
  style: ['normal', 'italic'],
  display: 'swap',
});

const firaCode = Fira_Code({
  variable: '--font-fira-code',
  subsets: ['latin'],
  display: 'swap',
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);
  const styles = getStyles(appConfig);
  const { pageTitle, pageDescription } = appConfig;

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        sora.variable,
        instrumentSerif.variable,
        firaCode.variable,
        'scroll-smooth font-sans antialiased'
      )}
    >
      <head>
        {styles && <style>{styles}</style>}
        <title>{pageTitle}</title>
        <meta name="description" content={pageDescription} />
        <link rel="icon" type="image/jpeg" href="/exodia-logo.jpeg" />
        <link rel="apple-touch-icon" sizes="180x180" href="/exodia-logo.jpeg" />
        <link rel="mask-icon" href="/exodia-logo.jpeg" color="#4DA6FF" />
      </head>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <NoiseOverlay />
          <ExodiaNav />
          {children}
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
