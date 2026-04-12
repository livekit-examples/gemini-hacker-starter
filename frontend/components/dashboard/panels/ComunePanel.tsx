'use client';

import { useEffect, useState } from 'react';
import { RoomEvent } from 'livekit-client';
import { useRoomContext } from '@livekit/components-react';
import { Tag } from '@/components/design-system/Tag';
import { cn } from '@/lib/shadcn/utils';

// ── Type definitions matching the comune_tools.py output shapes ──────────────

interface ServiceRequirementsPayload {
  type: 'service_requirements';
  service: string;
  service_id: string;
  required_documents: string[];
  processing_days: number;
  fee_eur: number;
  office: string;
  bookable_online: boolean;
  notes: string;
  found: boolean;
}

interface ApplicationStatusPayload {
  type: 'application_status';
  application_id: string;
  service: string;
  status: 'pending' | 'approved' | 'rejected' | 'requires_documents';
  submitted_on: string;
  expected_by: string;
  notes: string;
  found: boolean;
}

interface AppointmentConfirmationPayload {
  type: 'appointment_confirmation';
  confirmation_id: string;
  service: string;
  citizen_name: string;
  date: string;
  time: string;
  office: string;
  instructions: string;
  found: boolean;
}

type ComunePayload =
  | ServiceRequirementsPayload
  | ApplicationStatusPayload
  | AppointmentConfirmationPayload;

interface ToolOutput {
  id: string;
  payload: ComunePayload | Record<string, unknown>;
  timestamp: number;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ── Service Requirements Card ─────────────────────────────────────────────────

function ServiceRequirementsCard({ payload }: { payload: ServiceRequirementsPayload }) {
  return (
    <div
      data-testid="service-requirements-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-start justify-between gap-2">
        <span className="font-serif italic text-ghost text-base leading-tight">
          {payload.service}
        </span>
        <Tag data-testid="tool-output-type">Service</Tag>
      </div>

      {payload.found ? (
        <>
          {/* Document checklist */}
          {payload.required_documents.length > 0 && (
            <div className="space-y-1.5">
              <span className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest">
                Required Documents
              </span>
              <ol className="space-y-1 list-none pl-0">
                {payload.required_documents.map((doc, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="font-mono text-[10px] text-accent/60 w-4 flex-shrink-0 mt-0.5">
                      {i + 1}.
                    </span>
                    <span className="font-sans text-sm text-ghost/80">{doc}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2">
            {payload.processing_days > 0 && (
              <span
                data-testid="processing-days-badge"
                className="font-mono text-[10px] text-ghost/60 bg-graphite/60 rounded-full px-2 py-0.5"
              >
                {payload.processing_days}d processing
              </span>
            )}
            {payload.fee_eur >= 0 && (
              <span
                data-testid="fee-badge"
                className="font-mono text-[10px] text-ghost/60 bg-graphite/60 rounded-full px-2 py-0.5"
              >
                €{payload.fee_eur.toFixed(2)}
              </span>
            )}
            {payload.bookable_online && (
              <span className="font-mono text-[10px] text-accent/70 bg-accent/10 border border-accent/20 rounded-full px-2 py-0.5">
                Online booking
              </span>
            )}
          </div>

          {/* Office */}
          {payload.office && (
            <Tag data-testid="office-tag">{payload.office}</Tag>
          )}

          {/* Notes */}
          {payload.notes && (
            <p className="font-sans text-xs text-ghost/50 italic">{payload.notes}</p>
          )}
        </>
      ) : (
        <p className="font-mono text-xs text-ghost/40">Service not found in catalogue.</p>
      )}
    </div>
  );
}

// ── Application Status Card ───────────────────────────────────────────────────

const STATUS_CONFIG = {
  approved: { label: 'Approved', classes: 'text-green-400 bg-green-400/10 border-green-400/30' },
  pending: { label: 'Pending', classes: 'text-amber-400 bg-amber-400/10 border-amber-400/30' },
  rejected: { label: 'Rejected', classes: 'text-red-400 bg-red-400/10 border-red-400/30' },
  requires_documents: {
    label: 'Requires Documents',
    classes: 'text-blue-400 bg-blue-400/10 border-blue-400/30',
  },
} as const;

function ApplicationStatusCard({ payload }: { payload: ApplicationStatusPayload }) {
  const statusCfg =
    STATUS_CONFIG[payload.status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.pending;

  return (
    <div
      data-testid="application-status-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-start justify-between gap-2">
        <span
          data-testid="application-id"
          className="font-mono text-sm text-ghost/80 break-all"
        >
          {payload.application_id}
        </span>
        <Tag data-testid="tool-output-type">Status</Tag>
      </div>

      {/* Status badge */}
      <div>
        <span
          data-testid="status-badge"
          className={cn(
            'inline-flex items-center font-mono text-[10px] uppercase tracking-wider rounded-full px-3 py-1 border',
            statusCfg.classes
          )}
        >
          {statusCfg.label}
        </span>
      </div>

      {payload.service && (
        <p className="font-sans text-sm text-ghost/70">{payload.service}</p>
      )}

      <div className="flex flex-wrap gap-3">
        {payload.submitted_on && (
          <div className="flex flex-col gap-0.5">
            <span className="font-mono text-[9px] text-ghost/35 uppercase tracking-widest">
              Submitted
            </span>
            <span className="font-mono text-[10px] text-ghost/60">{payload.submitted_on}</span>
          </div>
        )}
        {payload.expected_by && (
          <div className="flex flex-col gap-0.5">
            <span className="font-mono text-[9px] text-ghost/35 uppercase tracking-widest">
              Expected by
            </span>
            <span className="font-mono text-[10px] text-ghost/60">{payload.expected_by}</span>
          </div>
        )}
      </div>

      {payload.notes && (
        <p className="font-sans text-xs text-ghost/50 italic">{payload.notes}</p>
      )}
    </div>
  );
}

// ── Appointment Confirmation Card ─────────────────────────────────────────────

function AppointmentConfirmationCard({
  payload,
}: {
  payload: AppointmentConfirmationPayload;
}) {
  return (
    <div
      data-testid="appointment-confirmation-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-start justify-between gap-2">
        <span className="font-serif italic text-ghost text-base leading-tight">
          {payload.service}
        </span>
        <Tag data-testid="tool-output-type">Appointment</Tag>
      </div>

      {payload.found && payload.confirmation_id ? (
        <>
          <div className="flex flex-col gap-0.5">
            <span className="font-mono text-[9px] text-ghost/35 uppercase tracking-widest">
              Confirmation ID
            </span>
            <span
              data-testid="confirmation-id"
              className="font-mono text-sm text-accent"
            >
              {payload.confirmation_id}
            </span>
          </div>

          <div className="flex flex-wrap gap-3">
            {payload.date && (
              <div className="flex flex-col gap-0.5">
                <span className="font-mono text-[9px] text-ghost/35 uppercase tracking-widest">
                  Date
                </span>
                <span className="font-mono text-[10px] text-ghost/60">{payload.date}</span>
              </div>
            )}
            {payload.time && (
              <div className="flex flex-col gap-0.5">
                <span className="font-mono text-[9px] text-ghost/35 uppercase tracking-widest">
                  Time
                </span>
                <span className="font-mono text-[10px] text-ghost/60">{payload.time}</span>
              </div>
            )}
          </div>

          {payload.office && <Tag>{payload.office}</Tag>}
        </>
      ) : null}

      {payload.instructions && (
        <p className="font-sans text-xs text-ghost/60">{payload.instructions}</p>
      )}

      {payload.citizen_name && (
        <p className="font-mono text-[10px] text-ghost/40">{payload.citizen_name}</p>
      )}
    </div>
  );
}

// ── Generic fallback card ─────────────────────────────────────────────────────

function GenericCard({ output }: { output: ToolOutput }) {
  const payload = output.payload as Record<string, unknown>;
  return (
    <div
      data-testid="tool-output-card"
      className="rounded-2xl border border-graphite/60 bg-background p-4 space-y-3 animate-in fade-in duration-300"
    >
      <div className="flex items-center justify-between gap-2">
        <Tag data-testid="tool-output-type">
          {String(payload.type ?? 'unknown').replace(/_/g, ' ')}
        </Tag>
        <span className="font-mono text-[9px] text-ghost/35 flex-shrink-0">
          {formatTime(output.timestamp)}
        </span>
      </div>
      <pre className="font-mono text-xs text-ghost/60 whitespace-pre-wrap break-words leading-relaxed overflow-x-auto">
        {JSON.stringify(payload, null, 2)}
      </pre>
    </div>
  );
}

// ── Card dispatcher ───────────────────────────────────────────────────────────

function ComuneCard({ output }: { output: ToolOutput }) {
  const payload = output.payload as Record<string, unknown>;
  const type = payload.type as string;

  return (
    <div>
      <div className="flex justify-end mb-1">
        <span className="font-mono text-[9px] text-ghost/35">{formatTime(output.timestamp)}</span>
      </div>
      {type === 'service_requirements' ? (
        <ServiceRequirementsCard payload={payload as unknown as ServiceRequirementsPayload} />
      ) : type === 'application_status' ? (
        <ApplicationStatusCard payload={payload as unknown as ApplicationStatusPayload} />
      ) : type === 'appointment_confirmation' ? (
        <AppointmentConfirmationCard
          payload={payload as unknown as AppointmentConfirmationPayload}
        />
      ) : (
        <GenericCard output={output} />
      )}
    </div>
  );
}

// ── Panel container ───────────────────────────────────────────────────────────

interface ComunePanelProps {
  className?: string;
  resetVersion?: number;
}

export function ComunePanel({ className, resetVersion = 0 }: ComunePanelProps) {
  const [outputs, setOutputs] = useState<ToolOutput[]>([]);
  const room = useRoomContext();

  useEffect(() => {
    setOutputs([]);
  }, [resetVersion]);

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
          Comune — Tool Output
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {outputs.length === 0 && (
          <p className="font-mono text-xs text-ghost/30 text-center py-8">
            Service lookups will appear here.
          </p>
        )}
        {outputs.map((output) => (
          <ComuneCard key={output.id} output={output} />
        ))}
      </div>
    </div>
  );
}
