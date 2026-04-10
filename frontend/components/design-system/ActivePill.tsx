import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

interface ActivePillProps extends HTMLAttributes<HTMLDivElement> {
  label: string;
}

export function ActivePill({ label, className, ...props }: ActivePillProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-3 py-1.5 font-mono text-[10px] text-accent uppercase tracking-widest',
        className
      )}
      {...props}
    >
      <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
      {label}
    </div>
  );
}
