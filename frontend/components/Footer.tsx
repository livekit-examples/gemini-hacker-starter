import Link from 'next/link';

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-graphite bg-[#020205] rounded-t-[4rem] px-8 py-12 mt-24">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Brand mark */}
        <Link
          href="/"
          className="font-sans font-bold tracking-widest text-sm select-none"
        >
          EXOD<span className="text-accent">IA</span>{' '}
          <span className="text-ghost/40">Voice Intelligence</span>
        </Link>

        {/* Copyright */}
        <p className="font-mono text-base text-ghost/40">
          &copy; {year} EXODIA Technologies. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
