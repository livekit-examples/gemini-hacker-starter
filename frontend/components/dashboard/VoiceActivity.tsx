'use client';

import { useVoiceAssistant } from '@livekit/components-react';
import { Track } from 'livekit-client';
import { useLocalParticipant, useMultibandTrackVolume } from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';

export function VoiceActivity({ className }: { className?: string }) {
  const { state } = useVoiceAssistant();
  const { localParticipant } = useLocalParticipant();
  const isSpeaking = state === 'speaking';
  const isActive = state === 'listening' || state === 'thinking' || state === 'speaking';

  const micPublication = localParticipant.getTrackPublication(Track.Source.Microphone);
  const micTrackRef = micPublication
    ? {
        source: Track.Source.Microphone,
        participant: localParticipant,
        publication: micPublication,
      }
    : undefined;
  const bands = useMultibandTrackVolume(micTrackRef, {
    bands: 5,
    loPass: 80,
    hiPass: 280,
  });

  const micLevel = bands.length > 0 ? bands.reduce((a, b) => a + b, 0) / bands.length : 0;
  const isUserTalking = micLevel > 0.08;
  const pulseScale = 1 + Math.min(micLevel, 0.35);

  return (
    <div
      data-testid="voice-activity"
      className={cn('flex items-center justify-center', className)}
    >
      <div className="relative flex items-center justify-center">
        {/* Outer ping ring — animate for agent speech and user speech */}
        {(isSpeaking || isUserTalking) && (
          <span
            className="absolute inline-flex h-24 w-24 rounded-full border border-accent/30 animate-ping"
            style={{ animationDuration: '1.5s' }}
          />
        )}

        {/* Middle ring */}
        <span
          className={cn(
            'absolute inline-flex h-16 w-16 rounded-full border transition-all duration-500',
            isSpeaking || isUserTalking
              ? 'border-accent/60 scale-110'
              : isActive
                ? 'border-accent/30'
                : 'border-graphite/60'
          )}
          style={{ transform: `scale(${pulseScale})` }}
        />

        {/* Center dot */}
        <span
          className={cn(
            'inline-flex h-8 w-8 rounded-full transition-all duration-300',
            isSpeaking || isUserTalking
              ? 'bg-accent/80 scale-110'
              : isActive
                ? 'bg-accent/30'
                : 'bg-graphite/50'
          )}
          style={{ transform: `scale(${pulseScale})` }}
        />
      </div>
    </div>
  );
}
