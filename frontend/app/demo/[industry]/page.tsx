import { redirect } from 'next/navigation';
import type { DemoConfig } from '@/components/dashboard/DashboardLayout';
import { DemoClient } from './DemoClient';

/**
 * Static fallback configs used when the backend is unavailable.
 * Fields match the DemoConfig interface.
 */
const FALLBACK_CONFIGS: Record<string, DemoConfig> = {
  sales: {
    slug: 'sales',
    name: 'Sales Strategy',
    persona_name: 'Aria',
    persona_initials: 'AR',
    persona_role: 'Senior Sales Strategist',
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
    available: true,
  },
  manufacturing: {
    slug: 'manufacturing',
    name: 'Manufacturing & Quality',
    persona_name: 'Marco',
    persona_initials: 'MA',
    persona_role: 'Process & Quality Engineer',
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
    available: false,
  },
  logistics: {
    slug: 'logistics',
    name: 'Logistics & Supply Chain',
    persona_name: 'Elena',
    persona_initials: 'EL',
    persona_role: 'Head of Logistics Operations',
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
    available: false,
  },
  real_estate: {
    slug: 'real_estate',
    name: 'Real Estate Advisory',
    persona_name: 'Sofia',
    persona_initials: 'SO',
    persona_role: 'Senior Property Advisor',
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
    available: false,
  },
  dental: {
    slug: 'dental',
    name: 'Dental Practice',
    persona_name: 'Dr. Nour',
    persona_initials: 'DN',
    persona_role: 'Specialist in Restorative Dentistry',
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
    available: false,
  },
};

async function getDemoConfig(industry: string): Promise<DemoConfig | null> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/config?industry=${industry}`, {
        cache: 'no-store',
      });
      if (res.ok) {
        return (await res.json()) as DemoConfig;
      }
    } catch {
      // fall through to static fallback
    }
  }
  return FALLBACK_CONFIGS[industry] ?? null;
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
