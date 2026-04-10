import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

type DotState = 'connected' | 'connecting' | 'idle';

interface StatusDotProps extends HTMLAttributes<HTMLSpanElement> {
  state: DotState;
}

export function StatusDot({ state, className, ...props }: StatusDotProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest',
        className
      )}
      data-state={state}
      {...props}
    >
      <span
        className={cn(
          'h-2 w-2 rounded-full',
          state === 'connected' && 'bg-[#4ade80] animate-pulse',
          state === 'connecting' && 'bg-[#fbbf24] animate-pulse',
          state === 'idle' && 'bg-ghost/30'
        )}
      />
      {state}
    </span>
  );
}
