import { redirect } from 'next/navigation';
import type { DemoConfig } from '@/components/dashboard/DashboardLayout';
import { DemoClient } from './DemoClient';

export const dynamic = 'force-dynamic';

async function getDemoConfig(industry: string): Promise<DemoConfig | null> {
  const backendUrl =
    process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backendUrl) return null;
  try {
    const res = await fetch(`${backendUrl}/api/config?industry=${industry}`, {
      cache: 'no-store',
    });
    if (res.ok) return (await res.json()) as DemoConfig;
  } catch {
    // backend unavailable
  }
  return null;
}

interface DemoPageProps {
  params: Promise<{ industry: string }>;
  searchParams: Promise<{ lang?: string }>;
}

export default async function DemoPage({ params, searchParams }: DemoPageProps) {
  const { industry } = await params;
  const { lang } = await searchParams;
  const config = await getDemoConfig(industry);

  if (!config) {
    redirect('/');
  }

  // Validate lang against supported languages; fall back to first supported
  const validLang = config.supported_languages.find((l) => l.code === lang);
  const initialLanguage = validLang?.code ?? config.supported_languages[0]?.code ?? 'en';

  return <DemoClient config={config} initialLanguage={initialLanguage} />;
}
