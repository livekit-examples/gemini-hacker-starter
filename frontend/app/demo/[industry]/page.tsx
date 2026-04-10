import { redirect } from 'next/navigation';
import type { DemoConfig } from '@/components/dashboard/DashboardLayout';
import { DemoClient } from './DemoClient';

async function getDemoConfig(industry: string): Promise<DemoConfig | null> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
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
}

export default async function DemoPage({ params }: DemoPageProps) {
  const { industry } = await params;
  const config = await getDemoConfig(industry);

  if (!config) {
    redirect('/');
  }

  return <DemoClient config={config} />;
}
