'use client';

import { cn } from '@/lib/shadcn/utils';
import { Button } from '@/components/design-system/Button';
import type { LanguageInfo } from './DashboardLayout';

interface SessionControlsProps {
  languages: LanguageInfo[];
  onDisconnect: () => void;
  onReset: () => void;
  selectedLanguage?: string;
  onLanguageChange?: (code: string) => void;
  microphones?: Array<{ deviceId: string; label: string }>;
  selectedMicrophoneId?: string;
  onMicrophoneChange?: (deviceId: string) => void;
  className?: string;
}

export function SessionControls({
  languages,
  onDisconnect,
  onReset,
  selectedLanguage = 'en',
  onLanguageChange,
  microphones = [],
  selectedMicrophoneId,
  onMicrophoneChange,
  className,
}: SessionControlsProps) {
  return (
    <div
      data-testid="session-controls"
      className={cn(
        'flex flex-col gap-4 rounded-[2rem] border border-graphite bg-[#05050A] p-5',
        className
      )}
    >
      <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
        Controls
      </span>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="language-selector"
          className="font-mono text-[10px] text-ghost/50 uppercase tracking-widest"
        >
          Language
        </label>
        <select
          id="language-selector"
          data-testid="language-selector"
          value={selectedLanguage}
          onChange={(e) => onLanguageChange?.(e.target.value)}
          className="w-full bg-[#05050A] border border-graphite rounded-[2rem] px-4 py-2.5 font-mono text-xs text-ghost/70 focus:outline-none focus:border-accent/50 cursor-pointer"
          aria-label="Language selector"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.display_name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-2">
        <label
          htmlFor="microphone-selector"
          className="font-mono text-[10px] text-ghost/50 uppercase tracking-widest"
        >
          Microphone
        </label>
        <select
          id="microphone-selector"
          data-testid="microphone-selector"
          value={selectedMicrophoneId ?? ''}
          onChange={(e) => onMicrophoneChange?.(e.target.value)}
          className="w-full bg-[#05050A] border border-graphite rounded-[2rem] px-4 py-2.5 font-mono text-xs text-ghost/70 focus:outline-none focus:border-accent/50 cursor-pointer"
          aria-label="Microphone selector"
        >
          <option value="">Default microphone</option>
          {microphones.map((microphone) => (
            <option key={microphone.deviceId || microphone.label} value={microphone.deviceId}>
              {microphone.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-2">
        <Button
          variant="outline"
          data-testid="disconnect-button"
          onClick={onDisconnect}
          className="w-full justify-center"
        >
          Disconnect
        </Button>
        <Button
          variant="muted"
          data-testid="reset-button"
          onClick={onReset}
          className="w-full justify-center"
        >
          Reset Demo
        </Button>
      </div>
    </div>
  );
}
