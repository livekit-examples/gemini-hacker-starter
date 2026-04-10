import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

interface TagProps extends HTMLAttributes<HTMLSpanElement> {}

export function Tag({ className, children, ...props }: TagProps) {
  return (
    <span
      className={cn(
        'rounded-full border border-accent/20 bg-accent/5 px-2 py-0.5 font-mono text-[9px] text-accent/60 uppercase tracking-widest',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
