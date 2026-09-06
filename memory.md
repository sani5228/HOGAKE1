# MEMORY.md

> Persistent project memory. Read this before starting work in a new session.
> This file summarizes and cross-references `PRD.md`, `architecture.md`, `rules.md`, `phase.md`, and `design.md` — it does not replace them. When this file and a source document disagree, treat it as a flag to re-check both, and prefer `rules.md`'s priority order (see "Documentation Map" below).

> **Inspection note:** This file was generated from the five documentation files only. The repository at https://github.com/sani5228/SIH2026.git could not be inspected in the session that generated this file (no network access available). Several points below (queue/booking status names, exact schema, existing HTML/CSS/JS) are marked **[UNVERIFIED — confirm against repo]** and must be checked against the actual repository/code before being treated as final, per the project's own rule that documentation should never override existing implementation without a deliberate decision.

---

## Project Identity

- **Name:** Smart Online Procurement Slot Booking System for Farmers (brand: **FASAL**). Also referred to as the "SIH 2026 Farmer Procurement Platform."
- **Purpose:** Digitize agricultural procurement so farmers get a pre-assigned center/date/shift instead of showing up to an unstructured queue. Core loop: Registration → Slot Booking → Automatic Allocation → Procurement → Payment/Transaction Record → Dashboards.
- **Status:** Prototype for SIH 2026 / academic demonstration — explicitly **not** a production government system.
- **Main objective:** Reduce farmer wait time and center congestion via deterministic, backend-driven scheduling, while keeping the implementation simple enough for a student team (or AI assistant) to build and maintain.

---

## Long-Term Decisions (do not change without explicit new instruction)

1. **No Twilio, no real SMS gateway.** SMS is simulated by printing the formatted message to the backend terminal/console. Notifications must still go through a Notification Service abstraction so a real provider could be swapped in later without redesigning callers.
2. **No real IVR/telecom integration.** IVR is simulated via REST endpoints that call the same Booking/Scheduling services as the web flow. Real telephony is a future extension only.
3. **No real payment gateway.** Payment status (Pending/Processed/Paid) is recorded and calculated, never processed through a bank/UPI/NEFT integration.
4. **PostgreSQL** is the planned relational database.
5. **Backend: Python/Flask, REST API.** **Frontend: HTML5/CSS3/vanilla JavaScript** (no framework/build step). No frontend business logic — frontend only collects input and renders backend responses.
6. **Existing frontend HTML/CSS/JS (FASAL) in the GitHub repo is the visual design baseline** — https://github.com/sani5228/SIH2026.git. New UI must extend that visual language, not replace it. **[UNVERIFIED — confirm against repo before building UI]**.
7. **Layered architecture, not microservices:** Presentation → API/Controller → Service/Business Logic → Repository/Data Access → PostgreSQL, all as one deployable Flask app.
8. **One shared Scheduling Service** is the sole authority for date/shift/center assignment, used identically by Web and IVR. Booking Service must not duplicate scheduling math.
9. **Farmers never choose their center or date.** Both are always system-assigned.
10. **No unnecessary complexity:** avoid paid APIs, cloud services, microservices, external integrations beyond what's listed, production infra, ML/AI scheduling, blockchain.

---

## Project Constraints

- Prototype-scale, single-team, local deployment: frontend `:5500`, backend `:5000`, PostgreSQL `:5432`.
- Backend is authoritative for all business rules; frontend validation is UX-only.
- Rule priority when documents conflict (per `rules.md` §31): (1) explicit latest project requirement → (2) `rules.md` → (3) `PRD.md` → (4) `architecture.md` → (5) `api-contract.md` → (6) existing implementation. If existing code conflicts with documented rules, flag it — don't silently change either side.
- Secrets via environment variables only (`DATABASE_URL`, `JWT_SECRET`, `FLASK_ENV`, `CORS_ORIGINS`); never hard-coded.

---

## Core Workflow

```
Registration
    ↓
Login (OTP for farmers; credentials [+optional OTP] for center/admin)
    ↓
Select Crop + Enter Quantity (center and date are NOT selected by farmer)
    ↓
Automatic Allocation (Scheduling Service assigns center, date, shift)
    ↓
Token Generated + SMS (simulated) Confirmation
    ↓
Farmer Arrives at Assigned Center/Shift
    ↓
Center Verifies Token → Weighs Actual Quantity
    ↓
Procurement Recorded (total_amount = actual_weight × rate_per_quintal)
    ↓
Payment Status Updated (Pending → Paid)
    ↓
Farmer Views History & Status on Dashboard
```

Booking/procurement channels: **Web** and **IVR (simulated)** — both converge on the same Booking + Scheduling services.

---

## Users and Roles

| Role | Responsibility | Cannot |
|---|---|---|
| **Farmer** | Register/login, select eligible (current-season) crops, enter exact quantity in quintals, view assigned schedule/token/status, cancel/rebook, view procurement & payment history, use chatbot/IVR | Choose center or date, set/see rate, modify token, override capacity/scheduling |
| **Procurement Center Staff** | Manage own crop list & capacity, view own schedule/farmers, verify token, record actual weight, complete procurement | Touch another center's data, bypass admin-only config |
| **Administrator** | Manage farmers/centers/crops, verify new centers, view/manage all bookings & procurement, system-wide stats, via purpose-built management screens only | Use a generic raw-table editor (explicitly disallowed) |

---

## Core Domain Concepts

- **Farmer** — `FA######` ID; profile + location (State/District/Village) + registered crops (many-to-many). Aadhaar stored encrypted, never exposed except masked to Admin / full to the farmer's own profile.
- **Procurement Centre** — `PC######` ID; starts `PENDING_VERIFICATION`, becomes `ACTIVE` after Admin approval; has daily capacity (default 420 min / 7h) split into two shifts; accepts a set of crops (many-to-many).
- **Crop** — name, category, `rate_per_quintal`, `time_to_unload_per_quintal`, one `season` value, active/inactive.
- **Slot / Shift** — Shift 1 (~8–9 AM arrival / 9–12 procurement), Shift 2 (~1–2 PM arrival / 2–5 PM procurement); each shift plans up to 210 min (half of the 420-min daily plan).
- **Booking** — a farmer's request for a crop + quantity; holds the system-assigned center/date/shift and a unique token; distinct lifecycle from the procurement record itself.
- **Token** — backend-generated, unique per booking, never chosen/edited by the farmer.
- **Queue** — position/status of the farmer's booking within a center's day; not a walk-up physical queue — it's the pre-assigned shift/order derived from booking timestamp (FIFO).
- **Procurement (record)** — the actual weighing event: `actual_weight_quintal`, `rate_per_quintal` (applied at procurement time by default), `total_amount = actual_weight × rate`.
- **Payment** — see "Payment Meaning" below; separate table/lifecycle from the procurement record.
- **Notification** — an SMS-simulation event tied to a farmer/center/booking; queued, sent (printed), or failed, independent of whether it blocks the underlying booking/procurement action (it never blocks).

Do not add domain fields beyond what's listed here without checking the actual repo/PRD first.

---

## Queue and Procurement States

**[UNVERIFIED — confirm the authoritative enum against the repo before relying on exact string values.]**

The PRD's `bookings.status` enum (most detailed source found):
```
BOOKED → SCHEDULED → ARRIVED → PROCUREMENT → COMPLETED
                                            ↘ CANCELLED
                                            ↘ RESCHEDULED
```
`rules.md` describes the same lifecycle in slightly different terms ("Booked → Scheduled → Arrived → Weighed → Procured/Completed") and explicitly says exact status names must match whatever the backend implementation actually uses — it does not itself lock in a naming scheme. `architecture.md`'s procurement sequence diagram uses informal lowercase strings ("arrived", "completed", "pending") for illustration only. Treat the PRD's uppercase enum as the working default, but verify against the real backend/database before writing code that depends on exact values.

Related enums seen in the docs:
- `procurement_centers.status`: `PENDING_VERIFICATION`, `ACTIVE`, `SUSPENDED`
- `farmers.status`: `ACTIVE`, `SUSPENDED`
- `crops.status`: `ACTIVE`, `INACTIVE`
- `payments.status`: `PENDING`, `PAID`, `FAILED` (rules.md phrases this informally as "Pending, Processed, Paid")
- `notifications.status`: `QUEUED`, `SENT`, `FAILED`

---

## Notification Architecture

```
Backend (Booking / Procurement / Auth events)
   ↓
Notification Service (formats message; abstraction layer)
   ↓
Terminal / console print — simulated SMS output
```

- No Twilio, no real SMS/telecom provider, in this prototype.
- The service boundary must remain real (not inlined into routes), so a real provider can be plugged in later.
- SMS failure must never block the underlying booking/procurement action; it's tracked independently on the `notifications` record.
- UI may say "SMS generated successfully" but must never claim actual delivery occurred.

---

## Payment Meaning

Payment = the amount owed **to the farmer** for the produce actually procured by the center — not a payment collected from anyone.
```
Payment Amount = Actual Weight (quintals) × Rate per Quintal (at procurement time, by default)
```
No real banking/payment-gateway integration is required or in scope unless explicitly requested later; payment is a recorded/calculated status only (Pending/Processed/Paid terminology per `rules.md`; Pending/Paid/Failed per PRD schema — same concept, confirm exact values against repo).

---

## Backend Conventions

- REST-style APIs; one authoritative API contract (`api-contract.md`) — no duplicate contract content anywhere else.
- Explicit request/response schemas, input validation, and consistent HTTP status codes on every endpoint.
- Centralized auth/authorization middleware validates JWTs and role before a request reaches business logic.
- Strict layer separation: routes handle HTTP only; all scheduling/procurement/business rules live in services; only repositories touch PostgreSQL directly.
- Services of record: Auth, Farmer, Center, Crop, Booking, Scheduling (sole scheduling authority), Procurement, Admin, Notification, IVR Simulation.
- Scheduling specifics: 420-minute (7h) planning capacity per center/day (two 210-min shifts); ~510-minute (8.5h) hard operational ceiling absorbs late arrivals/delays but is never pre-allocated to new bookings. Allocation order: earliest date/shift with sufficient remaining capacity, at an eligible `ACTIVE` center that accepts the crop; ties broken by earliest booking timestamp (FIFO), then smaller quantity, then a deterministic secondary key (e.g. booking ID).
- Concurrency: capacity checks + schedule assignment must be atomic (e.g. row-lock on the daily capacity ledger) to prevent Web+IVR race conditions overbooking a center/day.

---

## Database Conventions

- PostgreSQL is the system of record. Use the **actual schema already in the repository as source of truth** once inspected — don't re-derive it purely from documentation.
- Roles (Farmer/Center/Admin) are **separate tables**, not one generic `users` table — their fields and security postures differ too much (Aadhaar encryption only applies to farmers, etc.). A shared `FA`/`PC`/`AD` ID-prefix convention is used for readability only.
- Key relationships: `farmers` ↔ `crops` via `farmer_crops`; `procurement_centers` ↔ `crops` via `center_crops`; `bookings` references farmer/crop/(nullable-until-allocated) center; a capacity ledger table tracks committed minutes per center/date/shift; `procurement_records` references `bookings` (1:1-ish, post-arrival); `payments` references `procurement_records`; `notifications` references farmer/center/booking (all nullable, event-based).
- Booking vs. Procurement are **deliberately separate tables/records** — booking is pre-arrival intent, procurement is the actual post-arrival event — so status transitions and cancellation/rebooking don't disturb historical procurement data.
- `total_amount` / rate / quantity math is always computed server-side, never accepted from the client.
- Aadhaar: encrypted at rest, only last 4 digits ever shown outside Admin's controlled verification workflow; never returned in any Center-scoped API response.

---

## Frontend / Design Reference

- Brand: **FASAL** — natural/agricultural, warm cream/paper backgrounds, green ("sprout") and harvest-orange accents, soil-brown text, soft borders, rounded cards (7–14px radius), subtle shadows, minimal/spacious layout, ~1180px max content width.
- Typography: **Fraunces** for display/headings/brand, **Inter** for body/UI/tables/forms.
- Design source of truth: the existing repo's `home.html/css/js`, `index.html`, `style.css`, `script.js` **[UNVERIFIED — inspect repo before building new pages]**. Reuse existing CSS variables/tokens, buttons, cards, form patterns, header/nav, mobile hamburger nav, and the existing multilingual language selector (English, Hindi, Tamil, Punjabi, Assamese, Telugu) rather than introducing new ones.
- Do not: replace the palette/fonts/branding, introduce a generic blue SaaS dashboard look, add heavy gradients/glassmorphism, or move backend business logic into the frontend to simplify UI work.
- Status badges must use both color and text (semantic color, e.g. green=scheduled/completed, wheat/orange=arrived, error=cancelled) — never color alone.

---

## Documentation Map

- `PRD.md` — what the product does (problem, goals, users, requirements, journeys, DB design, API design, MVP scope).
- `architecture.md` — how the system is structured (layers, services, tech stack, deployment, directory structure).
- `rules.md` — authoritative business/validation/security rules; does **not** duplicate schema or API contract.
- `phase.md` — build order (Phases 0–16, Project Prep → Demo Prep), dependencies, definition of done, progress tracking table.
- `design.md` — UI/UX spec; existing repo HTML/CSS/JS is the design baseline.
- `api-contract.md` — (referenced by all four documents above as the single authoritative endpoint contract; not among the files reviewed when this memory file was written — locate and inspect it before implementing/consuming any endpoint.)
- `memory.md` (this file) — persistent cross-session context; intentionally does not duplicate full sections of the above.

---

## Repository Reference

- **URL:** https://github.com/sani5228/SIH2026.git
- Contains the existing FASAL homepage and registration page (HTML/CSS/JS) that establish the visual baseline, and is the presumed home for the eventual Flask backend and PostgreSQL schema.
- **Not yet inspected as of this file's creation** (no network access in that session). Before making further assumptions about existing implementation, schema, status-enum naming, or frontend structure, clone/inspect the repo directly.

---

## Development Principles

1. Build database → backend foundation → auth → farmer/crop/center modules → booking → scheduling → procurement → notifications/IVR → dashboards → integration testing → security hardening → polish → demo prep (see `phase.md` Phases 0–16 for full detail; don't duplicate here).
2. Business logic before UI polish; each phase tested before moving on.
3. Web and IVR always share one booking/scheduling implementation — never two.
4. No silent resolution of documentation conflicts — record them and decide deliberately (see `phase.md` §24 "Phase Planning Issues" and `architecture.md` §36 "Consistency Issues" for where these are meant to be logged).

---

## Change History / Important Decisions

- **Initial memory.md created** from `PRD.md`, `architecture.md`, `rules.md`, `phase.md`, `design.md` (repository not inspected — no network access in that session; repo inspection still pending).
- **Open discrepancy to resolve on next repo-connected session:** `architecture.md` §33 lists "Audit logging" and "Real-time queue tracking" under *Future Extensions* (not yet implemented), while `PRD.md` §21 defines `audit_log` as a core table required by the NFRs and Admin's "no raw table editor" constraint. Per the rules.md priority order, PRD.md outranks architecture.md — treat audit logging as an in-scope current requirement, not a future extension, until this is explicitly reconciled in the documents themselves.
- **Open item:** exact booking/procurement status string values are not yet locked in — see "Queue and Procurement States" above.
