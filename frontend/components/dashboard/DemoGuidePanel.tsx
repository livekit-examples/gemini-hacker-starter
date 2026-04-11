'use client';

import { useState } from 'react';
import { cn } from '@/lib/shadcn/utils';

export interface DemoScenario {
  title: string;
  description: string;
  steps: string[];
}

interface DemoGuidePanelProps {
  scenarios: DemoScenario[];
  className?: string;
}

function ScenarioCard({ scenario, index }: { scenario: DemoScenario; index: number }) {
  const [open, setOpen] = useState(false);

  return (
    <li className="rounded-[1.25rem] border border-graphite/60 bg-background/40 overflow-hidden">
      {/* Header — always visible, toggles the steps */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-accent/5 transition-colors"
        aria-expanded={open}
      >
        {/* Index pill */}
        <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full border border-accent/30 bg-accent/10 flex items-center justify-center font-mono text-[9px] text-accent/70">
          {index + 1}
        </span>

        <div className="flex-1 min-w-0">
          <p className="font-mono text-[9px] text-accent/70 uppercase tracking-widest leading-none mb-1">
            {scenario.title}
          </p>
          <p className="font-sans text-[11px] text-ghost/50 leading-snug">
            {scenario.description}
          </p>
        </div>

        {/* Chevron */}
        <svg
          className={cn(
            'flex-shrink-0 mt-1 w-3 h-3 text-ghost/30 transition-transform duration-200',
            open && 'rotate-180'
          )}
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M2 4l4 4 4-4" />
        </svg>
      </button>

      {/* Steps — shown when expanded */}
      {open && (
        <ol className="px-4 pb-4 flex flex-col gap-2 border-t border-graphite/40 pt-3">
          {scenario.steps.map((step, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <span className="flex-shrink-0 font-mono text-[9px] text-accent/40 mt-0.5 w-3 text-right">
                {i + 1}.
              </span>
              <p className="font-sans text-xs text-ghost/70 leading-relaxed italic">
                &ldquo;{step}&rdquo;
              </p>
            </li>
          ))}
        </ol>
      )}
    </li>
  );
}

export function DemoGuidePanel({ scenarios, className }: DemoGuidePanelProps) {
  if (!scenarios.length) return null;

  return (
    <div
      data-testid="demo-guide-panel"
      className={cn(
        'flex flex-col gap-3 rounded-[2rem] border border-graphite bg-[#05050A] p-5',
        className
      )}
    >
      <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
        Demo scenarios
      </span>

      <ul className="flex flex-col gap-2">
        {scenarios.map((scenario, i) => (
          <ScenarioCard key={scenario.title} scenario={scenario} index={i} />
        ))}
      </ul>
    </div>
  );
}
