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
// Status badge
// ---------------------------------------------------------------------------

const STATUS_STYLES: Record<string, string> = {
  in_transit: 'border-accent/40 bg-accent/10 text-accent',
  delayed: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
  delivered: 'border-green-500/40 bg-green-500/10 text-green-400',
  customs_hold: 'border-red-500/40 bg-red-500/10 text-red-400',
};

const STATUS_LABELS: Record<string, string> = {
  in_transit: 'In Transit',
  delayed: 'Delayed',
  delivered: 'Delivered',
  customs_hold: 'Customs Hold',
};

function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? 'border-graphite/40 bg-graphite/10 text-ghost/50';
  const label = STATUS_LABELS[status] ?? status.replace(/_/g, ' ');
  return (
    <span
      data-testid="shipment-status-badge"
      data-status={status}
      className={cn(
        'rounded-full border px-2 py-0.5 font-mono text-[9px] uppercase tracking-widest',
        style
      )}
    >
      {label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Shipment lookup card
// ---------------------------------------------------------------------------

interface ShipmentPayload {
  tracking_id?: string;
  origin?: string;
  destination?: string;
  status?: string;
  eta?: string;
  carrier?: string;
  delay_days?: number;
  commodity?: string;
  last_update?: string;
  found?: boolean;
}

function ShipmentLookupCard({ output }: { output: ToolOutput }) {
  const p = output.payload as ShipmentPayload;

  if (!p.found) {
    return (
      <div
        data-testid="logistics-shipment-card"
        data-found="false"
        className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-2 animate-in fade-in duration-300"
      >
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            Shipment Lookup
          </span>
          <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
            {formatTime(output.timestamp)}
          </span>
        </div>
        <p className="font-sans text-sm text-ghost/50 italic">
          Tracking ID not found. Verify the ID and try again.
        </p>
      </div>
    );
  }

  return (
    <div
      data-testid="logistics-shipment-card"
      data-found="true"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
            Shipment
          </span>
          {p.status && <StatusBadge status={p.status} />}
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>

      {/* Tracking ID */}
      {p.tracking_id && (
        <p
          data-testid="shipment-tracking-id"
          className="font-mono text-xs text-accent/80"
        >
          {p.tracking_id}
        </p>
      )}

      {/* Route */}
      {p.origin && p.destination && (
        <div className="flex items-center gap-2 font-sans text-sm text-ghost/70">
          <span>{p.origin}</span>
          <span className="text-ghost/30">→</span>
          <span>{p.destination}</span>
        </div>
      )}

      {/* Meta row */}
      <div className="flex flex-wrap gap-2">
        {p.carrier && (
          <span className="rounded-full border border-graphite/40 px-2 py-0.5 font-mono text-[9px] text-ghost/50 uppercase tracking-widest">
            {p.carrier}
          </span>
        )}
        {p.eta && (
          <span className="rounded-full border border-graphite/40 px-2 py-0.5 font-mono text-[9px] text-ghost/50 uppercase tracking-widest">
            ETA {p.eta}
          </span>
        )}
        {p.delay_days !== undefined && p.delay_days > 0 && (
          <span className="rounded-full border border-amber-500/40 bg-amber-500/5 px-2 py-0.5 font-mono text-[9px] text-amber-400 uppercase tracking-widest">
            +{p.delay_days}d delay
          </span>
        )}
      </div>

      {/* Last update */}
      {p.last_update && (
        <p className="font-sans text-xs text-ghost/50 leading-relaxed italic">
          {p.last_update}
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Delay flag card
// ---------------------------------------------------------------------------

interface DelayFlagPayload {
  tracking_id?: string;
  reason?: string;
  confirmation?: string;
}

function DelayFlagCard({ output }: { output: ToolOutput }) {
  const p = output.payload as DelayFlagPayload;

  return (
    <div
      data-testid="logistics-delay-flag-card"
      className="rounded-2xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-2 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-amber-400/80 uppercase tracking-widest">
            Delay Flagged
          </span>
          {p.tracking_id && (
            <span className="font-mono text-[9px] text-ghost/40">{p.tracking_id}</span>
          )}
        </div>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>
      {p.reason && (
        <p className="font-sans text-sm text-ghost/70 leading-relaxed">{p.reason}</p>
      )}
      {p.confirmation && (
        <p className="font-mono text-[10px] text-green-400/70">{p.confirmation}</p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Carrier brief card
// ---------------------------------------------------------------------------

interface CarrierBriefPayload {
  carrier?: string;
  on_time_rate_pct?: number;
  avg_delay_days?: number;
  open_incidents?: number;
  active_routes?: string[];
  specialisations?: string[];
  recommendation?: string;
  found?: boolean;
}

function onTimeColor(rate: number): string {
  if (rate >= 90) return 'text-green-400';
  if (rate >= 80) return 'text-amber-400';
  return 'text-red-400';
}

function CarrierBriefCard({ output }: { output: ToolOutput }) {
  const p = output.payload as CarrierBriefPayload;

  if (!p.found) {
    return (
      <div
        data-testid="logistics-carrier-card"
        data-found="false"
        className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-2 animate-in fade-in duration-300"
      >
        <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
          Carrier Brief
        </span>
        <p className="font-sans text-sm text-ghost/50 italic">Carrier not found in database.</p>
      </div>
    );
  }

  return (
    <div
      data-testid="logistics-carrier-card"
      data-found="true"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-[9px] text-accent/60 uppercase tracking-widest">
          Carrier Brief
        </span>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>

      {/* Carrier name */}
      {p.carrier && (
        <p className="font-sans text-sm font-medium text-ghost/80">{p.carrier}</p>
      )}

      {/* Metrics row */}
      <div className="grid grid-cols-3 gap-2">
        {p.on_time_rate_pct !== undefined && (
          <div className="text-center">
            <p className={cn('font-mono text-base font-bold', onTimeColor(p.on_time_rate_pct))}>
              {p.on_time_rate_pct.toFixed(1)}%
            </p>
            <p className="font-mono text-[8px] text-ghost/40 uppercase tracking-widest mt-0.5">
              On-Time
            </p>
          </div>
        )}
        {p.avg_delay_days !== undefined && (
          <div className="text-center">
            <p className="font-mono text-base font-bold text-ghost/70">
              {p.avg_delay_days.toFixed(1)}d
            </p>
            <p className="font-mono text-[8px] text-ghost/40 uppercase tracking-widest mt-0.5">
              Avg Delay
            </p>
          </div>
        )}
        {p.open_incidents !== undefined && (
          <div className="text-center">
            <p className={cn(
              'font-mono text-base font-bold',
              p.open_incidents > 5 ? 'text-red-400' : p.open_incidents > 2 ? 'text-amber-400' : 'text-green-400'
            )}>
              {p.open_incidents}
            </p>
            <p className="font-mono text-[8px] text-ghost/40 uppercase tracking-widest mt-0.5">
              Incidents
            </p>
          </div>
        )}
      </div>

      {/* Recommendation */}
      {p.recommendation && (
        <div>
          <p className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest mb-1">
            Recommendation
          </p>
          <p className="font-sans text-xs text-ghost/60 leading-relaxed">{p.recommendation}</p>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Fallback card
// ---------------------------------------------------------------------------

function GenericLogisticsCard({ output }: { output: ToolOutput }) {
  return (
    <div
      data-testid="logistics-generic-card"
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

function LogisticsCard({ output }: { output: ToolOutput }) {
  if (output.type === 'shipment_lookup') return <ShipmentLookupCard output={output} />;
  if (output.type === 'delay_flag') return <DelayFlagCard output={output} />;
  if (output.type === 'carrier_brief') return <CarrierBriefCard output={output} />;
  return <GenericLogisticsCard output={output} />;
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface LogisticsPanelProps {
  className?: string;
  resetVersion?: number;
}

export function LogisticsPanel({ className, resetVersion = 0 }: LogisticsPanelProps) {
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
      data-testid="logistics-panel"
      className={cn(
        'flex flex-col rounded-[2rem] border border-graphite bg-[#05050A] overflow-hidden',
        className
      )}
    >
      <div className="px-5 py-3 border-b border-graphite/50 flex-shrink-0">
        <span className="font-mono text-[10px] text-ghost/40 uppercase tracking-widest">
          Operations Intelligence
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {outputs.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Shipment status, delay flags, and carrier briefs will appear here.
          </p>
        )}
        {outputs.map((output) => (
          <LogisticsCard key={output.id} output={output} />
        ))}
      </div>
    </div>
  );
}
