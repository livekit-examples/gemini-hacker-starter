# EXODIA Technologies — Style Guide

A reference for building consistent EXODIA-branded interfaces across all demo and product websites.

---

## Design Principles

- **Dark-first.** Every surface is near-black. Light is used sparingly as accent.
- **Precision over decoration.** Minimal UI. Every element earns its place.
- **Mono for data, serif for voice, sans for body.** Typography carries the tone.
- **Plasma blue as the single brand signal.** One accent color. No secondary palette.

---

## Color Tokens

| Token | Hex | Usage |
|---|---|---|
| `background` | `#0A0A14` | Page background (Deep Void) |
| `accent` | `#4DA6FF` | Brand highlight, CTAs, hover states (Plasma) |
| `ghost` | `#F0EFF4` | Primary text, headings |
| `graphite` | `#18181B` | Card borders, container backgrounds |

### Opacity Scale (applied to `ghost` and `accent`)

| Usage | Class example |
|---|---|
| Primary text | `text-ghost` |
| Secondary text | `text-ghost/70` |
| Muted text | `text-ghost/50` |
| Subtle / label | `text-ghost/40` |
| Near-invisible | `text-ghost/35` |
| Accent border | `border-accent/30` |
| Accent hover | `hover:border-accent/40` |
| Accent fill | `bg-accent/5`, `bg-accent/10` |

### Surface Colors (not in Tailwind config — use inline or extend)

| Usage | Value |
|---|---|
| Section dark card | `#05050A` |
| Slightly lifted card | `#07070F` |
| Logos strip background | `#04040A` |

---

## Typography

### Font Stack

```css
/* Google Fonts import */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=Sora:wght@100;200;300;400;500;600;700;800&display=swap');
```

| Role | Family | Tailwind class | Notes |
|---|---|---|---|
| Body / UI | Sora | `font-sans` | Default for paragraphs and labels |
| Display / Voice | Instrument Serif | `font-serif` | Used italic for headlines and pull quotes |
| Code / Data | Fira Code | `font-mono` | Labels, tags, nav items, status text |

### Type Scale Usage

```
Section headings    font-serif italic text-4xl–6xl text-ghost leading-none tracking-tight
Page title (hero)   font-sans font-bold uppercase text-ghost ~8vw leading-[0.84]
Accent italic line  font-serif italic text-accent ~7.5vw
Body copy           font-sans text-sm–xl font-light leading-relaxed text-ghost/70
Mono label          font-mono text-[10px]–text-sm uppercase tracking-widest text-accent
Pull quote          font-serif italic text-2xl–3xl text-ghost/80 leading-relaxed
```

### Sizing Convention

Use `clamp()` for fluid hero text rather than breakpoint overrides:

```html
text-[clamp(2rem,8.2vw,8rem)]   <!-- large display -->
text-[clamp(1rem,2.1vw,1.55rem)]  <!-- hero body -->
text-[clamp(0.72rem,1.1vw,0.95rem)]  <!-- mono labels -->
```

---

## Spacing & Layout

- **Page padding:** `px-6 sm:px-12 md:px-24`
- **Section vertical padding:** `py-24` to `py-32`
- **Max content width:** `max-w-6xl mx-auto` (general) · `max-w-3xl` (prose / manifesto)
- **Card gap in carousels:** `gap-5` (20px)
- **Card width (standard):** `300px` — set via `style={{ width: 300 }}`

---

## Border Radius

| Component | Class |
|---|---|
| Cards | `rounded-[2rem]` |
| Buttons, pills | `rounded-full` |
| Logo tiles | `rounded-xl` |
| Avatar circles | `rounded-full` |

---

## Cards

Standard dark card pattern:

```html
<div class="group relative flex flex-col overflow-hidden rounded-[2rem]
            border border-graphite bg-[#05050A] p-7
            hover:border-accent/40 transition-all duration-500 hover:bg-[#07070F]">

  <!-- Ambient hover glow (top-right corner) -->
  <div class="pointer-events-none absolute -right-10 -top-10 h-36 w-36 rounded-full
              bg-accent opacity-0 blur-[80px]
              transition-opacity duration-700 group-hover:opacity-10" />

  <!-- content -->
</div>
```

---

## Buttons

Three variants. All use `rounded-full font-mono tracking-tight`.

### Primary

```html
<button class="relative overflow-hidden rounded-full px-6 py-3
               font-mono text-base tracking-tight
               bg-accent text-white">
  <!-- GSAP fill-up wipe on hover: white bg slides up, text turns accent -->
</button>
```

### Outline

```html
<button class="rounded-full px-6 py-3 font-mono text-base tracking-tight
               border border-graphite bg-transparent text-ghost">
  <!-- GSAP fill-up wipe on hover: accent bg slides up, text turns white -->
</button>
```

### Muted / Disabled pill

```html
<span class="rounded-full border border-graphite/40 bg-graphite/20 px-3 py-1.5
             font-mono text-[10px] text-ghost/30 uppercase tracking-widest
             cursor-not-allowed">
  Demo Coming Soon
</span>
```

### Active pill (with pulse dot)

```html
<a class="flex items-center gap-2 rounded-full border border-accent/40
          bg-accent/10 px-3 py-1.5 font-mono text-[10px] text-accent
          uppercase tracking-widest hover:bg-accent/20 transition-colors">
  <span class="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
  View Demo
</a>
```

---

## Navigation

```html
<!-- Wrapper: fixed, top-6, full-width, high z-index -->
<nav class="fixed top-6 left-0 right-0 z-50 px-6 sm:px-12">

  <!-- Inner pill -->
  <div class="mx-auto flex max-w-6xl items-center justify-between
              rounded-full border border-graphite/60 bg-background/80
              px-5 py-3 backdrop-blur-md">

    <!-- Brand mark -->
    <span class="font-sans font-bold tracking-widest text-ghost">
      EXOD<span class="text-accent">IA</span>
      <span class="text-ghost/40 font-light tracking-wide"> Technologies</span>
    </span>

    <!-- Nav links: font-mono text-xs uppercase tracking-widest text-ghost/50 hover:text-ghost -->

    <!-- CTA: Button variant="primary" -->
  </div>
</nav>
```

---

## Section Headers

Standard pattern used across all sections:

```html
<div>
  <h2 class="font-serif italic text-4xl sm:text-5xl md:text-6xl
             text-ghost leading-none mb-4 tracking-tight">
    Section <span class="text-accent underline decoration-1 underline-offset-4">Keyword</span>.
  </h2>
  <p class="font-mono text-sm text-ghost/60">
    One-line descriptor in mono.
  </p>
</div>
```

---

## Horizontal Carousels

Used for Team, Enterprise Deployments, and other card lists:

```tsx
const CARD_WIDTH = 300;
const CARD_GAP = 20;
const SCROLL_AMOUNT = CARD_WIDTH + CARD_GAP;

// Arrow buttons
<button
  onClick={() => el.scrollBy({ left: SCROLL_AMOUNT, behavior: 'smooth' })}
  disabled={!canScrollRight}
  class="flex h-11 w-11 items-center justify-center rounded-full
         border border-graphite bg-[#05050A] text-ghost/50
         transition-all duration-200
         hover:border-accent/40 hover:text-ghost
         disabled:opacity-20 disabled:cursor-not-allowed"
>
  <ChevronRight class="w-5 h-5" />
</button>

// Scroll track
<div
  class="flex gap-5 overflow-x-auto scroll-smooth
         px-6 sm:px-12 md:px-24 pb-4"
  style="scrollbar-width: none; -ms-overflow-style: none;"
>
```

---

## Infinite Marquee (Logos Strip)

```css
@keyframes logos-scroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
```

```html
<!-- Duplicate the logo array once for seamless loop -->
<div style="animation: logos-scroll 28s linear infinite; width: max-content;"
     class="flex items-center gap-16">
  <!-- Logo tiles (rendered twice) -->
</div>

<!-- Edge fade masks -->
<div class="pointer-events-none absolute inset-y-0 left-0 z-10 w-24
            bg-gradient-to-r from-[#04040A] to-transparent" />
<div class="pointer-events-none absolute inset-y-0 right-0 z-10 w-24
            bg-gradient-to-l from-[#04040A] to-transparent" />
```

Logo tile:
```html
<a class="flex shrink-0 items-center justify-center rounded-xl
          border border-graphite/50 bg-[#07070F] px-7 py-3
          opacity-40 grayscale transition-all duration-300
          hover:opacity-80 hover:grayscale-0 hover:border-accent/30"
   style="min-width: 140px; height: 52px;">
  <img style="filter: brightness(0) invert(1);" class="h-6 w-auto object-contain" />
</a>
```

---

## Avatar / Initials

Used in the Core Members carousel:

```html
<div class="relative flex h-24 w-24 items-center justify-center
            rounded-full border-2 border-graphite
            group-hover:border-accent/40 transition-colors duration-300
            overflow-hidden"
     style="background-color: #0d1117;">

  <!-- Inner radial gradient -->
  <div class="absolute inset-0 rounded-full bg-gradient-to-br from-accent/10 to-transparent" />

  <span class="relative font-serif italic text-2xl font-semibold text-accent/80 select-none">
    MG
  </span>
</div>
```

---

## Tags / Credential Pills

```html
<span class="rounded-full border border-accent/20 bg-accent/5
             px-2 py-0.5 font-mono text-[9px] text-accent/60
             uppercase tracking-widest">
  MSc Engineering
</span>
```

---

## Status Indicator

```html
<div class="rounded-full border border-graphite bg-background/50 px-3 py-1
            flex items-center gap-2">
  <div class="h-2 w-2 rounded-full bg-green-500
              shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
  <span class="font-mono text-base text-green-500 uppercase tracking-wider">
    System Operational
  </span>
</div>
```

---

## Noise Overlay

Applied on pages that need the film-grain texture:

```html
<div class="pointer-events-none fixed inset-0 z-[100] opacity-5 mix-blend-overlay">
  <svg class="absolute left-0 top-0 h-full w-full">
    <filter id="noiseFilter">
      <feTurbulence type="fractalNoise" baseFrequency="0.65"
                    numOctaves="3" stitchTiles="stitch" />
    </filter>
    <rect width="100%" height="100%" filter="url(#noiseFilter)" />
  </svg>
</div>
```

---

## Animations (GSAP)

### Page entrance (staggered reveal)

```ts
gsap.from('.reveal-text', {
  y: 40,
  opacity: 0,
  duration: 1.2,
  stagger: 0.15,
  ease: 'power3.out',
  delay: 0.5,
});
```

### Scroll-triggered reveal

```ts
gsap.from(el, {
  scrollTrigger: { trigger: el, start: 'top 85%' },
  y: 40,
  opacity: 0,
  duration: 1,
  ease: 'power3.out',
});
```

### Navbar entrance (safe — use `fromTo` + `clearProps`)

```ts
gsap.fromTo(navRef.current,
  { y: -40, opacity: 0 },
  { y: 0, opacity: 1, duration: 1, ease: 'power3.out', delay: 0.2,
    clearProps: 'transform,opacity' }
);
```

### Protocol/ScrollTrigger resize fix

```ts
useEffect(() => {
  let timeout: ReturnType<typeof setTimeout>;
  const handleResize = () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => ScrollTrigger.refresh(true), 200);
  };
  window.addEventListener('resize', handleResize);
  return () => { window.removeEventListener('resize', handleResize); clearTimeout(timeout); };
}, []);
```

---

## Footer Pattern

```
Border: border-t border-graphite
Background: bg-[#020205]
Shape: rounded-t-[4rem] on the footer element
Top accent line: h-px gradient via-accent with glow shadow
Brand mark: EXOD<accent>IA</accent> Technologies
Copyright: font-mono text-base text-ghost/40
```

---

## Tailwind Config (copy into new projects)

```js
// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0A0A14',
        accent:     '#4DA6FF',
        ghost:      '#F0EFF4',
        graphite:   '#18181B',
      },
      fontFamily: {
        sans:  ['Sora', 'sans-serif'],
        serif: ['"Instrument Serif"', 'serif'],
        mono:  ['"Fira Code"', 'monospace'],
      },
    },
  },
  plugins: [],
};
```

```css
/* index.css — paste at top */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=Sora:wght@100;200;300;400;500;600;700;800&display=swap');
```

---

## Logo Treatment on Dark Backgrounds

External logos that are dark or colored:

```css
filter: brightness(0) invert(1);   /* turns any logo white */
```

Apply via inline style per logo. Hover with `grayscale-0` to restore original color if preferred.

---

## Do / Don't

| Do | Don't |
|---|---|
| Use `font-mono` for all labels, tags, nav items | Mix fonts arbitrarily |
| Keep accent (`#4DA6FF`) as the sole highlight color | Add secondary accent colors |
| Use `opacity-*` variants of `ghost` for hierarchy | Use different text colors for hierarchy |
| Animate with GSAP (`power3.out`, `power2.inOut`) | Use CSS `transition` for entrance animations |
| `rounded-[2rem]` for content cards | Use `rounded-lg` / `rounded-2xl` on cards |
| Serif italic for headlines and pull quotes | Use serif for body copy |
| Single word underline in section headings | Underline full heading strings |
