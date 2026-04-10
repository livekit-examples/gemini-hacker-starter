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
      // fall through to empty list — backend unavailable
    }
  }
  return [];
}

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
