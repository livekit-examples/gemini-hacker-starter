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
// Severity badge colours
// ---------------------------------------------------------------------------

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'border-red-500/40 bg-red-500/10 text-red-400',
  major: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
  minor: 'border-green-500/40 bg-green-500/10 text-green-400',
};

function SeverityBadge({ severity }: { severity: string }) {
  const style = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.minor;
  return (
    <span
      data-testid="severity-badge"
      data-severity={severity}
      className={cn(
        'rounded-full border px-2 py-0.5 font-mono text-[9px] uppercase tracking-widest',
        style
      )}
    >
      {severity}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Defect detection card
// ---------------------------------------------------------------------------

interface DefectDetectionPayload {
  defect_type?: string;
  severity?: string;
  area?: string;
  recommended_action?: string;
}

function DefectDetectionCard({ output }: { output: ToolOutput }) {
  const p = output.payload as DefectDetectionPayload;
  const severity = p.severity ?? 'minor';
  const defectLabel = (p.defect_type ?? 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div
      data-testid="manufacturing-defect-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            Defect Detected
          </span>
          <SeverityBadge severity={severity} />
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>

      {/* Defect type */}
      <div>
        <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-0.5">
          Type
        </p>
        <p className="font-mono text-xs text-accent/80">{defectLabel}</p>
      </div>

      {/* Affected area */}
      {p.area && (
        <div>
          <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-0.5">
            Area
          </p>
          <p className="font-sans text-sm text-ghost/70">{p.area}</p>
        </div>
      )}

      {/* Recommended action */}
      {p.recommended_action && (
        <div>
          <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-0.5">
            Action Required
          </p>
          <p className="font-sans text-sm text-ghost/70 leading-relaxed">
            {p.recommended_action}
          </p>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Defect report card
// ---------------------------------------------------------------------------

interface DefectReportPayload {
  report?: string;
  defect_count?: number;
}

function DefectReportCard({ output }: { output: ToolOutput }) {
  const p = output.payload as DefectReportPayload;

  return (
    <div
      data-testid="manufacturing-defect-report-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            Defect Report
          </span>
          {p.defect_count !== undefined && (
            <span className="rounded-full border border-accent/20 bg-accent/5 px-2 py-0.5 font-mono text-[9px] text-accent/60 uppercase tracking-widest">
              {p.defect_count} defect{p.defect_count !== 1 ? 's' : ''}
            </span>
          )}
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>
      {p.report && (
        <pre className="font-mono text-xs text-ghost/60 whitespace-pre-wrap break-words leading-relaxed overflow-x-auto">
          {p.report}
        </pre>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// SOP lookup card
// ---------------------------------------------------------------------------

interface SopLookupPayload {
  procedure_id?: string;
  title?: string;
  steps?: string[];
  found?: boolean;
}

function SopLookupCard({ output }: { output: ToolOutput }) {
  const p = output.payload as SopLookupPayload;

  if (!p.found) {
    return (
      <div
        data-testid="manufacturing-sop-card"
        data-found="false"
        className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-2 animate-in fade-in duration-300"
      >
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            SOP Lookup
          </span>
          <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
            {formatTime(output.timestamp)}
          </span>
        </div>
        <p className="font-sans text-sm text-ghost/50 italic">
          No matching procedure found. Try a different keyword.
        </p>
      </div>
    );
  }

  return (
    <div
      data-testid="manufacturing-sop-card"
      data-found="true"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            SOP Lookup
          </span>
          {p.procedure_id && (
            <span className="font-mono text-[9px] text-ghost/40">{p.procedure_id}</span>
          )}
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>

      {/* Title */}
      {p.title && (
        <p className="font-sans text-sm font-medium text-ghost/80">{p.title}</p>
      )}

      {/* Steps */}
      {p.steps && p.steps.length > 0 && (
        <ol
          data-testid="sop-steps-list"
          className="space-y-2"
        >
          {p.steps.map((step, i) => (
            <li
              key={i}
              className="flex items-start gap-3"
            >
              <span className="font-mono text-[9px] text-accent/60 mt-0.5 flex-shrink-0 w-4 text-right">
                {i + 1}.
              </span>
              <span className="font-sans text-sm text-ghost/70 leading-relaxed">{step}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Fallback card
// ---------------------------------------------------------------------------

function GenericManufacturingCard({ output }: { output: ToolOutput }) {
  return (
    <div
      data-testid="manufacturing-generic-card"
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

function ManufacturingCard({ output }: { output: ToolOutput }) {
  if (output.type === 'defect_detection') return <DefectDetectionCard output={output} />;
  if (output.type === 'defect_report') return <DefectReportCard output={output} />;
  if (output.type === 'sop_lookup') return <SopLookupCard output={output} />;
  return <GenericManufacturingCard output={output} />;
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface ManufacturingPanelProps {
  className?: string;
  resetVersion?: number;
}

export function ManufacturingPanel({ className, resetVersion = 0 }: ManufacturingPanelProps) {
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

  // Test-only injection via custom DOM event
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
      data-testid="manufacturing-panel"
      className={cn(
        'flex flex-col rounded-[2rem] border border-graphite bg-[#05050A] overflow-hidden',
        className
      )}
    >
      <div className="px-5 py-3 border-b border-graphite/50 flex-shrink-0">
        <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
          Quality Intelligence
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {outputs.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Defect classifications and SOP lookups will appear here.
          </p>
        )}
        {outputs.map((output) => (
          <ManufacturingCard key={output.id} output={output} />
        ))}
      </div>
    </div>
  );
}
