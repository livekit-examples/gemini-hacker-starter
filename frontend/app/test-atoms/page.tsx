/**
 * Test harness page for design system atoms.
 * Used exclusively by Playwright E2E tests — not linked from any user-facing UI.
 */
import {
  ActivePill,
  Avatar,
  Button,
  Card,
  SectionHeader,
  StatusDot,
  Tag,
} from '@/components/design-system';

export default function TestAtomsPage() {
  return (
    <main className="p-8 space-y-8 bg-background min-h-screen">
      <h1 className="font-mono text-ghost text-sm uppercase tracking-widest">
        Design System — Atom Test Harness
      </h1>

      {/* Buttons */}
      <section className="flex gap-4 items-center">
        <Button variant="primary" data-testid="btn-primary">
          Primary
        </Button>
        <Button variant="outline" data-testid="btn-outline">
          Outline
        </Button>
        <Button variant="muted" data-testid="btn-muted">
          Muted
        </Button>
      </section>

      {/* Card */}
      <Card data-testid="card">
        <p className="text-ghost/70 text-sm">Card content</p>
      </Card>

      {/* Tag */}
      <section className="flex gap-2">
        <Tag data-testid="tag">Sales</Tag>
        <Tag data-testid="tag-industry">Manufacturing</Tag>
      </section>

      {/* ActivePill */}
      <ActivePill label="View Demo" data-testid="active-pill" />

      {/* StatusDot */}
      <section className="flex flex-col gap-2">
        <StatusDot state="connected" data-testid="status-connected" />
        <StatusDot state="connecting" data-testid="status-connecting" />
        <StatusDot state="idle" data-testid="status-idle" />
      </section>

      {/* Avatar */}
      <section className="flex gap-4">
        <Avatar initials="AR" data-testid="avatar-ar" />
        <Avatar initials="SO" size="lg" data-testid="avatar-so" />
      </section>

      {/* SectionHeader */}
      <SectionHeader keyword="Smart" data-testid="section-header">
        Powerful Smart Solutions
      </SectionHeader>
    </main>
  );
}
