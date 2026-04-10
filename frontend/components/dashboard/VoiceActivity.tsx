'use client';

import { useVoiceAssistant } from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';

export function VoiceActivity({ className }: { className?: string }) {
  const { state } = useVoiceAssistant();
  const isSpeaking = state === 'speaking';
  const isActive = state === 'listening' || state === 'thinking' || state === 'speaking';

  return (
    <div
      data-testid="voice-activity"
      className={cn('flex items-center justify-center', className)}
    >
      <div className="relative flex items-center justify-center">
        {/* Outer ping ring — only when speaking */}
        {isSpeaking && (
          <span
            className="absolute inline-flex h-24 w-24 rounded-full border border-accent/30 animate-ping"
            style={{ animationDuration: '1.5s' }}
          />
        )}

        {/* Middle ring */}
        <span
          className={cn(
            'absolute inline-flex h-16 w-16 rounded-full border transition-all duration-500',
            isSpeaking
              ? 'border-accent/60 scale-110'
              : isActive
                ? 'border-accent/30'
                : 'border-graphite/60'
          )}
        />

        {/* Center dot */}
        <span
          className={cn(
            'inline-flex h-8 w-8 rounded-full transition-all duration-300',
            isSpeaking
              ? 'bg-accent/80 scale-110'
              : isActive
                ? 'bg-accent/30'
                : 'bg-graphite/50'
          )}
        />
      </div>
    </div>
  );
}
