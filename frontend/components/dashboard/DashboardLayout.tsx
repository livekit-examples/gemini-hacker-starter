'use client';

import { cn } from '@/lib/shadcn/utils';
import { PersonaCard } from './PersonaCard';
import { TranscriptPanel } from './TranscriptPanel';
import { ToolOutputPanel } from './ToolOutputPanel';
import { SessionControls } from './SessionControls';
import { VoiceActivity } from './VoiceActivity';
import { DemoGuidePanel, type DemoScenario } from './DemoGuidePanel';
import { ComunePanel } from './panels/ComunePanel';

export interface LanguageInfo {
  code: string;
  display_name: string;
  flag: string;
  is_rtl: boolean;
}

export interface DemoConfig {
  slug: string;
  name: string;
  persona_name: string;
  persona_initials: string;
  persona_role: string;
  value_prop: string;
  accent: string;
  available: boolean;
  supported_languages: LanguageInfo[];
  demo_scenarios?: DemoScenario[];
  disclaimer?: Record<string, string>;
}

interface DashboardLayoutProps {
  config: DemoConfig;
  connectionState?: 'connected' | 'connecting' | 'idle';
  selectedLanguage?: string;
  onLanguageChange?: (code: string) => void;
  microphones?: Array<{ deviceId: string; label: string }>;
  selectedMicrophoneId?: string;
  onMicrophoneChange?: (deviceId: string) => void;
  onDisconnect?: () => void;
  onConnect?: () => void;
  onReset?: () => void;
  toolOutputResetVersion?: number;
  className?: string;
}

export function DashboardLayout({
  config,
  connectionState = 'idle',
  selectedLanguage = 'en',
  onLanguageChange,
  microphones,
  selectedMicrophoneId,
  onMicrophoneChange,
  onDisconnect = () => {},
  onConnect = () => {},
  onReset = () => {},
  toolOutputResetVersion = 0,
  className,
}: DashboardLayoutProps) {
  const currentLang = config.supported_languages.find((l) => l.code === selectedLanguage);
  const isRtl = currentLang?.is_rtl ?? false;

  return (
    <div
      data-testid="dashboard-layout"
      dir={isRtl ? 'rtl' : 'ltr'}
      className={cn(
        'flex flex-col lg:flex-row gap-4 px-4 pt-24 pb-6 lg:h-screen lg:overflow-hidden',
        className
      )}
    >
      {/* ── Left panel — 280px ──────────────────────────────────────── */}
      <div
        data-testid="dashboard-left"
        className="w-full lg:w-[280px] lg:flex-shrink-0 flex flex-col gap-4 lg:h-full lg:overflow-hidden"
      >
        <PersonaCard
          initials={config.persona_initials}
          name={config.persona_name}
          role={config.persona_role}
          connectionState={connectionState}
          language={currentLang ? `${currentLang.flag} ${currentLang.code.toUpperCase()}` : selectedLanguage.toUpperCase()}
        />
        {config.demo_scenarios?.length ? (
          <DemoGuidePanel scenarios={config.demo_scenarios} className="flex-1 overflow-y-auto min-h-0" />
        ) : null}
      </div>

      {/* ── Center panel — flex-1 ────────────────────────────────────── */}
      <div
        data-testid="dashboard-center"
        className="flex-1 flex flex-col gap-4 min-w-0 lg:h-full lg:overflow-hidden"
      >
        {/* Voice activity ring */}
        <VoiceActivity className="h-32 flex-shrink-0" />

        {/* Live transcript — fills remaining space and scrolls */}
        <TranscriptPanel className="flex-1 min-h-0 max-h-[50vh] lg:max-h-none" isRtl={isRtl} />
      </div>

      {/* ── Right panel — 320px ──────────────────────────────────────── */}
      <div
        data-testid="dashboard-right"
        className="w-full lg:w-[320px] lg:flex-shrink-0 flex flex-col gap-4 lg:h-full lg:overflow-hidden"
      >
        {config.slug === 'comune' ? (
          <ComunePanel
            className="flex-1 min-h-0 max-h-[50vh] lg:max-h-none"
            resetVersion={toolOutputResetVersion}
          />
        ) : (
          <ToolOutputPanel
            className="flex-1 min-h-0 max-h-[50vh] lg:max-h-none"
            resetVersion={toolOutputResetVersion}
          />
        )}
        <SessionControls
          languages={config.supported_languages}
          connectionState={connectionState}
          onDisconnect={onDisconnect}
          onConnect={onConnect}
          onReset={onReset}
          selectedLanguage={selectedLanguage}
          onLanguageChange={onLanguageChange}
          microphones={microphones}
          selectedMicrophoneId={selectedMicrophoneId}
          onMicrophoneChange={onMicrophoneChange}
        />
      </div>
    </div>
  );
}
