import { cn } from '@/lib/shadcn/utils';
import { ButtonHTMLAttributes } from 'react';

export type ButtonVariant = 'primary' | 'outline' | 'muted';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({
  variant = 'primary',
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const isMuted = variant === 'muted';
  return (
    <button
      className={cn(
        'rounded-full font-mono tracking-tight px-5 py-2 text-sm transition-colors',
        variant === 'primary' && 'bg-accent text-background hover:bg-accent/90',
        variant === 'outline' &&
          'border border-graphite text-ghost hover:border-ghost/30 bg-transparent',
        isMuted && 'bg-graphite/50 text-ghost/40 cursor-not-allowed opacity-60',
        className
      )}
      disabled={isMuted || disabled}
      {...props}
    >
      {children}
    </button>
  );
}
