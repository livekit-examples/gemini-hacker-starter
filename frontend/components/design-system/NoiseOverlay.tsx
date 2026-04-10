export function NoiseOverlay() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-[100] opacity-[0.04] mix-blend-overlay"
      style={{ animation: 'noise-scroll 8s steps(2) infinite' }}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
        style={{ width: '200%', height: '200%', marginLeft: '-50%', marginTop: '-50%' }}
      >
        <filter id="exodia-noise">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.65"
            numOctaves="3"
            stitchTiles="stitch"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#exodia-noise)" />
      </svg>
    </div>
  );
}
