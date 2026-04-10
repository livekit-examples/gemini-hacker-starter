'use client';

import { useEffect, useState } from 'react';
import { RoomEvent } from 'livekit-client';
import { useRoomContext } from '@livekit/components-react';
import { Tag } from '@/components/design-system/Tag';
import { cn } from '@/lib/shadcn/utils';

interface ToolOutput {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  timestamp: number;
}

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function ToolCard({ output }: { output: ToolOutput }) {
  return (
    <div
      data-testid="tool-output-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <Tag data-testid="tool-output-type">{output.type.replace(/_/g, ' ')}</Tag>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>
      <pre className="font-mono text-xs text-ghost/60 whitespace-pre-wrap break-words leading-relaxed overflow-x-auto">
        {JSON.stringify(output.payload, null, 2)}
      </pre>
    </div>
  );
}

export function ToolOutputPanel({ className }: { className?: string }) {
  const [outputs, setOutputs] = useState<ToolOutput[]>([]);
  const room = useRoomContext();

  // Listen to LiveKit data messages on "tool-output" topic
  useEffect(() => {
    const handler = (
      payload: Uint8Array,
      _participant: unknown,
      _kind: unknown,
      topic: string | undefined
    ) => {
      if (topic !== 'tool-output') return;
      try {
        const data = JSON.parse(new TextDecoder().decode(payload)) as Record<string, unknown>;
        const output: ToolOutput = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          type: (data.type as string) ?? 'unknown',
          payload: data,
          timestamp: Date.now(),
        };
        setOutputs((prev) => [output, ...prev].slice(0, 20));
      } catch {
        // ignore malformed payloads
      }
    };

    room.on(RoomEvent.DataReceived, handler);
    return () => {
      room.off(RoomEvent.DataReceived, handler);
    };
  }, [room]);

  // Test-only injection via custom DOM event (used in Playwright tests)
  useEffect(() => {
    const handler = (e: Event) => {
      const data = (e as CustomEvent<Record<string, unknown>>).detail;
      const output: ToolOutput = {
        id: `test-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        type: (data.type as string) ?? 'test',
        payload: data,
        timestamp: Date.now(),
      };
      setOutputs((prev) => [output, ...prev].slice(0, 20));
    };
    window.addEventListener('__tool_output__', handler);
    return () => window.removeEventListener('__tool_output__', handler);
  }, []);

  return (
    <div
      data-testid="tool-output-panel"
      className={cn(
        'flex flex-col rounded-[2rem] border border-graphite bg-[#05050A] overflow-hidden',
        className
      )}
    >
      <div className="px-5 py-3 border-b border-graphite/50 flex-shrink-0">
        <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
          Tool Output
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {outputs.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Tool results will appear here.
          </p>
        )}
        {outputs.map((output) => (
          <ToolCard key={output.id} output={output} />
        ))}
      </div>
    </div>
  );
}
