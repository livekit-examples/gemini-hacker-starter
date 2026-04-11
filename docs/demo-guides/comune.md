# Demo Guide — Comune (Public Administration)

**Persona:** Giulia, Municipal Services AI  
**Agent slug:** `comune`  
**URL:** `/demo/comune`

Giulia helps citizens navigate Italian municipal bureaucracy: document requirements,
application status tracking, and appointment booking. The demo is strongest when the
presenter plays the role of a resident (or immigrant) who needs a real service and does
not know where to start.

---

## Before you connect

1. Open `/demo/comune` in the browser.
2. Select the language you want to present in (English recommended for international audiences; Arabic for the immigrant-community angle).
3. Click **Connect** — Giulia introduces herself within a few seconds.

---

## Scenario 1 — Residency Registration (new arrival)

**Best for:** Showing the immigrant-community use case. Giulia lists a non-EU document requirement (permesso di soggiorno) without prompting.

**What to say:**
> "I just moved to Milan from Egypt. I need to register my new address at the municipality. What documents do I need?"

**Tool triggered:** `lookup_service_requirements("residency registration")`

**Expected response highlights:**
- 5 required documents including *permesso di soggiorno in corso di validità* for non-EU citizens
- Processing time: **45 days** (police inspection required)
- Fee: **free**
- Office: *Ufficio Anagrafe — Sportello 2*
- Giulia should offer to book an appointment at the end

**Follow-up — book the appointment:**
> "Yes, please book an appointment for me. My name is Fatima Al-Rashidi. I'm free on 15 March."

**Tool triggered:** `book_appointment("residency_registration", "Fatima Al-Rashidi", "2025-03-15")`

**Expected response highlights:**
- Confirmation ID (e.g. `CONF-2025-ANA-XXXX`)
- Date, time, office, and instructions

---

## Scenario 2 — Check Application Status (pending)

**Best for:** Showing real-time status lookup. The application is awaiting a police inspection, so Giulia explains what happens next.

**What to say:**
> "I submitted a residency application a few weeks ago. Can you check the status? The reference number is APP-2024-ANA-00341."

**Tool triggered:** `check_application_status("APP-2024-ANA-00341")`

**Expected response highlights:**
- Status: **pending**
- Submitted: 3 November 2024
- Expected by: 18 December 2024
- Note: police inspection scheduled for the week of 9 December

---

## Scenario 3 — Check Application Status (requires documents)

**Best for:** Showing the "action required" case — Giulia explains what is missing and what to do next.

**What to say:**
> "I applied for a building permit back in September. My ID is APP-2024-PER-00078. Has there been any update?"

**Tool triggered:** `check_application_status("APP-2024-PER-00078")`

**Expected response highlights:**
- Status: **requires documents**
- Missing: updated project drawings signed by a licensed technician
- Deadline to submit: 20 December 2024
- Giulia should offer to explain the building permit requirements in detail

**Follow-up — pivot to service lookup:**
> "What documents are required for a building permit in general?"

**Tool triggered:** `lookup_service_requirements("building permit")`

**Expected response highlights:**
- 6 required documents (technical report, architectural drawings, etc.)
- Processing time: **75 days** (suspended if documentation is incomplete)
- Fee: **€350**
- Office: *Ufficio Urbanistica ed Edilizia Privata — Piano 2*
- Not bookable online — Giulia should note this

---

## Scenario 4 — Check Application Status (rejected)

**Best for:** Showing graceful handling of bad news. Giulia explains why it was rejected and what alternatives exist.

**What to say:**
> "I applied for outdoor seating for my restaurant. The application ID is APP-2024-PER-00031. What happened?"

**Tool triggered:** `check_application_status("APP-2024-PER-00031")`

**Expected response highlights:**
- Status: **rejected**
- Reason: requested area is classified as an emergency road
- Giulia explains that a new application for an adjacent area is possible
- Giulia should offer to look up the outdoor seating (dehors) requirements

---

## Scenario 5 — Citizenship Application (complex, long process)

**Best for:** Demonstrating that Giulia handles intimidating bureaucracy calmly and sets realistic expectations.

**What to say:**
> "I've been living in Italy for 12 years. I want to apply for Italian citizenship. What do I need?"

**Tool triggered:** `lookup_service_requirements("citizenship")`

**Expected response highlights:**
- 7 required documents (apostilled birth certificate, criminal record from country of origin, income documentation, €250 contribution receipt, etc.)
- Processing time: **730 days (2 years)**
- Fee: **€250**
- Office: *Prefettura — assisted by the Comune*
- Not bookable online — Giulia should explain the Comune assists with document collection

**Follow-up — book assistance appointment:**
> "Can I book an appointment with the Comune to get help gathering the documents?"

**Tool triggered:** `book_appointment("citizenship_application", ..., ...)`

**Expected response:** `found: false` — this service is not bookable online. Giulia should explain how to contact the office directly.

---

## Scenario 6 — ISEE Declaration Assistance (social services)

**Best for:** The social-services / low-income angle. Shows that Giulia understands free services and CAF assistance.

**What to say:**
> "I need to get my ISEE certificate to apply for reduced school fees for my children. Where do I start?"

**Tool triggered:** `lookup_service_requirements("ISEE")`

**Expected response highlights:**
- 6 required documents (ID for all family members, CU tax certificates, bank statement as of 31 December, etc.)
- Processing time: **5 days**
- Fee: **free**
- Office: *Ufficio Servizi Sociali — CAF convenzionato*
- Valid from 1 January to 31 December of the current year

**Follow-up — check a stuck application:**
> "I already started the process. My application is APP-2024-SOC-00389. Is it done?"

**Tool triggered:** `check_application_status("APP-2024-SOC-00389")`

**Expected response highlights:**
- Status: **requires documents**
- Missing: bank statement as of 31/12/2023
- Giulia instructs to bring the complete statement to the CAF desk

---

## Scenario 7 — ZTL Pass (urban mobility)

**Best for:** Quick, practical query. Good for a "let's try something different" mid-demo beat.

**What to say:**
> "I run a small shop inside the historic centre. How do I get a ZTL pass so I can drive in?"

**Tool triggered:** `lookup_service_requirements("ZTL")`

**Expected response highlights:**
- 5 required documents including vehicle registration and proof of entitlement (commercial activity in ZTL)
- Processing time: **15 days**
- Fee: **€50**
- Office: *Ufficio Mobilità e Traffico*
- Pass is tied to the licence plate; valid 12 months

---

## Scenario 8 — Disabled Parking Badge (accessibility)

**Best for:** Empathy and accessibility angle — shows Giulia's patient, helpful tone.

**What to say:**
> "My mother has difficulty walking after her surgery. Can we get a disabled parking badge for her?"

**Tool triggered:** `lookup_service_requirements("disabled parking")`

**Expected response highlights:**
- 5 required documents including ASL medical certificate confirming reduced mobility
- Processing time: **30 days**
- Fee: **free**
- Office: *Ufficio Anagrafe — Sportello Disabilità*
- Valid 5 years for permanent conditions; Giulia should offer to book

---

## Language variants to show

| Language | Suggested scenario | What to watch for |
|---|---|---|
| English | Scenario 1 (residency) | Giulia lists permesso di soggiorno for non-EU |
| Italian | Scenario 3 (building permit status) | Technical terminology stays correct |
| Arabic (Egyptian) | Scenario 1 (residency) | RTL layout; warm colloquial register (كده، عايز) |
| Arabic (Emirati) | Scenario 5 (citizenship) | Formal Gulf register (حضرتك، تفضل) |

---

## Edge cases and failure paths

| Prompt | Expected behaviour |
|---|---|
| "Check my application APP-FAKE-99999" | `found: false` — Giulia says the ID is not in the system and asks the user to double-check |
| "What documents do I need for a spaceship permit?" | `found: false` — Giulia apologises, says the service is not in her database, and offers to help with a related service |
| "Book an appointment for citizenship" | `found: false` — Giulia explains the service is not bookable online and gives the direct office contact |
| "Book an appointment for building permit" | `found: false` — not bookable online; Giulia directs to the Urbanistica office |
| Ask for a service in Italian while language is set to English | Giulia should still respond in English and resolve the service correctly |

---

## Quick-reference: all seeded application IDs

| ID | Service | Status |
|---|---|---|
| APP-2024-ANA-00341 | Residency registration | pending |
| APP-2024-ANA-00289 | Address change | approved |
| APP-2024-ANA-00412 | Birth certificate | approved |
| APP-2024-STA-00112 | Citizenship application | pending |
| APP-2024-STA-00067 | Name change | pending |
| APP-2024-PER-00078 | Building permit | requires\_documents |
| APP-2024-PER-00054 | Commercial activity (SCIA) | approved |
| APP-2024-PER-00031 | Outdoor seating (dehors) | rejected |
| APP-2024-TRA-00203 | Disabled parking badge | approved |
| APP-2024-TRA-00187 | ZTL pass | pending |
| APP-2024-SOC-00445 | TARI registration | approved |
| APP-2024-SOC-00389 | ISEE declaration | requires\_documents |
