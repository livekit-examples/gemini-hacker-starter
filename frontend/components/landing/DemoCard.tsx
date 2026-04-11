'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ActivePill, Avatar, Button, Card, Tag } from '@/components/design-system';
import type { LanguageInfo } from '@/components/dashboard/DashboardLayout';

export interface DemoCardData {
  slug: string;
  name: string;
  persona_name: string;
  persona_initials: string;
  persona_role: string;
  value_prop: string;
  accent: string;
  available: boolean;
  supported_languages: LanguageInfo[];
  disclaimer?: Record<string, string>;
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
  const [selectedLang, setSelectedLang] = useState(
    supported_languages[0]?.code ?? 'en'
  );

  const demoHref = `/demo/${slug}?lang=${selectedLang}`;

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

      {/* Language selector */}
      {supported_languages.length > 0 && (
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor={`lang-${slug}`}
            className="font-mono text-[9px] text-ghost/40 uppercase tracking-widest"
          >
            Language
          </label>
          <select
            id={`lang-${slug}`}
            data-testid="demo-card-language-selector"
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            className="w-full bg-[#05050A] border border-graphite rounded-[2rem] px-3 py-2 font-mono text-[11px] text-ghost/70 focus:outline-none focus:border-accent/50 cursor-pointer"
            aria-label={`Language for ${name} demo`}
          >
            {supported_languages.map((lang) => (
              <option key={lang.code} value={lang.code} data-testid="language-tag">
                {lang.flag} {lang.display_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* CTA */}
      <div className="mt-auto pt-1">
        {available ? (
          <Link href={demoHref} aria-label={`View ${name} demo`}>
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
