'use client';

import { cn } from '@/lib/shadcn/utils';
import { PersonaCard } from './PersonaCard';
import { TranscriptPanel } from './TranscriptPanel';
import { ToolOutputPanel } from './ToolOutputPanel';
import { SessionControls } from './SessionControls';
import { VoiceActivity } from './VoiceActivity';

export interface DemoConfig {
  slug: string;
  name: string;
  persona_name: string;
  persona_initials: string;
  persona_role: string;
  value_prop: string;
  accent: string;
  available: boolean;
  supported_languages: string[];
  disclaimer?: Record<string, string>;
}

interface DashboardLayoutProps {
  config: DemoConfig;
  connectionState?: 'connected' | 'connecting' | 'idle';
  selectedLanguage?: string;
  onLanguageChange?: (code: string) => void;
  onDisconnect?: () => void;
  onReset?: () => void;
  className?: string;
}

export function DashboardLayout({
  config,
  connectionState = 'idle',
  selectedLanguage = 'en',
  onLanguageChange,
  onDisconnect = () => {},
  onReset = () => {},
  className,
}: DashboardLayoutProps) {
  return (
    <div
      data-testid="dashboard-layout"
      className={cn(
        'flex flex-col lg:flex-row gap-4 px-4 pt-24 pb-6 min-h-screen',
        className
      )}
    >
      {/* ── Left panel — 280px ──────────────────────────────────────── */}
      <div
        data-testid="dashboard-left"
        className="w-full lg:w-[280px] lg:flex-shrink-0 flex flex-col gap-4"
      >
        <PersonaCard
          initials={config.persona_initials}
          name={config.persona_name}
          role={config.persona_role}
          connectionState={connectionState}
          language={selectedLanguage.toUpperCase()}
        />
      </div>

      {/* ── Center panel — flex-1 ────────────────────────────────────── */}
      <div
        data-testid="dashboard-center"
        className="flex-1 flex flex-col gap-4 min-w-0"
      >
        {/* Voice activity ring */}
        <VoiceActivity className="h-32 flex-shrink-0" />

        {/* Live transcript — fills remaining space */}
        <TranscriptPanel className="flex-1 min-h-[200px]" />
      </div>

      {/* ── Right panel — 320px ──────────────────────────────────────── */}
      <div
        data-testid="dashboard-right"
        className="w-full lg:w-[320px] lg:flex-shrink-0 flex flex-col gap-4"
      >
        <ToolOutputPanel className="flex-1 min-h-[200px]" />
        <SessionControls
          onDisconnect={onDisconnect}
          onReset={onReset}
          selectedLanguage={selectedLanguage}
          onLanguageChange={onLanguageChange}
        />
      </div>
    </div>
  );
}
