'use client';

import { useEffect, useRef } from 'react';

interface HeroRevealProps {
  children: React.ReactNode;
}

export function HeroReveal({ children }: HeroRevealProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cleanup: (() => void) | undefined;

    import('gsap').then(({ gsap }) => {
      const targets = containerRef.current?.querySelectorAll('.reveal-text');
      if (!targets?.length) return;

      gsap.fromTo(
        targets,
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.9,
          ease: 'power3.out',
          stagger: 0.15,
          clearProps: 'transform,opacity',
        }
      );

      cleanup = () => {
        gsap.killTweensOf(targets);
      };
    });

    return () => cleanup?.();
  }, []);

  return <div ref={containerRef}>{children}</div>;
}
