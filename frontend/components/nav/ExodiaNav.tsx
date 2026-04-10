'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import { Button } from '@/components/design-system';

const NAV_LINKS = [
  { label: 'Demos', href: '/#demos' },
  { label: 'Industries', href: '/#industries' },
  { label: 'About', href: '/#about' },
];

export function ExodiaNav() {
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    let cleanup: (() => void) | undefined;

    import('gsap').then(({ gsap }) => {
      if (!navRef.current) return;

      gsap.fromTo(
        navRef.current,
        { y: -32, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.9,
          ease: 'power3.out',
          clearProps: 'transform,opacity',
        }
      );

      cleanup = () => {
        gsap.killTweensOf(navRef.current);
      };
    });

    return () => cleanup?.();
  }, []);

  return (
    <nav
      ref={navRef}
      data-testid="exodia-nav"
      className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-8 rounded-full border border-graphite/60 bg-background/80 backdrop-blur-md px-6 py-3"
    >
      {/* Brand mark */}
      <Link
        href="/"
        className="font-sans font-bold tracking-widest text-sm whitespace-nowrap select-none"
      >
        EXOD<span className="text-accent">IA</span>{' '}
        <span className="text-ghost/40">Voice Intelligence</span>
      </Link>

      {/* Nav links */}
      <ul className="hidden md:flex items-center gap-6 list-none m-0 p-0">
        {NAV_LINKS.map(({ label, href }) => (
          <li key={label}>
            <Link
              href={href}
              className="font-mono text-xs uppercase tracking-widest text-ghost/50 hover:text-ghost transition-colors"
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>

      {/* CTA */}
      <Link href="/#demos">
        <Button variant="primary" className="text-xs px-4 py-2 whitespace-nowrap">
          Start Demo
        </Button>
      </Link>
    </nav>
  );
}
