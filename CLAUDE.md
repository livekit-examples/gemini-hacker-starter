# Exodia — Multimodal AI Demo Platform

## Vision

Transform this hackathon starter into the most compelling AI agent demo platform for medium-sized companies. Target verticals: **Sales, Manufacturing, Supply Chain & Logistics, Real Estate, Dental**. Every demo must look and feel like a shipping product, not a prototype.

**Supported languages:** English, Italian, Arabic (Egyptian dialect), Arabic (Emirati dialect)

> **Product positioning:** This application is **EXODIA Voice Intelligence** — a multimodal AI voice demo sub-product within the EXODIA Technologies family. It is **not** the main EXODIA Technologies marketing or corporate site. The nav brand mark, landing page hero, footer, and all user-facing copy must identify this as *Voice Intelligence*, not just "Technologies". Think of it as: `EXODIA Technologies > Voice Intelligence` — a distinct product with its own landing page, persona cards, and demo dashboards.

---

## Architecture Target

```
┌─────────────────────────────────────────────────────────────────┐
│  Next.js Frontend (EXODIA design system — zero LiveKit branding) │
│  ├── Landing page / demo selector                                │
│  ├── Dashboard layout (transcript · tool output · status panel) │
│  └── Industry demo pages                                        │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend  ← single deployable unit                      │
│  ├── /api/connection-details   (LiveKit token vending)          │
│  ├── /api/config               (per-industry app config)        │
│  ├── /api/demos                (available demo manifest)        │
│  ├── /api/health                                                │
│  └── AgentServer (livekit-agents) runs inside same process      │
│       managed as an asyncio background task                     │
├─────────────────────────────────────────────────────────────────┤
│  Agent Class Hierarchy (Python, inside backend/)                │
│  BaseAgent                                                      │
│  └── PersonaAgent  (language · tool registry · turn handling)  │
│      ├── ComuneAgent          ← PRIORITY first                 │
│      ├── SalesAgent                                             │
│      ├── ManufacturingAgent                                     │
│      ├── LogisticsAgent                                         │
│      ├── RealEstateAgent                                        │
│      └── DentalAgent                                           │
├─────────────────────────────────────────────────────────────────┤
│  LiveKit Cloud (SFU / room management — infrastructure only)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure Target

```
backend/
  app/
    main.py                   # FastAPI app + lifespan that boots AgentServer
    agent_runner.py           # starts livekit AgentServer as asyncio background task
    routers/
      connection.py
      config.py
      demos.py
      health.py
    agents/
      base.py                 # BaseAgent — core LiveKit wiring
      persona.py              # PersonaAgent — language detection, tool registry
      comune.py               # ComuneAgent — public administration (PRIORITY)
      sales.py
      manufacturing.py
      logistics.py
      real_estate.py
      dental.py
      registry.py             # maps industry slug → agent class
    languages/
      profiles.py             # LanguageProfile dataclass + 4 profiles
      detector.py             # language detection from participant metadata
    tools/
      comune_tools.py         # PRIORITY
      sales_tools.py
      manufacturing_tools.py
      logistics_tools.py
      real_estate_tools.py
      dental_tools.py
    data/
      comune_services.json
      comune_applications.json
      manufacturing_sop.json
      logistics_shipments.json
      logistics_carriers.json
      real_estate_listings.json
      real_estate_market.json
      dental_patients.json
      dental_procedures.json
    models.py                 # all Pydantic models
    demo_configs.py           # DemoConfig objects for all 5 industries
    config.py                 # settings via pydantic-settings
  tests/
    ...
  Dockerfile
  pyproject.toml
frontend/
  app/
    layout.tsx                # noise overlay, font imports, EXODIA theme
    page.tsx                  # landing / demo selector
    demo/[industry]/page.tsx  # per-industry dashboard
  components/
    design-system/            # all atoms: Button, Card, Tag, StatusDot, Avatar
    nav/                      # ExodiaNav
    dashboard/
      DashboardLayout.tsx
      TranscriptPanel.tsx
      ToolOutputPanel.tsx
      SessionControls.tsx
      PersonaCard.tsx
    landing/
      IndustryGrid.tsx
      DemoCard.tsx
  styles/
    globals.css               # EXODIA tokens, font import, noise keyframes
  tailwind.config.ts
docker-compose.yml            # backend + frontend only (agent runs inside backend)
```

---

## Agent Class Hierarchy

### `BaseAgent` — `backend/app/agents/base.py`
Wraps `livekit.agents.Agent`. Holds room + session. Provides track subscription lifecycle hooks. No persona, no tools, no language.

### `PersonaAgent(BaseAgent)` — `backend/app/agents/persona.py`
Adds `language_profile`, `persona_name`, `persona_instructions`. Manages tool registry via `register_tool(fn)`. Reads participant metadata on session start. Builds full system prompt. Exposes `switch_language(code)`.

### Industry agents
Each inherits `PersonaAgent`. `__init__` sets persona fields and calls `register_tool` for each tool. Tool implementations live in `backend/app/tools/`. Agents can override `on_session_start` for demo-specific setup.

### `AgentRegistry` — `backend/app/agents/registry.py`
`REGISTRY: dict[str, type[PersonaAgent]]` → used by `agent_runner.py` to dispatch sessions by industry.

---

## Dashboard Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  ExodiaNav (pill nav, fixed top-6)                               │
├──────────────────┬───────────────────────────┬───────────────────┤
│  Left (280px)    │  Center (flex-1)          │  Right (320px)    │
│                  │                           │                   │
│  PersonaCard     │  Camera / screen preview  │  ToolOutputPanel  │
│  ─────────────   │  or avatar when no video  │  (structured      │
│  Language select │                           │   tool outputs)   │
│  Session status  │  Voice activity indicator │  ─────────────── │
│  Demo reset      │  TranscriptPanel (live)   │  SessionControls  │
└──────────────────┴───────────────────────────┴───────────────────┘
```

---

## EXODIA Design System (applied from Session 5 onward)

Full reference: `style-guide.md`. Hard rules:

| Rule | Detail |
|---|---|
| Colors | `background: #0A0A14` · `accent: #4DA6FF` · `ghost: #F0EFF4` · `graphite: #18181B` |
| Fonts | Sora (body/UI) · Instrument Serif italic (headlines) · Fira Code (mono labels) |
| Cards | `rounded-[2rem]` · `border-graphite` · `bg-[#05050A]` · ambient glow on hover |
| Buttons | `rounded-full font-mono tracking-tight` — Primary / Outline / Muted pill |
| Animations | GSAP only for entrances — `power3.out`, `power2.inOut` |
| Text hierarchy | opacity variants of `ghost` only — never different text colors |
| Accent | `#4DA6FF` as the sole highlight — no secondary palette |
| Section headings | `font-serif italic` with single-word `text-accent underline` |
| Labels / tags | `font-mono uppercase tracking-widest` |

LiveKit brand artifacts to strip: `/lk-logo.svg`, `/lk-logo-dark.svg`, all `lk-*` CSS classes, `accent: '#1fd5f9'` (LiveKit cyan).

---

## Cross-Session Rules

1. Every `@function_tool` gets a unit test before the session closes.
2. All user-visible text comes from the config/API — never hardcoded in components.
3. Every demo works in all 4 languages before the session closes.
4. Seeded data uses realistic names, numbers, and industry terminology — no "Acme Corp".
5. `docker compose up` must work at the end of every session without exception.
6. One session = one PR with a passing CI check.
7. Zero LiveKit branding visible in the UI at any point after Session 6.
8. New personas are added by subclassing `PersonaAgent` + registering in `registry.py` only.

---

## Running Tests

```bash
# Backend
cd backend && uv run pytest tests/ -v

# Frontend
cd frontend && pnpm exec playwright test

# Via Docker
docker compose run --rm backend uv run pytest tests/ -v
```

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `LIVEKIT_URL` | backend | LiveKit WebSocket URL |
| `LIVEKIT_API_KEY` | backend | LiveKit API key |
| `LIVEKIT_API_SECRET` | backend | LiveKit API secret |
| `GOOGLE_API_KEY` | backend | Gemini API key |
| `REALTIME_MODEL` | backend | Gemini model ID (default: `gemini-2.5-flash-native-audio-latest`) |
| `REALTIME_VOICE` | backend | Default voice (default: `Aoede`) |
| `DEFAULT_LANGUAGE` | backend | Default language code (default: `en`) |
| `DEFAULT_INDUSTRY` | backend | Default demo industry (default: `sales`) |
| `NEXT_PUBLIC_BACKEND_URL` | frontend | FastAPI backend URL |

---

## Current State (Session 0 — baseline)

- `agent/agent.py` — single flat hackathon persona, no hierarchy, no tests
- `frontend/` — LiveKit Agents UI, LiveKit branding, LiveKit color tokens
- Connection details + health live in Next.js API routes
- Agent runs as a separate Docker service
- No tests anywhere

**Next action:** Start Session 1.

---

# Coding Sessions

Sessions are grouped into phases. Each session has a single focused scope, its own test suite, and a hard exit criterion. Tests must be green before the next session begins.

> **Priority directive (updated):** Frontend design and visual polish are the current top priority. After Session 2, work through **PHASE 2 — Design System (Sessions 5–9) first**, then return to PHASE 1 sessions 3–4. In PHASE 4, the **Public Administration (Comune) demo is the first industry to implement** (Sessions 12–13) — it is the highest-priority industry vertical. Sales follows immediately after (Sessions 14–15). The table and phase headings below reflect this revised execution order.

---

## PHASE 1 — Backend Foundation (Sessions 1–4)

---

### SESSION 1 — FastAPI Skeleton

**Status:** `[x] Complete`

**Goal:** A working FastAPI service with all four routes, Pydantic models, and environment config. The frontend can already point to it.

**Scope:**
- Create `backend/` directory with `pyproject.toml` (uv-managed, separate from `agent/`)
- `app/config.py` — `pydantic-settings` class reading all env vars with defaults and validation
- `app/models.py` — Pydantic response models: `HealthResponse`, `ConnectionDetailsResponse`, `AppConfigResponse`, `DemoSummary`, `DemosResponse`
- `app/routers/health.py` — `GET /api/health` returns `{status: "ok", version: "0.1.0"}`
- `app/routers/connection.py` — `GET /api/connection-details` mints a LiveKit JWT using `livekit-server-sdk`, returns token + url
- `app/routers/config.py` — `GET /api/config` returns hardcoded `AppConfigResponse` (will be dynamic later)
- `app/routers/demos.py` — `GET /api/demos` returns stub list of 5 demo summaries (slugs + names only)
- `app/main.py` — FastAPI app, registers all routers, no agent yet
- `backend/Dockerfile` — uvicorn entrypoint
- `docker-compose.yml` — add `backend` service; keep existing `agent` and `frontend` services untouched for now
- Frontend: add `NEXT_PUBLIC_BACKEND_URL` env var; update connection-details fetch to call backend (one file change only)

**E2E Tests (`backend/tests/`):**
- `test_health.py` — GET /api/health → 200, body matches schema
- `test_connection.py` — GET /api/connection-details → 200, token is a valid JWT with expected LiveKit claims
- `test_config.py` — GET /api/config → 200, required fields present
- `test_demos.py` — GET /api/demos → 200, returns list of 5 items each with `slug` and `name`

**Exit Criterion:** `pytest backend/tests/ -v` green. `docker compose up` starts all 3 services. Frontend connects via the new backend token endpoint.

---

### SESSION 2 — Agent Encapsulation

**Status:** `[x] Complete`

**Goal:** The LiveKit agent runs inside the FastAPI process. The standalone `agent/` Docker service is retired.

**Scope:**
- `backend/app/agent_runner.py` — `async def start_agent_server()` creates an `AgentServer`, registers a dispatch handler pointing to the existing `HackathonAgent` (ported verbatim), starts it as `asyncio.create_task()`
- `backend/app/main.py` — add `@asynccontextmanager` lifespan that calls `start_agent_server()` on startup and cancels the task on shutdown
- Port `HackathonAgent` from `agent/agent.py` into `backend/app/agents/hackathon.py` — exact same behaviour, no refactor yet
- Add `livekit-agents[google,images,turn-detector]` and `google-genai` to `backend/pyproject.toml`
- Remove the `agent` service from `docker-compose.yml`
- Verify the agent still connects to LiveKit and responds to voice after the migration

**E2E Tests (`backend/tests/`):**
- `test_agent_runner.py` — `start_agent_server()` returns a running task without raising; task is not done immediately after creation
- `test_agent_startup.py` — FastAPI app starts with lifespan (use `TestClient` with `with` block); no exception during startup

**Exit Criterion:** `pytest backend/tests/ -v` green. `docker compose up` starts `backend` + `frontend` only. Agent responds to voice in the browser — identical behaviour to before.

---

### SESSION 3 — Agent Class Hierarchy

**Status:** `[x] Complete`

**Goal:** The class hierarchy skeleton is in place. `HackathonAgent` is migrated into it. Adding a new industry agent requires only subclassing + one registry line.

**Scope:**
- `backend/app/agents/base.py` — `BaseAgent(livekit.agents.Agent)`:
  - `__init__(self, room)` — stores room, sets up track subscription handlers
  - `_on_track_subscribed`, `_on_track_unsubscribed` — moved from flat entrypoint into class
  - No persona, no tools, no language
- `backend/app/agents/persona.py` — `PersonaAgent(BaseAgent)`:
  - Fields: `persona_name: str`, `persona_instructions: str`, `language_profile: LanguageProfile | None`
  - `_tool_registry: list` — populated by `register_tool(fn)`
  - `build_system_prompt() -> str` — combines `BASE_VIDEO_AWARENESS + persona_instructions + (language_instructions if profile set)`
  - `switch_language(code: str)` — updates `language_profile`, rebuilds prompt
  - `__init__` calls `super().__init__` and calls `_register_tools()` (abstract hook for subclasses)
- `backend/app/agents/registry.py` — `REGISTRY: dict[str, type[PersonaAgent]]`; `get_agent(industry, room) -> PersonaAgent`; initially all 5 slugs map to a `DefaultAgent` placeholder
- `backend/app/agents/hackathon.py` — `HackathonAgent(PersonaAgent)`: migrated to use `register_tool`, `build_system_prompt`, sets its own `persona_name` and `persona_instructions`; registered in `REGISTRY` under key `"hackathon"`
- `agent_runner.py` dispatch handler updated to call `registry.get_agent(industry, room)` using `DEFAULT_INDUSTRY` env var

**E2E Tests (`backend/tests/`):**
- `test_agent_hierarchy.py`:
  - `PersonaAgent` is a subclass of `BaseAgent`
  - `HackathonAgent` is a subclass of `PersonaAgent`
  - `HackathonAgent` instantiates without error (mocked room)
  - `build_system_prompt()` returns a non-empty string containing persona instructions
  - `register_tool` adds to `_tool_registry`
- `test_agent_registry.py`:
  - Registry contains at least `"hackathon"` key
  - `get_agent("hackathon", mock_room)` returns a `HackathonAgent` instance
  - `get_agent("unknown", mock_room)` returns a `DefaultAgent` instance without raising

**Exit Criterion:** All tests green. `docker compose up` still works. Agent behaviour unchanged.

---

### SESSION 4 — Demo Config System

**Status:** `[ ] Not started`

**Goal:** The backend has a canonical `DemoConfig` per industry that is the single source of truth for all display data, persona metadata, and language support. `/api/config` and `/api/demos` return real structured data. The frontend is fully config-driven with no hardcoded display strings.

> **Note:** Session 8 added display fields (`persona_name`, `persona_initials`, `persona_role`, `value_prop`, `available`, `supported_languages`) to `DemoSummary` as a temporary stub. In this session those fields are removed from `DemoSummary` and moved into `DemoConfig`, which becomes the authoritative model. `DemoSummary` reverts to `slug` + `name` only (used for list indexing). The landing page and `FALLBACK_DEMOS` in `app/page.tsx` must be updated to fetch from the full `DemoConfig` endpoint.

**Scope:**
- `backend/app/demo_configs.py` — `DemoConfig` Pydantic model:
  - Identity: `slug`, `name`
  - Persona: `persona_name`, `persona_initials`, `persona_role`
  - Display: `value_prop`, `accent`, `available` (bool)
  - Languages: `supported_languages: list[str]` — all 4 codes for every industry
  - Dental only: `disclaimer: dict[str, str]` — keyed by language code
  - Define all 5 industry configs with real, specific copy (no lorem ipsum)
- `app/models.py` — `DemoSummary` reverts to `slug` + `name` only; add `DemoConfigResponse` wrapping `DemoConfig`
- `app/routers/config.py` — `GET /api/config?industry={slug}` returns full `DemoConfig`; 404 with descriptive message if unknown slug
- `app/routers/demos.py` — `GET /api/demos` returns list of `DemoConfig` objects (replaces the extended `DemoSummary` stubs added in Session 8)
- `frontend/app/page.tsx` — remove `FALLBACK_DEMOS` inline stubs; fetch full `DemoConfig` list from `/api/demos`; `DemoCardData` interface maps to `DemoConfig` fields
- No hardcoded display strings anywhere in frontend components

**E2E Tests (`backend/tests/`):**
- `test_demo_configs.py`:
  - All 5 slugs (`sales`, `manufacturing`, `logistics`, `real_estate`, `dental`) present
  - Each config has non-empty `persona_name`, `persona_initials`, `persona_role`, `value_prop`, `accent`
  - `supported_languages` contains all 4 language codes for every industry
  - `available` is a bool for all entries
- `test_config_endpoint.py`:
  - `GET /api/config?industry=sales` returns sales config with all required fields
  - `GET /api/config?industry=unknown` returns 404 with descriptive message
- `test_demos_endpoint.py`:
  - Returns exactly 5 items
  - Each item matches full `DemoConfig` schema (not just slug + name)
  - `persona_initials` is 2–3 uppercase characters for all entries

**Exit Criterion:** All tests green. `GET /api/demos` returns full `DemoConfig` for each industry. Frontend landing page reads all display data from backend with no hardcoded fallbacks.

---

## PHASE 2 — Design System (Sessions 5–9)

---

### SESSION 5 — Strip LiveKit Branding + Tailwind Setup

**Status:** `[x] Complete`

**Goal:** Zero LiveKit branding in the frontend. EXODIA color and font tokens installed and working.

**Scope:**
- Delete `/public/lk-logo.svg`, `/public/lk-logo-dark.svg`
- Remove all `lk-*` CSS class references from components
- Remove LiveKit color tokens (`#1fd5f9`, `#4285f4`) from Tailwind config and globals
- `tailwind.config.ts` — install EXODIA tokens: `background: '#0A0A14'`, `accent: '#4DA6FF'`, `ghost: '#F0EFF4'`, `graphite: '#18181B'`; font families: Sora (`sans`), Instrument Serif (`serif`), Fira Code (`mono`)
- `styles/globals.css` — Google Fonts import (Sora, Instrument Serif, Fira Code); `body { background-color: #0A0A14; color: #F0EFF4; font-family: Sora }`
- Noise overlay component (`components/design-system/NoiseOverlay.tsx`) — SVG fractalNoise, `opacity-5 mix-blend-overlay fixed inset-0 pointer-events-none z-[100]`
- Add `NoiseOverlay` to root `layout.tsx`
- Verify app still loads and existing LiveKit UI components render (they will look unstyled — that is expected and acceptable at this stage)

**E2E Tests:**
- `pytest backend/tests/` — no backend changes, all existing tests still green (regression check)
- Playwright `test_branding.spec.ts`:
  - No `<img>` with `src` containing `lk-logo` in the DOM
  - `document.body` computed background color is `rgb(10, 10, 20)` (`#0A0A14`)
  - At least one element uses `font-family: Sora`

**Exit Criterion:** All tests green. No LiveKit logos visible. App loads with correct background color and fonts.

---

### SESSION 6 — Design System Atoms

**Status:** `[x] Complete`

**Goal:** All reusable UI primitives exist and match the style guide exactly. Every other session uses these — nothing is rebuilt from scratch.

**Scope (all in `components/design-system/`):**
- `Button.tsx` — three variants: `primary` (bg-accent, white text), `outline` (border-graphite, ghost text), `muted` (disabled pill with `cursor-not-allowed`); all `rounded-full font-mono tracking-tight`
- `Card.tsx` — `rounded-[2rem] border border-graphite bg-[#05050A] p-7` with ambient corner glow `group-hover:opacity-10` (using `group` + absolute div)
- `Tag.tsx` — `rounded-full border border-accent/20 bg-accent/5 px-2 py-0.5 font-mono text-[9px] text-accent/60 uppercase tracking-widest`
- `ActivePill.tsx` — `flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-3 py-1.5 font-mono text-[10px] text-accent uppercase tracking-widest` with animated dot
- `StatusDot.tsx` — props: `state: 'connected' | 'connecting' | 'idle'`; green pulse / amber pulse / grey accordingly
- `Avatar.tsx` — initials avatar: `rounded-full border-2 border-graphite`, inner radial gradient, `font-serif italic text-2xl text-accent/80`
- `SectionHeader.tsx` — `font-serif italic text-4xl–6xl text-ghost`, accepts `keyword` prop for the single accented underlined word
- Storybook or simple `components/design-system/index.ts` barrel export

**E2E Tests:**
- Playwright `test_design_system.spec.ts`:
  - `Button` primary renders with background color `#4DA6FF`
  - `Button` muted has `cursor-not-allowed`
  - `Card` has `border-radius` ≥ `32px`
  - `StatusDot` with `state="connected"` contains a green element
  - `Avatar` with initials `"AR"` renders those characters

**Exit Criterion:** All tests green. All 7 atoms render correctly in isolation. Barrel export works.

---

### SESSION 7 — ExodiaNav + Root Layout

**Status:** `[x] Complete`

**Goal:** The navigation pill and root layout are production-ready and match the style guide.

**Scope:**
- `components/nav/ExodiaNav.tsx`:
  - Fixed `top-6`, pill container: `rounded-full border border-graphite/60 bg-background/80 backdrop-blur-md`
  - Brand mark: `EXOD<span class="text-accent">IA</span> <span class="text-ghost/40">Technologies</span>` in `font-sans font-bold tracking-widest`
  - Nav links: `font-mono text-xs uppercase tracking-widest text-ghost/50 hover:text-ghost`
  - CTA: `Button` primary variant
  - GSAP entrance: `fromTo` with `clearProps` per style guide
- `app/layout.tsx` — add `ExodiaNav`, `NoiseOverlay`, correct `<html lang>`, dark background class
- Footer component (`components/Footer.tsx`): `border-t border-graphite bg-[#020205] rounded-t-[4rem]`; brand mark; copyright in `font-mono text-base text-ghost/40`
- Remove the existing LiveKit default header/footer if present

**E2E Tests:**
- Playwright `test_nav.spec.ts`:
  - Nav element is `position: fixed`
  - Brand mark text contains "EXODIA"
  - Nav background contains `backdrop-filter: blur`
  - GSAP entrance completes (nav visible after 1.5s)

**Exit Criterion:** All tests green. Nav renders correctly on all pages. Footer renders. No console errors on load.

---

### SESSION 8 — Landing Page

**Status:** `[x] Complete`

**Goal:** A polished **EXODIA Voice Intelligence** landing page with GSAP-animated hero and all 5 industry demo cards wired to the backend. This is the sub-product landing page, not a generic EXODIA Technologies corporate page — copy and positioning must reflect "Voice Intelligence" throughout.

**Scope:**
- `app/page.tsx` — replaces the old voice-chat entry screen; fetches `/api/demos` on SSR; falls back to static stubs if backend is unavailable
- `ExodiaNav` brand mark updated to read `EXODIA Voice Intelligence` (was "Technologies")
- `Footer` brand mark updated to match
- Hero section:
  - `font-serif italic text-[clamp(2rem,8.2vw,8rem)] text-ghost leading-none` headline: "Voice Intelligence"
  - Accent italic subline: "AI agents that see, hear, and act"
  - `font-mono text-sm text-ghost/60` descriptor line
  - GSAP staggered reveal via `HeroReveal` client component
- `components/landing/IndustryGrid.tsx` — responsive CSS grid, renders `DemoCard` for each demo
- `components/landing/DemoCard.tsx`:
  - Extends `Card` atom
  - `Avatar` (persona initials), persona name in `font-serif italic`, industry label as `Tag`
  - Value prop in `font-sans text-sm text-ghost/70`
  - Language support tags (4 `Tag` atoms)
  - `ActivePill` "View Demo" if `available: true`, `Button` muted "Coming Soon" if false
  - Links to `/demo/[slug]`
- GSAP scroll-triggered reveal on card grid
- No placeholder text — all content from `DemoConfig`

**E2E Tests:**
- Playwright `test_landing.spec.ts`:
  - Page title contains "Exodia" or "EXODIA"
  - Exactly 5 demo cards rendered
  - Each card has an avatar, a persona name, and at least one language tag
  - "View Demo" link on `available` cards; disabled element on unavailable cards
  - No element with text "lorem" or "placeholder" (case insensitive)

**Exit Criterion:** All tests green. Landing page shows all 5 industry cards with real content. GSAP animations run without console errors.

---

### SESSION 9 — Dashboard Layout + Core Panels

**Status:** `[x] Complete`

**Goal:** The three-panel dashboard shell exists and is wired to a live agent session. Transcript and tool output panels update in real time.

**Scope:**
- `components/dashboard/DashboardLayout.tsx` — three-column layout (280px | flex-1 | 320px); collapses to single column below `lg`
- `components/dashboard/PersonaCard.tsx` — `Avatar`, persona name (`font-serif italic`), role (`font-mono text-xs text-ghost/50`), `StatusDot` wired to connection state, language badge (`Tag`)
- `components/dashboard/TranscriptPanel.tsx` — scrolling list of `{speaker, text, timestamp}` entries; speaker label `font-mono text-[10px] text-accent uppercase tracking-widest`; auto-scrolls to bottom; fades in new entries
- `components/dashboard/ToolOutputPanel.tsx` — renders typed cards when LiveKit data messages arrive on topic `"tool-output"`; each card: type tag pill at top, content area, timestamp in `text-ghost/35`
- `components/dashboard/SessionControls.tsx` — Disconnect (`Button` outline), Reset (`Button` muted), language selector (`<select>` styled with `bg-[#05050A] border-graphite rounded-[2rem]`)
- Voice activity indicator — simple CSS animated ring in center panel; pulses when agent is speaking
- `app/demo/[industry]/page.tsx` — fetches config for `params.industry`; renders `DashboardLayout` with correct `PersonaCard` data; redirects to `/` if industry not found

**E2E Tests:**
- Playwright `test_dashboard.spec.ts`:
  - Navigate to `/demo/sales` → three panels rendered
  - `PersonaCard` shows "Aria" (sales persona name)
  - `SessionControls` contains disconnect and reset buttons
  - Simulate a tool-output data message → `ToolOutputPanel` renders a card
  - Language selector contains all 4 language options
- `test_transcript.spec.ts`:
  - Injecting a transcript entry via state update → entry appears in panel
  - Auto-scroll: after 10 entries, scroll position is at bottom

**Exit Criterion:** All tests green. `/demo/sales` loads with correct persona. Transcript and tool output panels respond to live data. Dashboard looks production-grade against the style guide checklist.

---

## PHASE 3 — Multilingual (Sessions 10–11)

---

### SESSION 10 — Language Profiles + Backend Detector

**Status:** `[ ] Not started`

**Goal:** All 4 language profiles are written and tested. The agent can detect and apply the correct one from participant metadata.

**Scope:**
- `backend/app/languages/profiles.py`:
  ```python
  @dataclass
  class LanguageProfile:
      code: str
      display_name: str
      flag: str               # emoji flag for UI
      system_instructions: str
      greeting_prompt: str
      is_rtl: bool
  ```
  Four fully written profiles:
  - `en` — neutral professional English, direct register
  - `it` — formal Italian (`Lei` form), business register, no tutoring
  - `ar-EG` — Egyptian Arabic, warm colloquial, dialect markers (كده، عايز، إيه)
  - `ar-AE` — Emirati Arabic, formal Gulf register (حضرتك، تفضل)
  Each `system_instructions` is at least 3 sentences of real guidance for the LLM
- `backend/app/languages/detector.py`:
  - `detect_language(metadata: dict | None, fallback: str) -> LanguageProfile`
  - Reads `metadata["preferredLanguage"]`; validates against known codes; returns fallback profile on unknown/missing
- `PersonaAgent.switch_language(code: str)` wired to `detector.py`; updates `self.language_profile`; rebuilds system prompt

**E2E Tests (`backend/tests/test_languages.py`):**
- All 4 profiles load without error
- `is_rtl` is `True` for `ar-EG` and `ar-AE`, `False` for `en` and `it`
- `system_instructions` non-empty and ≥ 50 characters for all 4
- `greeting_prompt` non-empty for all 4
- `detect_language({"preferredLanguage": "it"}, "en")` returns Italian profile
- `detect_language({"preferredLanguage": "xx-UNKNOWN"}, "en")` returns English profile
- `detect_language(None, "en")` returns English profile

**Exit Criterion:** All tests green. No backend changes break existing sessions' tests.

---

### SESSION 11 — Language Selector + RTL Frontend

**Status:** `[ ] Not started`

**Goal:** The user can select a language before connecting. Arabic demos render RTL correctly.

**Scope:**
- `SessionControls.tsx` language selector: populated from `DemoConfig.supported_languages`; flag emoji + display name per profile; writes `preferredLanguage` to LiveKit participant metadata pre-connect
- Backend `/api/config` response includes full `supported_languages` list with `code`, `display_name`, `flag`, `is_rtl`
- `DashboardLayout.tsx`: applies `dir="rtl"` and `text-right` adjustments when `is_rtl` is true
- `TranscriptPanel.tsx`: RTL text alignment for Arabic entries (detect per-message or per-session)
- Language selector in `DemoCard` on the landing page (pre-connect selection persists to dashboard)
- Manual smoke test checklist created at `docs/testing/session11_smoke.md`: one greeting in each of the 4 languages, RTL layout check for both Arabic variants

**E2E Tests:**
- Playwright `test_language_selector.spec.ts`:
  - Language selector renders 4 options on `/demo/sales`
  - Selecting "Arabic (Egyptian)" sets `dir="rtl"` on the dashboard container
  - Flag emoji appears next to each option
- `pytest backend/tests/test_config_languages.py`:
  - `/api/config?industry=dental` returns all 4 language objects with `is_rtl` field

**Exit Criterion:** All tests green. RTL layout correct for both Arabic variants (visual check). Smoke checklist signed off.

---

## PHASE 4 — Industry Demos (Sessions 12–23)

Each industry is two sessions: **backend** (agent + tools + data) then **frontend** (panel wiring + persona card). **Public Administration (Comune) is first and highest priority.**

---

### SESSION 12 — Public Administration (Comune): Agent + Tools ⬅ PRIORITY

**Status:** `[ ] Not started`

**Persona:** Giulia, Municipal Services AI. Patient, precise, empathetic — bridges the gap between bureaucratic complexity and the citizen who just needs to get things done. Fluent in all 4 languages; especially important for Arabic-speaking immigrant communities navigating Italian municipal services.

**Scope:**
- `backend/app/agents/comune.py` — `ComuneAgent(PersonaAgent)`:
  - `persona_name = "Giulia"`, `persona_role = "Municipal Services AI"`
  - Full `persona_instructions` written (min 8 sentences): explains services clearly, never invents requirements, always cites the official document list, offers to book appointments at the end of every service query
  - Registers 3 tools on `__init__`
- `backend/app/tools/comune_tools.py`:
  - `lookup_service_requirements(service_name: str) -> dict` — `{service, required_documents: list[str], processing_days: int, fee_eur: float, office: str, notes: str, found: bool}`; matches by keyword against seeded data
  - `check_application_status(application_id: str) -> dict` — `{application_id, service, status: "pending"|"approved"|"rejected"|"requires_documents", submitted_on, expected_by, notes, found: bool}`
  - `book_appointment(service: str, citizen_name: str, preferred_date: str) -> dict` — `{confirmation_id, service, date, time, office, instructions, found: bool}` — returns `found: false` if service not bookable online
- `backend/app/data/comune_services.json` — 15 municipal services with realistic Italian bureaucratic requirements:
  - Anagrafe: birth certificate, marriage certificate, death certificate, residency registration, residency change
  - Civil state: name change, citizenship application
  - Permits: building permit, commercial activity permit, outdoor seating permit
  - Transport: parking permit (disabili), ZTL pass, vehicle scrappage declaration
  - Social: waste collection registration, ISEE declaration assistance
  - Each entry: `{service_id, name, keywords: list[str], required_documents: list[str], processing_days: int, fee_eur: float, office: str, bookable_online: bool, notes: str}`
- `backend/app/data/comune_applications.json` — 12 application records with realistic IDs (e.g. `APP-2024-ANA-00341`), statuses, and services
- `registry.py` — `"comune"` → `ComuneAgent`; add `"comune"` to the 5-industry list (now 6)

**E2E Tests (`backend/tests/test_comune_tools.py`):**
- `lookup_service_requirements("residenza")` returns `found: True`, non-empty `required_documents` list, numeric `processing_days`
- `lookup_service_requirements("xyznotexist")` returns `found: False`
- `check_application_status("APP-2024-ANA-00341")` returns valid dict with `status` one of 4 valid values
- `check_application_status("APP-FAKE-99999")` returns `found: False`
- `book_appointment("residency_registration", "Fatima Al-Rashidi", "2025-03-15")` returns `confirmation_id` and `date`
- `test_comune_data.py`: exactly 15 services, 12 applications; all have required fields; `bookable_online` is a bool for all services

**Exit Criterion:** All tests green. Service data reads as authentic Italian municipal content. Tools return correctly shaped outputs.

---

### SESSION 13 — Public Administration (Comune): Frontend Panel

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/ComunePanel.tsx`:
  - **Service requirements card:** service name header, `required_documents` as numbered checklist (each item in `font-sans text-sm`), processing time and fee in `font-mono` badges, office name as `Tag`
  - **Application status card:** application ID in `font-mono`, status badge (green approved / amber pending / red rejected / blue requires_docs), expected-by date, notes
  - **Appointment confirmation card:** confirmation ID in `font-mono`, date + time + office, instructions text
- `PersonaCard` for Giulia: initials `"GI"`, role tag `"Municipal Services AI"`
- `/demo/comune/page.tsx` — fetches config for `"comune"` industry; renders `DashboardLayout` with `ComunePanel` in right column
- Demo intro card (shown before connecting): value prop, 4 scripted scenario titles as `Tag` pills — e.g. "Residency Registration", "Permit Status", "Document Request", "Appointment Booking"
- `DemoCard` for Comune on landing page: `available: true` (it is the first fully-built demo)

**E2E Tests:**
- Playwright `test_comune_demo.spec.ts`:
  - `/demo/comune` loads without error
  - `PersonaCard` shows "Giulia"
  - Simulating a `tool-output` data message with type `"service_requirements"` → checklist renders
  - Simulating `tool-output` with type `"application_status"` → status badge renders with correct colour
  - Simulating `tool-output` with type `"appointment_confirmation"` → confirmation ID rendered in mono font

**Exit Criterion:** All tests green. Comune demo page is fully navigable. Persona card, all three panel cards, and the intro screen render correctly.

---

### SESSION 14 — Sales: Agent + Tools  <!-- was Session 12 -->

**Status:** `[ ] Not started`

**Persona:** Aria, Senior Sales Strategist. Confident, direct, commercially sharp.

**Scope:**
- `backend/app/agents/sales.py` — `SalesAgent(PersonaAgent)`:
  - `persona_name = "Aria"`, `persona_role = "Senior Sales Strategist"`
  - Full `persona_instructions` written (min 8 sentences covering tone, approach, when to push back)
  - Registers 3 tools on `__init__`
- `backend/app/tools/sales_tools.py`:
  - `analyze_screen_content(summary: str) -> dict` — returns `{findings: list[str], recommendations: list[str], priority: "high"|"medium"|"low"}`
  - `generate_proposal_section(section: str, context: str) -> str` — returns rewritten copy
  - `log_talking_points(points: list[str]) -> str` — publishes structured JSON to LiveKit data topic `"tool-output"` and returns confirmation
- `registry.py` — `"sales"` key updated from `DefaultAgent` to `SalesAgent`

**E2E Tests (`backend/tests/test_sales_tools.py`):**
- `analyze_screen_content("CRM showing 3 open opportunities")` returns dict with all 3 keys
- `priority` is one of `"high"`, `"medium"`, `"low"`
- `generate_proposal_section("executive_summary", "SMB logistics company")` returns non-empty string
- `log_talking_points(["Build rapport", "Ask about Q4 targets"])` returns string containing "sent" or "published"
- `test_agent_registry.py` — `get_agent("sales", mock_room)` returns `SalesAgent`

**Exit Criterion:** All tests green. `SalesAgent` instantiates. Tools return correctly shaped outputs.

---

### SESSION 15 — Sales: Frontend Panel  <!-- was Session 13 -->

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/SalesPanel.tsx` — renders talking points from `ToolOutputPanel` as a prioritised list; priority badge (red/amber/green `Tag`); bullet points in `font-sans text-sm text-ghost/70`
- `PersonaCard` for Aria: initials `"AR"`, role tag "Sales Strategist"
- `/demo/sales/page.tsx` — wires `SalesPanel` into right column of `DashboardLayout`
- Demo intro card (shown before connecting): 2-line value prop, 4 scripted demo scenario titles as `Tag` pills

**E2E Tests:**
- Playwright `test_sales_demo.spec.ts`:
  - `/demo/sales` loads without error
  - PersonaCard shows "Aria"
  - Simulating a `tool-output` data message with type `"talking_points"` → `SalesPanel` renders bullet list
  - Priority badge renders with correct color class

**Exit Criterion:** All tests green. Sales demo page is fully navigable. Tool output panel populates correctly.

---

### SESSION 16 — Manufacturing: Agent + Tools + SOP Data  <!-- was Session 14 -->

**Status:** `[ ] Not started`

**Persona:** Marco, Process & Quality Engineer. Methodical, precise, no-nonsense.

**Scope:**
- `backend/app/agents/manufacturing.py` — `ManufacturingAgent(PersonaAgent)`, registers 3 tools
- `backend/app/tools/manufacturing_tools.py`:
  - `detect_visual_defect(description: str) -> dict` — `{defect_type, severity: "critical"|"major"|"minor", area, recommended_action}`
  - `generate_defect_report(defects: list[dict]) -> str` — formatted report string pushed to `"tool-output"`
  - `lookup_sop(keyword: str) -> dict` — `{procedure_id, title, steps: list[str], found: bool}`
- `backend/app/data/manufacturing_sop.json` — 20 entries; each: `{procedure_id, title, keywords: list[str], steps: list[str]}`; topics: torque specs, lockout-tagout, inspection criteria, machine error codes, PPE requirements
- `registry.py` — `"manufacturing"` → `ManufacturingAgent`

**E2E Tests (`backend/tests/`):**
- `test_manufacturing_tools.py`:
  - `detect_visual_defect(...)` returns all 4 keys; severity is one of 3 valid values
  - `lookup_sop("torque")` returns `found: True` and non-empty `steps`
  - `lookup_sop("xyznotexist")` returns `found: False`
- `test_sop_data.py`:
  - Exactly 20 entries load from JSON
  - All entries have `procedure_id`, `title`, `keywords`, `steps`
  - `steps` is non-empty for all entries

**Exit Criterion:** All tests green. SOP has 20 real, realistic entries.

---

### SESSION 17 — Manufacturing: Frontend Panel  <!-- was Session 15 -->

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/ManufacturingPanel.tsx` — defect report card: defect type header, severity badge (colour-coded Tag), recommended action; SOP result card: procedure title, numbered steps list
- `PersonaCard` for Marco: initials `"MA"`, role tag "Process & Quality Engineer"
- `/demo/manufacturing/page.tsx`

**E2E Tests:**
- Playwright `test_manufacturing_demo.spec.ts`:
  - PersonaCard shows "Marco"
  - Simulating defect `tool-output` → panel renders severity badge
  - Simulating SOP `tool-output` → panel renders numbered steps

**Exit Criterion:** All tests green. Manufacturing dashboard is demo-ready.

---

### SESSION 18 — Logistics: Agent + Tools + Seeded Data  <!-- was Session 16 -->

**Status:** `[ ] Not started`

**Persona:** Elena, Head of Logistics Operations. Sharp, fast, operationally focused.

**Scope:**
- `backend/app/agents/logistics.py` — `LogisticsAgent(PersonaAgent)`, registers 3 tools
- `backend/app/tools/logistics_tools.py`:
  - `lookup_shipment(tracking_id: str) -> dict` — `{tracking_id, origin, destination, status, eta, carrier, delay_days}`; from seeded JSON; returns `{found: false}` on miss
  - `flag_delay(tracking_id: str, reason: str) -> str` — publishes delay flag to `"tool-output"`, returns confirmation
  - `generate_carrier_brief(carrier_name: str) -> dict` — `{carrier, on_time_rate_pct, avg_delay_days, open_incidents, recommendation}`
- `backend/app/data/logistics_shipments.json` — 15 shipments with realistic IDs (e.g. `SHP-20240312-AUH`), origins, destinations, statuses
- `backend/app/data/logistics_carriers.json` — 5 carriers with realistic performance metrics
- `registry.py` — `"logistics"` → `LogisticsAgent`

**E2E Tests:**
- `test_logistics_tools.py` — all tools return correctly shaped dicts; miss returns `found: false`
- `test_logistics_data.py` — 15 shipments, 5 carriers; all have required fields; no "Acme Corp"

**Exit Criterion:** All tests green. Seeded data looks real.

---

### SESSION 19 — Logistics: Frontend Panel  <!-- was Session 17 -->

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/LogisticsPanel.tsx` — shipment card: tracking ID in `font-mono`, status badge, ETA; delay flag card: warning icon, reason, timestamp; carrier brief card: on-time rate, incidents count
- `PersonaCard` for Elena: initials `"EL"`, role tag "Head of Logistics Operations"
- `/demo/logistics/page.tsx`

**E2E Tests:**
- Playwright `test_logistics_demo.spec.ts`:
  - PersonaCard shows "Elena"
  - Shipment lookup `tool-output` → tracking ID rendered in mono font
  - Delay flag `tool-output` → warning card renders

**Exit Criterion:** All tests green. Logistics dashboard is demo-ready.

---

### SESSION 20 — Real Estate: Agent + Tools + Seeded Data  <!-- was Session 18 -->

**Status:** `[ ] Not started`

**Persona:** Sofia, Senior Property Advisor. Elegant, knowledgeable, client-centric.

**Scope:**
- `backend/app/agents/real_estate.py` — `RealEstateAgent(PersonaAgent)`, registers 3 tools
- `backend/app/tools/real_estate_tools.py`:
  - `analyze_property_visual(description: str) -> dict` — `{observations: list[str], issues: list[{item, severity}], estimated_adjustment: str}`
  - `generate_cma(location: str, sqm: int, bedrooms: int) -> dict` — `{comparables: list[{address,price,sqm,sold_date}], price_range: str, recommendation: str}`; uses seeded listings
  - `summarize_buyer_profile(answers: dict) -> str` — formatted profile string
- `backend/app/data/real_estate_listings.json` — 10 listings; Gulf or Mediterranean market; realistic prices in AED or EUR
- `backend/app/data/real_estate_market.json` — price/sqm by neighbourhood (8 neighbourhoods)
- `registry.py` — `"real_estate"` → `RealEstateAgent`

**E2E Tests:**
- `test_real_estate_tools.py` — CMA returns ≥ 3 comparables; property analysis has all 3 keys
- `test_real_estate_data.py` — 10 listings, 8 neighbourhoods; all have required fields

**Exit Criterion:** All tests green. CMA returns real-looking data.

---

### SESSION 21 — Real Estate: Frontend Panel  <!-- was Session 19 -->

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/RealEstatePanel.tsx` — CMA card: comparables table (address, price, sqm, date), price range summary; property analysis card: observations list, issues with severity badges, adjustment estimate
- Buyer profile card: formatted profile text with section headers
- `PersonaCard` for Sofia: initials `"SO"`, role tag "Senior Property Advisor"
- `/demo/real_estate/page.tsx`

**E2E Tests:**
- Playwright `test_real_estate_demo.spec.ts`:
  - PersonaCard shows "Sofia"
  - CMA `tool-output` → comparables table renders with ≥ 3 rows
  - Property analysis `tool-output` → issues list renders

**Exit Criterion:** All tests green. Real estate dashboard demo-ready.

---

### SESSION 22 — Dental: Agent + Tools + Seeded Data  <!-- was Session 20 -->

**Status:** `[ ] Not started`

**Persona:** Dr. Nour, Specialist in Restorative Dentistry. Calm, reassuring, precise.

**Scope:**
- `backend/app/agents/dental.py` — `DentalAgent(PersonaAgent)`, registers 3 tools
- `backend/app/tools/dental_tools.py`:
  - `analyze_dental_image(description: str) -> dict` — `{area, observation, clinical_term, lay_term, urgency: "urgent"|"monitor"|"routine"}`
  - `generate_patient_instructions(procedure: str, language_code: str) -> str` — multilingual aftercare from seeded data; raises `ValueError` if procedure or language not found
  - `lookup_patient_brief(patient_id: str) -> dict` — seeded patient profile; returns `{found: false}` on miss
- `backend/app/data/dental_patients.json` — 8 patient profiles: `{patient_id, name, age, conditions: list, upcoming_procedure}`
- `backend/app/data/dental_procedures.json` — 12 procedures; each: `{procedure_id, name, aftercare: {en, it, "ar-EG", "ar-AE"}}`
- Compliance disclaimer per language stored in `DentalConfig` in `demo_configs.py` (not in components)
- `registry.py` — `"dental"` → `DentalAgent`

**E2E Tests:**
- `test_dental_tools.py`:
  - `analyze_dental_image(...)` returns all 4 keys; urgency is one of 3 valid values
  - `generate_patient_instructions("root_canal", "ar-EG")` returns Arabic text
  - `generate_patient_instructions("root_canal", "xx")` raises `ValueError`
  - `lookup_patient_brief("PAT-001")` returns valid dict
- `test_dental_data.py`:
  - 8 patients, 12 procedures
  - All 4 language keys (`en`, `it`, `ar-EG`, `ar-AE`) present on every procedure's aftercare
- `test_dental_disclaimer.py`:
  - `DentalConfig.disclaimer` dict has keys for all 4 language codes
  - Each disclaimer string is non-empty and ≥ 20 characters

**Exit Criterion:** All tests green. Aftercare exists in all 4 languages for all 12 procedures. Disclaimer in all 4 languages.

---

### SESSION 23 — Dental: Frontend Panel + Disclaimer  <!-- was Session 21 -->

**Status:** `[ ] Not started`

**Scope:**
- `components/dashboard/panels/DentalPanel.tsx`:
  - Image analysis card: area, clinical term in `font-mono`, lay term in `font-sans`, urgency badge (red/amber/green)
  - Patient brief card: name, age, conditions list, upcoming procedure
  - Aftercare instructions card: procedure name header, instructions text (RTL if Arabic)
- Compliance disclaimer banner: displayed before the connect button, uses the `DentalConfig.disclaimer[languageCode]` string; styled as `border border-accent/30 bg-accent/5 rounded-[2rem] p-5`; visible in all 4 languages when language is switched
- `PersonaCard` for Dr. Nour: initials `"DN"`, role tag "Specialist in Restorative Dentistry"
- `/demo/dental/page.tsx`

**E2E Tests:**
- Playwright `test_dental_demo.spec.ts`:
  - PersonaCard shows "Dr. Nour"
  - Disclaimer banner is visible before connecting
  - Switching to Italian → disclaimer text changes to Italian variant
  - Image analysis `tool-output` → urgency badge renders with correct colour
  - Aftercare `tool-output` → text renders RTL when Arabic language active

**Exit Criterion:** All tests green. Disclaimer visible in all 4 languages. Dental dashboard demo-ready.

---

## PHASE 5 — Polish + Production (Sessions 22–24)

---

### SESSION 24 — Demo Switching + Persona Transitions  <!-- was Session 22 -->

**Status:** `[ ] Not started`

**Goal:** Industry switching happens without a full page reload. Transition feels smooth and intentional.

**Scope:**
- `app/demo/[industry]/page.tsx` — on industry change: LiveKit disconnect → new room with new `agentName` from `DemoConfig` → reconnect
- Industry selector in nav: clicking a different industry triggers the transition, not a navigation
- Transition animation: panels fade out → `PersonaCard` swaps (GSAP `power2.inOut`) → panels fade in
- "Active" industry highlighted in `ExodiaNav` with `font-mono text-accent` + underline
- `SessionControls` reset button: disconnects, clears transcript + tool output, returns to landing page
- Backend: `GET /api/demos` already returns `available` field; frontend disables switching to unavailable demos

**E2E Tests:**
- Playwright `test_demo_switching.spec.ts`:
  - On `/demo/sales`, click Manufacturing nav link → dashboard updates to Marco persona without full reload (URL changes, no full page flash)
  - Transition completes in < 2 seconds
  - Reset button → redirects to `/`
  - Clicking a "Coming Soon" demo does nothing (no navigation)

**Exit Criterion:** All tests green. Persona switching measured under 2 seconds. No blank flash during transition.

---

### SESSION 25 — Landing Page Polish + GSAP + Carousel  <!-- was Session 23 -->

**Status:** `[ ] Not started`

**Goal:** The landing page is visually compelling enough to open a sales conversation. The industry grid has both a desktop grid view and a mobile-first horizontal scroll carousel.

**Scope:**
- Hero: staggered GSAP reveal on each line of the headline (`stagger: 0.15`, `power3.out`)
- GSAP `ScrollTrigger` reveal on `IndustryGrid` cards (stagger by index, `start: "top 85%"`)
- `SectionHeader` component with single-word accent underline used consistently
- **Scrolling carousel (`components/landing/CarouselGrid.tsx`):**
  - Horizontal snap-scroll carousel using CSS `scroll-snap-type: x mandatory` — no library dependency
  - Each card is `scroll-snap-align: start`; container has `overflow-x: auto; scrollbar-width: none`
  - Prev / Next arrow buttons (`Button` outline variant) appear on `md:` and above; hidden on mobile (swipe-native)
  - Dot indicators below the carousel; active dot uses `bg-accent`, inactive `bg-graphite`
  - `IndustryGrid` renders `CarouselGrid` below `md` breakpoint, CSS grid above — controlled by a `useCarousel` hook that reads `window.innerWidth` on mount
  - Edge fade masks: `mask-image: linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%)`
- Infinite marquee component (`components/landing/Marquee.tsx`) — tech/stack badges scrolling below hero; edge fade masks; `logos-scroll` CSS keyframe (no JS); content: LiveKit, Gemini, FastAPI, Next.js, Python, TypeScript labels as `Tag` pills
- `<meta>` tags: `og:title`, `og:description`, `og:image` (static 1200×630 placeholder)
- Font loading: `display=swap` already set; verify no FOUT on slow 3G (Lighthouse check)

**E2E Tests:**
- Playwright `test_landing_polish.spec.ts`:
  - All 5 cards reachable (visible or scrollable-into-view) on 1280px viewport
  - On 375px viewport: carousel container is present and has `overflow-x` scroll
  - Dot indicators count equals number of demo cards (5)
  - Prev/Next buttons absent on 375px (hidden via CSS)
  - `og:title` meta tag present and non-empty
  - GSAP animations complete without JS errors (check `page.on('pageerror')`)
  - Marquee element is visible and contains at least one `Tag`

**Exit Criterion:** All tests green. Landing page reviewed against style-guide checklist. Carousel works on mobile (manual swipe check). Grid layout intact on desktop.

---

### SESSION 26 — Production Hardening  <!-- was Session 24 -->

**Status:** `[ ] Not started`

**Goal:** Demo-safe. Won't crash, won't leak, won't embarrass in front of a customer.

**Scope:**
- Frontend error boundary: `components/ErrorBoundary.tsx` wraps dashboard; renders EXODIA-styled fallback card on agent disconnect or JS error
- Backend rate limiting: `slowapi` — 10 requests/minute/IP on `/api/connection-details`; returns 429 with `Retry-After` header
- All backend endpoints: Pydantic input validation; 422 with descriptive `detail` on bad input
- Secrets audit: `grep` for `GOOGLE_API_KEY`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` values in frontend bundle; assert none found
- Structured logging: `structlog` in backend with JSON output; no raw `print()` calls; no PII (email, name, tracking IDs) in log messages
- Docker health checks: all services
- Cold start benchmark: `docker compose up` → first agent voice response; target ≤ 60 seconds; measure and document in `docs/benchmarks.md`
- README rewrite: step-by-step demo run guide for all 5 industries, all 4 languages; includes quick-start and full Docker instructions

**E2E Tests:**
- `pytest backend/tests/test_rate_limiting.py` — 11th request in 60s window → 429 with `Retry-After`
- `pytest backend/tests/test_input_validation.py` — missing `industry` param on `/api/config` → 422; invalid JSON body → 422
- `pytest backend/tests/test_no_secrets_in_responses.py` — assert env var values absent from all API response bodies
- Playwright `test_error_boundary.spec.ts` — simulate JS error in dashboard → error boundary renders (not blank screen); error card styled with EXODIA tokens
- Locust load test script `backend/tests/locustfile.py` — 20 RPS for 30s on `/api/connection-details`; p99 < 500ms; run and document results

**Exit Criterion:** All tests green. Load test passes. Cold start ≤ 60s documented. Zero secret leaks. README reviewed for clarity.

---

## PHASE 6 — Mobile & Responsive Design (Session 25)

---

### SESSION 27 — Mobile Responsiveness Pass  <!-- was Session 25 -->

**Status:** `[ ] Not started`

**Goal:** Every page and panel in the app renders correctly and is fully usable on a 375px (iPhone SE) viewport. No horizontal overflow, no text clipping, no tap targets smaller than 44px.

**Scope:**

**Landing page (`app/page.tsx` + landing components):**
- Hero text scales correctly with `clamp()` down to 375px — verify no overflow
- `CarouselGrid` (from Session 23) is the default grid view on mobile — confirm snap behaviour
- `ExodiaNav` collapses to icon-only or hamburger below `md:`; brand mark truncates gracefully
- Hero CTA and `ActivePill` links have min tap target `h-11 w-full sm:w-auto`

**Dashboard (`app/demo/[industry]/page.tsx` + dashboard components):**
- `DashboardLayout` is single-column below `lg:` — left and right panels stack above and below the center
- `TranscriptPanel` max height `h-64` on mobile with internal scroll; expands on larger screens
- `ToolOutputPanel` collapses to an accordion or bottom-sheet drawer on mobile (toggle button in `SessionControls`)
- `SessionControls` stacks vertically on mobile; language selector full-width
- `PersonaCard` uses compact layout below `md:` (avatar left, name/role right, no status text label)
- All tap targets (buttons, links, select) meet 44×44px minimum

**Shared:**
- `globals.css` — add `@media (pointer: coarse)` scroll snap momentum fix for iOS (`-webkit-overflow-scrolling: touch`)
- No horizontal overflow on any page at 375px (use `max-w-full overflow-x-hidden` on `<body>`)
- `<meta name="viewport" content="width=device-width, initial-scale=1">` present in `layout.tsx`

**E2E Tests:**
- Playwright `test_mobile.spec.ts` (all at `{ viewport: { width: 375, height: 812 } }`):
  - Landing page: no horizontal scrollbar (`scrollWidth === clientWidth` on `<body>`)
  - Landing page: `CarouselGrid` container present and `overflow-x` is `auto` or `scroll`
  - Dashboard `/demo/sales`: panels stack vertically (left panel appears above center in DOM order)
  - Dashboard: all `<button>` elements have bounding box height ≥ 44px
  - Nav: brand mark visible and not clipped (bounding box width > 0)
- Lighthouse CI script `scripts/mobile-audit.sh`: run `lhci autorun` on `/` and `/demo/sales`; assert performance ≥ 75, accessibility ≥ 90 on mobile preset

**Exit Criterion:** All Playwright mobile tests green. No horizontal overflow on any page at 375px (visual and automated check). Lighthouse accessibility ≥ 90 on mobile. Dashboard usable on an actual phone (manual smoke test checklist at `docs/testing/session25_mobile_smoke.md`).

---

## Session Summary

> **Agent instruction:** After completing any session, update the status column below — change `[ ]` to `[x]` for that session. Before starting a new session, scan this table to confirm which sessions are already done so you never re-implement completed work.

| Order | # | Done | Session | Phase | Key Deliverable |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | [x] | FastAPI Skeleton | Foundation | 4 routes, Pydantic models, Docker |
| 2 | 2 | [x] | Agent Encapsulation | Foundation | Agent inside FastAPI, standalone service retired |
| **3** | **5** | **[x]** | **Strip LiveKit + Tailwind** | **Design** | **EXODIA tokens, fonts, no LiveKit brand** |
| **4** | **6** | **[x]** | **Design System Atoms** | **Design** | **Button, Card, Tag, StatusDot, Avatar, etc.** |
| **5** | **7** | **[x]** | **ExodiaNav + Root Layout** | **Design** | **Nav pill, footer, layout shell** |
| **6** | **8** | **[x]** | **Landing Page** | **Design** | **Hero + 6 DemoCards wired to backend** |
| **7** | **9** | **[x]** | **Dashboard Layout** | **Design** | **3-panel shell, Transcript, ToolOutput, Controls** |
| 8 | 3 | [x] | Agent Class Hierarchy | Foundation | BaseAgent → PersonaAgent → registry |
| 9 | 4 | [ ] | Demo Config System | Foundation | DemoConfig for all 6 industries, replaces Session 8 stubs |
| 10 | 10 | [ ] | Language Profiles | Multilingual | 4 profiles, detector, PersonaAgent integration |
| 11 | 11 | [ ] | Language Selector + RTL | Multilingual | Frontend selector, RTL layout, smoke tests |
| **12** | **12** | **[ ]** | **Comune: Backend ⬅ PRIORITY** | **Public Admin** | **ComuneAgent, 3 tools, 15 services, 12 applications** |
| **13** | **13** | **[ ]** | **Comune: Frontend** | **Public Admin** | **ComunePanel, Giulia PersonaCard** |
| 14 | 14 | [ ] | Sales: Backend | Sales | SalesAgent, 3 tools |
| 15 | 15 | [ ] | Sales: Frontend | Sales | SalesPanel, Aria PersonaCard |
| 16 | 16 | [ ] | Manufacturing: Backend | Manufacturing | ManufacturingAgent, SOP data (20 entries) |
| 17 | 17 | [ ] | Manufacturing: Frontend | Manufacturing | DefectPanel, Marco PersonaCard |
| 18 | 18 | [ ] | Logistics: Backend | Logistics | LogisticsAgent, 15 shipments, 5 carriers |
| 19 | 19 | [ ] | Logistics: Frontend | Logistics | LogisticsPanel, Elena PersonaCard |
| 20 | 20 | [ ] | Real Estate: Backend | Real Estate | RealEstateAgent, listings + market data |
| 21 | 21 | [ ] | Real Estate: Frontend | Real Estate | CMApanel, Sofia PersonaCard |
| 22 | 22 | [ ] | Dental: Backend | Dental | DentalAgent, multilingual aftercare, disclaimer |
| 23 | 23 | [ ] | Dental: Frontend | Dental | DentalPanel, disclaimer banner, Dr. Nour card |
| 24 | 24 | [ ] | Demo Switching | Polish | Persona transitions, nav active state |
| 25 | 25 | [ ] | Landing Polish + GSAP + Carousel | Polish | Animations, snap carousel, marquee, meta tags |
| 26 | 26 | [ ] | Production Hardening | Production | Rate limiting, secrets audit, load test |
| 27 | 27 | [ ] | Mobile Responsiveness | Mobile | 375px layouts, tap targets, Lighthouse ≥ 90 |
