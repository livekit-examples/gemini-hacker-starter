'use client';

import { useEffect, useState } from 'react';
import { RoomEvent } from 'livekit-client';
import { useRoomContext } from '@livekit/components-react';
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

// ---------------------------------------------------------------------------
// Priority badge colours
// ---------------------------------------------------------------------------

const PRIORITY_STYLES: Record<string, string> = {
  high: 'border-red-500/40 bg-red-500/10 text-red-400',
  medium: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
  low: 'border-green-500/40 bg-green-500/10 text-green-400',
};

function PriorityBadge({ priority }: { priority: string }) {
  const style = PRIORITY_STYLES[priority] ?? PRIORITY_STYLES.medium;
  return (
    <span
      data-testid="priority-badge"
      data-priority={priority}
      className={cn(
        'rounded-full border px-2 py-0.5 font-mono text-[9px] uppercase tracking-widest',
        style
      )}
    >
      {priority}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Talking-points card
// ---------------------------------------------------------------------------

interface TalkingPointsPayload {
  priority?: string;
  findings?: string[];
  recommendations?: string[];
  points?: string[];
  count?: number;
}

function TalkingPointsCard({ output }: { output: ToolOutput }) {
  const p = output.payload as TalkingPointsPayload;
  const priority = p.priority ?? 'medium';

  // Support both direct `points` list (from log_talking_points) and
  // findings/recommendations structure (from analyze_screen_content)
  const hasFindingsRecs =
    Array.isArray(p.findings) && Array.isArray(p.recommendations);
  const hasPoints = Array.isArray(p.points) && p.points.length > 0;

  return (
    <div
      data-testid="sales-talking-points-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            {hasFindingsRecs ? 'Screen Analysis' : 'Talking Points'}
          </span>
          <PriorityBadge priority={priority} />
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>

      {/* Findings */}
      {hasFindingsRecs && p.findings && p.findings.length > 0 && (
        <div>
          <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-1.5">
            Findings
          </p>
          <ul className="space-y-1">
            {p.findings.map((finding, i) => (
              <li
                key={i}
                className="flex items-start gap-2 font-sans text-sm text-ghost/70"
              >
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent/50" />
                {finding}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {hasFindingsRecs && p.recommendations && p.recommendations.length > 0 && (
        <div>
          <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-1.5">
            Recommendations
          </p>
          <ul className="space-y-1">
            {p.recommendations.map((rec, i) => (
              <li
                key={i}
                className="flex items-start gap-2 font-sans text-sm text-ghost/70"
              >
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent/70" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Direct talking points list */}
      {hasPoints && p.points && (
        <ul className="space-y-1">
          {p.points.map((pt, i) => (
            <li
              key={i}
              className="flex items-start gap-2 font-sans text-sm text-ghost/70"
            >
              <span className="font-mono text-[9px] text-accent/60 mt-0.5 flex-shrink-0">
                {String(i + 1).padStart(2, '0')}
              </span>
              {pt}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Proposal section card
// ---------------------------------------------------------------------------

interface ProposalSectionPayload {
  section?: string;
  content?: string;
  context?: string;
}

function ProposalSectionCard({ output }: { output: ToolOutput }) {
  const p = output.payload as ProposalSectionPayload;
  const sectionLabel = (p.section ?? 'Section')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div
      data-testid="sales-proposal-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
          Proposal · {sectionLabel}
        </span>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>
      {p.context && (
        <p className="font-mono text-[9px] text-ghost/40">{p.context}</p>
      )}
      {p.content && (
        <p className="font-sans text-sm text-ghost/70 leading-relaxed">{p.content}</p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Fallback card for unknown types
// ---------------------------------------------------------------------------

function GenericSalesCard({ output }: { output: ToolOutput }) {
  return (
    <div
      data-testid="sales-generic-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
          {output.type.replace(/_/g, ' ')}
        </span>
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

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

function SalesCard({ output }: { output: ToolOutput }) {
  if (output.type === 'talking_points') return <TalkingPointsCard output={output} />;
  if (output.type === 'proposal_section') return <ProposalSectionCard output={output} />;
  return <GenericSalesCard output={output} />;
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface SalesPanelProps {
  className?: string;
  resetVersion?: number;
}

export function SalesPanel({ className, resetVersion = 0 }: SalesPanelProps) {
  const [outputs, setOutputs] = useState<ToolOutput[]>([]);
  const room = useRoomContext();

  useEffect(() => {
    setOutputs([]);
  }, [resetVersion]);

  // LiveKit data messages on "tool-output" topic
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
    return () => { room.off(RoomEvent.DataReceived, handler); };
  }, [room]);

  // Test-only injection via custom DOM event (mirrors ToolOutputPanel pattern)
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
      data-testid="sales-panel"
      className={cn(
        'flex flex-col rounded-[2rem] border border-graphite bg-[#05050A] overflow-hidden',
        className
      )}
    >
      <div className="px-5 py-3 border-b border-graphite/50 flex-shrink-0">
        <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
          Sales Intelligence
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {outputs.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Analysis and talking points will appear here.
          </p>
        )}
        {outputs.map((output) => (
          <SalesCard key={output.id} output={output} />
        ))}
      </div>
    </div>
  );
}
