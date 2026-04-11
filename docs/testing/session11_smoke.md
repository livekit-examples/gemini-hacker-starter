# Session 11 — Language Selector & RTL Smoke Test Checklist

Manual smoke tests to perform after automated tests pass.
Run against a live `docker compose up` instance.

---

## Prerequisites

- `docker compose up` is running
- Browser open at `http://localhost:3000`

---

## 1. English — Sales Demo

- [ ] Navigate to the landing page `/`
- [ ] Locate the **Sales Strategy** demo card
- [ ] Confirm the language selector shows `🇬🇧 English` as the default
- [ ] Click **View Demo** — confirm it navigates to `/demo/sales?lang=en`
- [ ] On the dashboard, confirm the language selector shows `🇬🇧 English` selected
- [ ] Confirm `dir` attribute on dashboard is `ltr` (no RTL text alignment)
- [ ] Connect to the agent — confirm the greeting is in English
- [ ] Verify transcript text is left-aligned

---

## 2. Italian — Sales Demo

- [ ] On the landing page, select `🇮🇹 Italiano` from the Sales card language selector
- [ ] Click **View Demo** — confirm it navigates to `/demo/sales?lang=it`
- [ ] On the dashboard, confirm `🇮🇹 Italiano` is selected in the language selector
- [ ] Confirm `dir` attribute on dashboard is `ltr`
- [ ] Connect — confirm the agent's first response is in formal Italian (uses *Lei* form)
- [ ] Verify transcript text is left-aligned

---

## 3. Arabic (Egyptian) — Sales Demo

- [ ] On the landing page, select `🇪🇬 Arabic (Egyptian)` from the Sales card language selector
- [ ] Click **View Demo** — confirm it navigates to `/demo/sales?lang=ar-EG`
- [ ] On the dashboard, confirm `🇪🇬 Arabic (Egyptian)` is selected
- [ ] Confirm `dir="rtl"` is applied to the dashboard container (inspect element or visual check)
- [ ] Confirm transcript entries are right-aligned
- [ ] Connect — confirm the agent greets in Egyptian Arabic dialect (uses كده / عايز expressions)
- [ ] Change language selector mid-session to `🇬🇧 English` — confirm RTL switches to LTR without reconnecting

---

## 4. Arabic (Emirati) — Sales Demo

- [ ] On the landing page, select `🇦🇪 Arabic (Emirati)` from the Sales card language selector
- [ ] Click **View Demo** — confirm it navigates to `/demo/sales?lang=ar-AE`
- [ ] On the dashboard, confirm `🇦🇪 Arabic (Emirati)` is selected
- [ ] Confirm `dir="rtl"` is applied — layout mirrors correctly (right panel on left side visually)
- [ ] Connect — confirm the agent greets in Gulf formal Arabic (uses حضرتك / تفضل)
- [ ] Verify PersonaCard language badge shows flag + code correctly

---

## 5. Language Selector on Dashboard (mid-session switch)

- [ ] Start any demo in English
- [ ] Change the language selector to `🇪🇬 Arabic (Egyptian)` mid-session
- [ ] Confirm the dashboard layout immediately switches to RTL (`dir="rtl"` without page reload)
- [ ] Confirm the PersonaCard badge updates to show the Egyptian flag
- [ ] Switch back to English — confirm LTR layout restores immediately

---

## 6. Four-Language Coverage on All Cards

- [ ] On the landing page, verify all 5 demo cards show a language selector
- [ ] Each selector should have exactly 4 options: `🇬🇧 English`, `🇮🇹 Italiano`, `🇪🇬 Arabic (Egyptian)`, `🇦🇪 Arabic (Emirati)`
- [ ] "Coming Soon" cards still show the language selector but the CTA is disabled

---

## Sign-off

| Tester | Date | Pass/Fail | Notes |
|--------|------|-----------|-------|
|        |      |           |       |
