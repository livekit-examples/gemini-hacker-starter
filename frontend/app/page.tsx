import { SectionHeader, Tag } from '@/components/design-system';
import { HeroReveal } from '@/components/landing/HeroReveal';
import { IndustryGrid } from '@/components/landing/IndustryGrid';
import type { DemoCardData } from '@/components/landing/DemoCard';

async function getDemos(): Promise<DemoCardData[]> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl}/api/demos`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        return (data.demos ?? []) as DemoCardData[];
      }
    } catch {
      // fall through to static fallback
    }
  }
  return FALLBACK_DEMOS;
}

const FALLBACK_DEMOS: DemoCardData[] = [
  {
    slug: 'sales',
    name: 'Sales Strategy',
    persona_name: 'Aria',
    persona_initials: 'AR',
    persona_role: 'Senior Sales Strategist',
    value_prop:
      'Analyse prospect screens in real time and generate tailored proposals on the fly — close faster with an AI co-pilot that knows your deal.',
    available: true,
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
  },
  {
    slug: 'manufacturing',
    name: 'Manufacturing & Quality',
    persona_name: 'Marco',
    persona_initials: 'MA',
    persona_role: 'Process & Quality Engineer',
    value_prop:
      'Detect visual defects on the production line and surface the right SOP in seconds — cut rework and keep compliance airtight.',
    available: false,
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
  },
  {
    slug: 'logistics',
    name: 'Logistics & Supply Chain',
    persona_name: 'Elena',
    persona_initials: 'EL',
    persona_role: 'Head of Logistics Operations',
    value_prop:
      'Track shipments, flag delays, and brief carrier performance in real time — keep your supply chain moving with zero blind spots.',
    available: false,
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
  },
  {
    slug: 'real_estate',
    name: 'Real Estate Advisory',
    persona_name: 'Sofia',
    persona_initials: 'SO',
    persona_role: 'Senior Property Advisor',
    value_prop:
      'Walk through a property on screen and receive live CMA analysis and buyer-profile summaries — turn viewings into offers faster.',
    available: false,
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
  },
  {
    slug: 'dental',
    name: 'Dental Practice',
    persona_name: 'Dr. Nour',
    persona_initials: 'DN',
    persona_role: 'Specialist in Restorative Dentistry',
    value_prop:
      'Review dental images with an AI specialist, retrieve patient briefs, and deliver multilingual aftercare instructions at the point of care.',
    available: false,
    supported_languages: ['EN', 'IT', 'AR-EG', 'AR-AE'],
  },
];

export default async function Page() {
  const demos = await getDemos();

  return (
    <main className="min-h-screen pb-24">
      {/* ── Hero ──────────────────────────────────────────────────── */}
      <section className="flex flex-col items-center text-center gap-6 px-6 pt-40 pb-24">
        <HeroReveal>
          <div className="flex flex-col items-center gap-6">
            <span className="reveal-text">
              <Tag>EXODIA Technologies</Tag>
            </span>

            <h1 className="reveal-text font-serif italic text-[clamp(2.5rem,8.2vw,7.5rem)] text-ghost leading-none">
              Voice{' '}
              <span className="text-accent underline decoration-accent">Intelligence</span>
            </h1>

            <p className="reveal-text font-serif italic text-[clamp(1rem,2.5vw,1.75rem)] text-accent">
              AI agents that see, hear, and act
            </p>

            <p className="reveal-text font-mono text-sm text-ghost/60 max-w-lg leading-relaxed">
              Five industry-specific multimodal voice agents — each one a fully operational demo
              ready to deploy inside your organisation.
            </p>
          </div>
        </HeroReveal>
      </section>

      {/* ── Industry grid ─────────────────────────────────────────── */}
      <section className="px-6 max-w-7xl mx-auto">
        <SectionHeader keyword="Demos" className="text-5xl mb-10 text-center">
          Industry Demos
        </SectionHeader>
        <IndustryGrid demos={demos} />
      </section>
    </main>
  );
}
