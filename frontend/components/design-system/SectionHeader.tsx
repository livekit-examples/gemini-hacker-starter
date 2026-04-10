import { cn } from '@/lib/shadcn/utils';
import { HTMLAttributes } from 'react';

interface SectionHeaderProps extends HTMLAttributes<HTMLHeadingElement> {
  /** The single word within children that should be accented and underlined */
  keyword: string;
}

export function SectionHeader({ children, keyword, className, ...props }: SectionHeaderProps) {
  const text = typeof children === 'string' ? children : '';
  const parts = text.split(keyword);

  return (
    <h2
      className={cn(
        'font-serif italic text-4xl text-ghost leading-none',
        className
      )}
      {...props}
    >
      {parts.map((part, i) => (
        <span key={i}>
          {part}
          {i < parts.length - 1 && (
            <span className="text-accent underline decoration-accent">{keyword}</span>
          )}
        </span>
      ))}
    </h2>
  );
}
