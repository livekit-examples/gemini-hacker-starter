import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
}

export function Card({ className, children, glow = true, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'group relative rounded-[2rem] border border-graphite bg-[#05050A] p-7',
        className
      )}
      {...props}
    >
      {glow && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 rounded-[2rem] opacity-0 transition-opacity duration-500 group-hover:opacity-10"
          style={{
            background: 'radial-gradient(circle at top left, #4DA6FF 0%, transparent 60%)',
          }}
        />
      )}
      {children}
    </div>
  );
}
