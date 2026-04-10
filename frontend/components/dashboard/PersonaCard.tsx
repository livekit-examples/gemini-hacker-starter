'use client';

import { cn } from '@/lib/shadcn/utils';
import { Avatar } from '@/components/design-system/Avatar';
import { StatusDot } from '@/components/design-system/StatusDot';
import { Tag } from '@/components/design-system/Tag';

interface PersonaCardProps {
  initials: string;
  name: string;
  role: string;
  language?: string;
  connectionState?: 'connected' | 'connecting' | 'idle';
  className?: string;
}

export function PersonaCard({
  initials,
  name,
  role,
  language = 'EN',
  connectionState = 'idle',
  className,
}: PersonaCardProps) {
  return (
    <div
      data-testid="persona-card"
      className={cn(
        'flex flex-col gap-5 rounded-[2rem] border border-graphite bg-[#05050A] p-5',
        className
      )}
    >
      <div className="flex items-center gap-4">
        <Avatar initials={initials} size="lg" />
        <div className="flex flex-col gap-1 min-w-0">
          <span
            data-testid="persona-name"
            className="font-serif italic text-lg text-ghost leading-tight"
          >
            {name}
          </span>
          <span className="font-mono text-[10px] text-ghost/50 uppercase tracking-wider truncate">
            {role}
          </span>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <StatusDot state={connectionState} />
        <Tag>{language}</Tag>
      </div>
    </div>
  );
}
