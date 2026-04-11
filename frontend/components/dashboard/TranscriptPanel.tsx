'use client';

import { useEffect, useRef, useState } from 'react';
import { type ReceivedMessage, useSessionContext, useSessionMessages } from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';

interface TestEntry {
  speaker: string;
  text: string;
  timestamp: number;
}

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function messageToEntry(m: ReceivedMessage): TestEntry {
  return {
    speaker: m.from?.isLocal ? 'You' : 'Agent',
    text: m.message ?? '',
    timestamp: m.timestamp,
  };
}

interface TranscriptPanelProps {
  className?: string;
  isRtl?: boolean;
}

export function TranscriptPanel({ className, isRtl = false }: TranscriptPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [testEntries, setTestEntries] = useState<TestEntry[]>([]);

  const session = useSessionContext();
  const { messages } = useSessionMessages(session);

  const lkEntries: TestEntry[] = messages.map(messageToEntry);

  // Test-only injection via custom DOM event (used in Playwright tests)
  useEffect(() => {
    const handler = (e: Event) => {
      const entry = (e as CustomEvent<TestEntry>).detail;
      setTestEntries((prev) => [...prev, entry]);
    };
    window.addEventListener('__transcript_entry__', handler);
    return () => window.removeEventListener('__transcript_entry__', handler);
  }, []);

  const entries = [...lkEntries, ...testEntries];

  // Auto-scroll to bottom whenever entries change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries.length]);

  return (
    <div
      data-testid="transcript-panel"
      className={cn(
        'flex flex-col rounded-[2rem] border border-graphite bg-[#05050A] overflow-hidden',
        className
      )}
    >
      <div className="px-5 py-3 border-b border-graphite/50 flex-shrink-0">
        <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
          Live Transcript
        </span>
      </div>

      <div
        ref={scrollRef}
        data-testid="transcript-scroll"
        className="flex-1 overflow-y-auto px-5 py-4 space-y-4 min-h-0"
      >
        {entries.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Session transcript will appear here.
          </p>
        )}

        {entries.map((entry, i) => (
          <div
            key={i}
            data-testid="transcript-entry"
            dir={isRtl ? 'rtl' : 'ltr'}
            className="animate-in fade-in duration-300"
          >
            <div className={cn('flex items-center gap-2 mb-1', isRtl && 'flex-row-reverse')}>
              <span className="font-mono text-[10px] text-accent uppercase tracking-widest">
                {entry.speaker}
              </span>
              <span className="font-mono text-[9px] text-ghost/30">
                {formatTime(entry.timestamp)}
              </span>
            </div>
            <p className={cn(
              'font-sans text-sm text-ghost/80 leading-relaxed',
              isRtl && 'text-right'
            )}>
              {entry.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
