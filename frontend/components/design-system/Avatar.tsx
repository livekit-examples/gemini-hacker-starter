import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

type AvatarSize = 'sm' | 'md' | 'lg';

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  initials: string;
  size?: AvatarSize;
}

export function Avatar({ initials, size = 'md', className, ...props }: AvatarProps) {
  return (
    <div
      className={cn(
        'rounded-full border-2 border-graphite flex items-center justify-center font-serif italic text-accent/80 select-none',
        size === 'sm' && 'h-8 w-8 text-sm',
        size === 'md' && 'h-12 w-12 text-xl',
        size === 'lg' && 'h-16 w-16 text-2xl',
        className
      )}
      style={{ background: 'radial-gradient(circle at 30% 30%, #1a1a2e 0%, #05050A 70%)' }}
      {...props}
    >
      {initials}
    </div>
  );
}
