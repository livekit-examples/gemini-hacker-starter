import Link from 'next/link';
import { ActivePill, Avatar, Button, Card, Tag } from '@/components/design-system';

export interface DemoCardData {
  slug: string;
  name: string;
  persona_name: string;
  persona_initials: string;
  persona_role: string;
  value_prop: string;
  available: boolean;
  supported_languages: string[];
}

export function DemoCard({
  slug,
  name,
  persona_name,
  persona_initials,
  persona_role,
  value_prop,
  available,
  supported_languages,
}: DemoCardData) {
  return (
    <Card data-testid="demo-card" className="flex flex-col gap-5">
      {/* Persona header */}
      <div className="flex items-center gap-4">
        <Avatar initials={persona_initials} size="lg" data-testid="avatar" />
        <div className="flex flex-col gap-1.5 min-w-0">
          <p
            data-testid="persona-name"
            className="font-serif italic text-xl text-ghost leading-none truncate"
          >
            {persona_name}
          </p>
          <p className="font-mono text-[10px] text-ghost/50 uppercase tracking-widest truncate">
            {persona_role}
          </p>
        </div>
      </div>

      {/* Industry label */}
      <Tag className="self-start">{name}</Tag>

      {/* Value prop */}
      <p className="font-sans text-sm text-ghost/70 leading-relaxed flex-1">{value_prop}</p>

      {/* Language tags */}
      <div className="flex flex-wrap gap-1.5">
        {supported_languages.map((lang) => (
          <Tag key={lang} data-testid="language-tag">
            {lang}
          </Tag>
        ))}
      </div>

      {/* CTA */}
      <div className="mt-auto pt-1">
        {available ? (
          <Link href={`/demo/${slug}`} aria-label={`View ${name} demo`}>
            <ActivePill label="View Demo" />
          </Link>
        ) : (
          <Button variant="muted" className="w-full text-xs">
            Coming Soon
          </Button>
        )}
      </div>
    </Card>
  );
}
