# Architecture Document
## Smart Online Procurement Slot Booking System for Farmers

**Document type:** Technical Architecture
**Project type:** Student Prototype (not a production government platform)
**Status:** Authoritative for implementation, consistent with PRD and API contract

---

## 1. Purpose

This document describes the actual technical architecture to be implemented for the Smart Online Procurement Slot Booking System. It covers the overall system, frontend, backend, database, authentication, booking, slot allocation, scheduling, procurement, mock SMS, mock IVR, the admin/procurement-center/farmer roles, API communication, data flow, security, deployment, and the project directory structure.

This architecture is intentionally simple. It avoids microservices, container orchestration, cloud infrastructure, payment gateways, real SMS/telecom providers, and external AI APIs, because the goal is a clean, understandable, extensible prototype — not a production government system.

This document must remain consistent with the project's PRD and API contract. Section 36 records the result of an internal consistency check against those documents.

---

## 2. Technology Stack

**Frontend**
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- Responsive UI (no frontend framework/build step required)

**Backend**
- Python
- Flask
- REST API

**Database**
- PostgreSQL

**Authentication**
- JWT (or the authentication mechanism already implemented by the backend)
- Role-based authorization

**Roles**
- `farmer`
- `center`
- `admin`

**Prototype SMS**
- No Twilio, no external SMS gateway
- SMS is simulated by printing the generated message to the backend terminal

**Prototype IVR**
- No real telecom/IVR provider
- IVR is simulated entirely through REST API endpoints

---

## 3. High-Level Architecture

```
                    ┌─────────────────────┐
                    │      Farmer         │
                    │  Web / IVR Mock     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Frontend       │
                    │ HTML/CSS/JavaScript │
                    └──────────┬──────────┘
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │   Flask Backend     │
                    │                     │
                    │ Auth                │
                    │ Booking             │
                    │ Scheduling          │
                    │ Procurement         │
                    │ Admin               │
                    │ IVR                 │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    PostgreSQL       │
                    │      Database       │
                    └─────────────────────┘

                    Backend Terminal
                           ▲
                           │
                    Mock SMS / OTP
```

**Component responsibilities**

| Component | Responsibility |
|---|---|
| Farmer (Web / IVR Mock) | End user interacting through a browser, or through the simulated IVR flow which reuses the same booking APIs. |
| Frontend | Renders pages, collects input, calls backend REST APIs, displays backend-computed results. Contains no business logic. |
| Flask Backend | Hosts all REST endpoints; contains auth, booking, scheduling, procurement, admin, and IVR simulation logic. |
| PostgreSQL | System of record for users, farmers, centers, crops, bookings, schedules, and procurement records. |
| Backend Terminal | Destination for mock SMS/OTP output — simulates an SMS provider by printing to stdout/logs. |

### 3.1 Mermaid — System Architecture

```mermaid
flowchart TD
    A[Farmer - Web Browser] --> B[Frontend: HTML/CSS/JS]
    A2[Farmer - IVR Mock] --> C
    B -->|REST API - fetch| C[Flask Backend]
    C --> D[Auth Service]
    C --> E[Booking Service]
    C --> F[Scheduling Service]
    C --> G[Procurement Service]
    C --> H[Admin Service]
    C --> I[IVR Simulation Service]
    D --> J[(PostgreSQL)]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    E --> K[Notification Service]
    K --> L[Backend Terminal - Mock SMS]
```

---

## 4. Architectural Style

The system uses a **simple layered architecture**:

```
Presentation Layer
        ↓
API / Controller Layer
        ↓
Service / Business Logic Layer
        ↓
Repository / Data Access Layer
        ↓
PostgreSQL
```

### 4.1 Why layered architecture instead of microservices

- The system has a single team, a single deployable backend, and a small, well-understood domain (booking + scheduling + procurement). Microservices would add network boundaries, deployment complexity, and inter-service contracts with no corresponding benefit at this scale.
- A single Flask application with clear internal layers gives the same separation of concerns (routes vs. business logic vs. data access) without the operational overhead of service discovery, distributed transactions, or container orchestration.
- It keeps the codebase easy for a student team (or an AI coding assistant) to navigate, test, and extend.
- It preserves a clean upgrade path: because responsibilities are already separated into services and repositories, any service could later be extracted into its own deployable unit if the project ever needed to scale that way. That extraction is explicitly a **future extension** (Section 34), not part of this prototype.

### 4.2 Layer rules

- **Frontend does not contain business logic.** It only collects input, calls the API client, and renders backend responses.
- **API routes handle HTTP concerns only** — parsing requests, invoking the correct service, and shaping the HTTP response. Routes do not contain scheduling math or procurement rules.
- **Services contain scheduling and procurement logic.** All domain rules (crop eligibility, time calculation, booking ordering, token generation) live here.
- **The database layer (repositories) handles persistence** — queries, inserts, updates, and transactions — and is the only layer that talks to PostgreSQL directly.
- **Authentication middleware handles authorization**, validating JWTs and enforcing role checks before a request reaches a route's business logic.

---

## 5. Component Architecture

### 5.1 Backend services

| Service | Responsibility |
|---|---|
| **Auth Service** | Registration, login, OTP verification, JWT issuance/validation, password/OTP hashing. |
| **Farmer Service** | Farmer profile management, crop selection, farmer-facing booking history and status views. |
| **Center Service** | Center profile management, crop/capacity configuration, center schedule views, marking arrival, recording actual weight. |
| **Crop Service** | Crop catalog: rate per quintal, time per quintal, season, active/inactive status. Used by admin for CRUD and by other services for lookups. |
| **Booking Service** | Validates booking requests (farmer, crop, quantity), orchestrates the booking lifecycle (create, view, cancel, rebook), and persists the booking record. It **delegates all scheduling decisions to the Scheduling Service** — it does not duplicate scheduling math. |
| **Scheduling Service** | The single authority for scheduling decisions: eligible center selection, procurement duration calculation, booking ordering, date/shift/slot assignment, and token generation rules. Used identically by both web and IVR booking flows. |
| **Procurement Service** | Records actual weight, computes procurement amount, tracks payment status ("pending" for the prototype), and marks procurement completion. |
| **Admin Service** | Farmer/center/crop management, system-wide statistics, and administrative views over bookings and procurement. |
| **Notification Service** | Formats and "sends" notifications. For the prototype, this **only simulates SMS** by printing the formatted message to the backend terminal. |
| **IVR Simulation Service** | Simulates a telecom IVR session (mobile number → language → crop → quantity) purely via REST endpoints, then calls the same Booking Service and Scheduling Service used by the web flow. |

### 5.2 Key architectural constraints

- The **Booking Service must not duplicate scheduling calculations**; all date/shift/slot/duration logic belongs to the Scheduling Service.
- The **Scheduling Service is the sole owner of scheduling decisions** for both web and IVR bookings.
- The **Notification Service only simulates SMS** — it has no real transport integration in this prototype.

### 5.3 Mermaid — Backend Layered Architecture

```mermaid
flowchart TD
    subgraph Presentation
        P1[Frontend Pages]
    end
    subgraph API["API / Controller Layer"]
        R1[routes/auth.py]
        R2[routes/farmer.py]
        R3[routes/center.py]
        R4[routes/booking.py]
        R5[routes/procurement.py]
        R6[routes/admin.py]
        R7[routes/ivr.py]
    end
    subgraph Service["Service / Business Logic Layer"]
        S1[Auth Service]
        S2[Farmer Service]
        S3[Center Service]
        S4[Crop Service]
        S5[Booking Service]
        S6[Scheduling Service]
        S7[Procurement Service]
        S8[Admin Service]
        S9[Notification Service]
        S10[IVR Simulation Service]
    end
    subgraph Repo["Repository / Data Access Layer"]
        D1[(Repositories)]
    end
    subgraph DB["Database"]
        PG[(PostgreSQL)]
    end

    P1 -->|REST API| R1 & R2 & R3 & R4 & R5 & R6 & R7
    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S5
    R5 --> S7
    R6 --> S8
    R7 --> S10
    S5 --> S6
    S5 --> S9
    S10 --> S5
    S1 & S2 & S3 & S4 & S5 & S6 & S7 & S8 --> D1
    D1 --> PG
```

---

## 6. Frontend Architecture

```
Pages
 ↓
Page-specific JS
 ↓
Central API Client
 ↓
REST API
```

All frontend API communication goes through a single module: **`frontend/js/api.js`**. Individual pages never call `fetch()` directly; they call functions exported by `api.js` (e.g. `api.createBooking(payload)`, `api.getFarmerCrops()`). This keeps base URL, headers, auth-token attachment, and error handling in one place, and makes it trivial to change API behavior without touching every page.

**Responsibilities addressed by the frontend layer:**

- **Authentication state:** The JWT (or session token) returned at login is stored in memory/`sessionStorage`-equivalent client state and attached by `api.js` to every authenticated request as an `Authorization` header. Login state is checked on page load to decide whether to redirect to login.
- **Role-based routing:** After login, the frontend reads the role (`farmer` / `center` / `admin`) from the auth response and redirects to the corresponding dashboard (`/farmer/`, `/center/`, `/admin/`). Pages under `/admin/` are not reachable without an admin session, etc. — this is a UX convenience only; the backend still enforces authorization independently.
- **API error handling:** `api.js` normalizes backend error responses (see Section 25's error shape) into a consistent object that page-specific JS can use to show a message, without every page re-implementing parsing logic.
- **Loading states:** Page-specific JS toggles simple loading indicators (e.g., disabling a submit button, showing a spinner element) while an `api.js` call is in flight.
- **Form validation:** Basic client-side validation (required fields, numeric quantity, format checks) runs before submission purely to improve UX. It is never treated as the source of truth — the backend re-validates everything.
- **Dashboard rendering:** Each role's dashboard page fetches its own data (bookings, schedule, statistics) through `api.js` and renders it into the DOM using vanilla JS templating (string templates / `innerHTML` population).
- **Responsive design:** CSS uses relative units and a small set of breakpoints in `frontend/css/` so pages remain usable on mobile browsers, which matters given the target users.

---

## 7. User Roles and Permissions

### 7.1 Farmer

**Can:**
- Register
- Login
- Select crops
- View eligible crops
- Create booking
- View booking
- Cancel booking
- Rebook
- View procurement status
- View history
- Manage crop selection

**Cannot:**
- Select an arbitrary procurement center
- Select an arbitrary date
- Change the system-generated token
- Change the rate
- Change the estimated procurement time
- Access other farmers' data

### 7.2 Procurement Center

**Can:**
- Register
- Login
- Manage crop selection
- Manage capacity
- View its own schedule
- View associated farmers
- Mark farmer arrival
- Record actual weight
- Complete procurement
- View procurement history

**Cannot:**
- Modify another center's schedule
- Modify booking allocation
- Change government/admin-defined crop rate
- Access unrelated farmers
- View Aadhaar data unnecessarily

### 7.3 Admin

**Can:**
- View dashboard
- Manage farmers
- Manage centers
- Manage crops (add, edit, deactivate)
- View bookings
- View procurement
- View system statistics

**Constraint:** Admin accounts are predefined (seeded/provisioned directly). There is **no public admin registration** endpoint or page.

All permission boundaries above are enforced in the **Authentication/Authorization middleware and service layer**, not just hidden in the UI.

---

## 8. Core Data Flow

### 8.1 Farmer Registration

```
Farmer
 ↓
Frontend
 ↓
OTP API
 ↓
OTP Verification
 ↓
Farmer Registration API
 ↓
Farmer Service
 ↓
PostgreSQL
 ↓
Farmer ID Generated
 ↓
Frontend
```

### 8.2 Web Booking

```
Farmer
 ↓
Select eligible crop
 ↓
Enter quantity in quintals
 ↓
Confirm booking
 ↓
POST /api/bookings
 ↓
Booking Service
 ↓
Validate farmer/crop/quantity
 ↓
Scheduling Service
 ↓
Find eligible center
 ↓
Calculate procurement duration
 ↓
Apply booking ordering rules
 ↓
Assign date
 ↓
Assign shift
 ↓
Assign slot
 ↓
Generate token
 ↓
Save booking
 ↓
Notification Service
 ↓
Print mock SMS
 ↓
Return booking
 ↓
Frontend confirmation page
```

### 8.3 Mermaid — Booking Flow

```mermaid
sequenceDiagram
    participant F as Farmer (Frontend)
    participant API as Booking API
    participant BS as Booking Service
    participant SS as Scheduling Service
    participant N as Notification Service
    participant DB as PostgreSQL

    F->>API: POST /api/bookings (crop, quantity)
    API->>BS: create_booking(request)
    BS->>DB: Validate farmer, crop, eligibility
    BS->>SS: request_schedule(farmer, crop, quantity)
    SS->>DB: Read center capacity / existing schedule
    SS->>SS: Compute duration, apply ordering rules
    SS->>DB: Reserve date/shift/slot (transaction)
    SS-->>BS: date, center, shift, slot, estimated_time
    BS->>BS: Generate token
    BS->>DB: Save booking + booking_schedule (commit)
    BS->>N: notify(booking)
    N->>N: Print mock SMS to terminal
    BS-->>API: booking confirmation
    API-->>F: 201 Created + booking details
```

---

## 9. Scheduling Architecture

This section is the core scheduling contract for the system and must not be reinterpreted elsewhere.

### 9.1 Real center working time

A procurement center works approximately **8 hours/day**. This is the real, physical operational working time of the center.

### 9.2 Scheduling calculation time

For **slot allocation and normal booking capacity**, the system uses **7 hours/day** as the planning/scheduling limit.

The remaining ~1 hour of real operational time is **intentionally reserved bandwidth**, not normal booking capacity. It exists to absorb:

- Late arrivals
- Delays
- Operational variation
- Unexpected processing time
- Other real-center situations

**Rule:** The system must never treat the full 8-hour operational time as normal booking capacity. Only the 7-hour planning limit is used when assigning new bookings to a day.

### 9.3 Mermaid — Scheduling Flow

```mermaid
flowchart TD
    A[New booking request: crop, quantity] --> B[Scheduling Service]
    B --> C{Eligible center available?}
    C -- No --> Z[Reject / no eligible center]
    C -- Yes --> D[Compute estimated_time = time_per_quintal x quantity]
    D --> E{7-hour planning capacity<br/>available on current day?}
    E -- Yes --> F[Assign current day: date, shift, slot]
    E -- No --> G[Move to next available date]
    G --> E
    F --> H[Generate token]
    H --> I[Persist booking + schedule in transaction]
```

---

## 10. Time Calculation

Each crop has a configured `procurement_time_per_quintal`.

**Single crop booking:**

```
estimated_time = procurement_time_per_quintal × expected_quantity_quintal
```

**Multiple crops (if a booking spans multiple crops):**

```
Total Estimated Time =
    (a × quantity_a) + (b × quantity_b) + (c × quantity_c)
```

Where `a`, `b`, `c` are the per-quintal procurement times for crops A, B, and C respectively.

**Architectural rule:** The backend (Scheduling Service) performs this calculation. The frontend never computes estimated time itself — it only displays the value returned by the API.

---

## 11. Booking Order

Booking allocation follows **First Book → First Serve**.

- The primary ordering factor is the booking timestamp (server-side, at the moment the booking request is accepted and validated — not client-submitted time).
- If two bookings arrive at effectively the same time, the timestamp is recorded with sufficient precision (e.g., microsecond-resolution database timestamp) to break the tie in most cases.
- If timestamps still tie exactly, a deterministic tie-breaker is used (Section 12).

This keeps the algorithm simple, predictable, and easy to test — no priority queues or optimization heuristics are introduced.

---

## 12. Same-Time Booking Rule

When two farmers book at essentially the same time **for the same crop**, apply this deterministic ordering, in order:

1. **Lower quantity → earlier slot**
2. If quantity is equal → **earlier booking timestamp**
3. If timestamp is identical → **lower user/booking ID**

This is used strictly as a tie-breaker within the same crop and (implicitly) the same eligible center/day context — it does not override the general First-Book-First-Serve rule; it only resolves ties within it.

---

## 13. Different Crops

When the two competing bookings are for **different crops**:

1. First determine whether the bookings would go to **different procurement centers**.
   - **Different centers:** No conflict. Each center schedules its own bookings independently — there is nothing to compare.
   - **Same center:** Compare estimated procurement duration for each booking:
     ```
     estimated_time = crop_time_per_quintal × quantity
     ```
     The Scheduling Service uses the defined ordering rules (Sections 11–12, applied consistently) to determine relative placement on the shared center schedule.

No additional optimization algorithm (e.g., bin-packing, load balancing across centers) is introduced. The rule set stays deterministic and simple, consistent with Section 26 (Non-Goals do not include advanced scheduling optimization).

---

## 14. Date Allocation

Farmers do **not** select the date. The farmer only submits: crop, quantity (and, implicitly, is matched to an eligible center by the Scheduling Service).

The backend determines:
- **Date**
- **Center**
- **Shift**
- **Slot**

If the current day's **7-hour planning capacity** is already filled for the relevant center, the booking is pushed to the **next available date**. A later farmer is never assigned to an already-full day just because the center physically operates for 8 hours — the 7-hour planning limit is what defines "full" for allocation purposes (see Section 9).

---

## 15. Working-Hour Rounding

For the prototype:

- The real operational working period is represented as **approximately 8 hours/day**.
- The **configured 7-hour scheduling limit** is what planning/allocation logic uses.
- Any UI display or internal rounding of working hours must never cause normal scheduled booking capacity to exceed the configured 7-hour planning limit.
- The implementation keeps this as a single configuration value (e.g., `DAILY_PLANNING_HOURS = 7`, `DAILY_OPERATIONAL_HOURS = 8`) rather than scattering hour math across multiple modules, to keep behavior deterministic and easy to verify.

---

## 16. Late Arrival / Bandwidth

If a farmer does not arrive during their assigned slot/window:

1. The backend checks the center's **remaining real operational bandwidth** for that day (up to the ~8-hour operational limit, i.e., including the reserved ~1 hour discussed in Section 9).
2. **If sufficient real operational bandwidth remains:** the center may still procure the farmer that day (operationally possible, handled as an exception path, not as new "planned" capacity).
3. **Otherwise:** the farmer must rebook (a new booking request goes back through the normal Scheduling Service flow).

**Architectural rule:** The frontend only displays the resulting backend status (e.g., "Late — center may still accommodate you" vs. "Rebooking required"). The frontend never independently decides whether a late farmer can be accommodated — that decision is made solely by the backend (Scheduling/Procurement Service), consistent with the single-source-of-truth principle (Section 27).

---

## 17. Token Architecture

- Tokens are generated by the **backend** (Booking Service, using rules provided by the Scheduling Service context) — never by the frontend.
- Format example: `TK-20260905-0012` (prefix + date + zero-padded sequence, or an equivalent deterministic scheme chosen at implementation time).

**A token must be:**
- Unique
- Associated with exactly one booking
- Displayed to the farmer
- Displayed to the center
- Used for procurement identification

The frontend cannot generate or modify tokens under any circumstance; it only renders the token value returned by the API.

---

## 18. Database Architecture

**Core tables/entities:**

- `users`
- `farmers`
- `procurement_centers`
- `crops`
- `farmer_crops`
- `center_crops`
- `bookings`
- `booking_schedule`
- `procurements`
- `notifications`
- `otp_sessions`
- `ivr_sessions`

**Relationships:**

```
User
 ├── Farmer
 └── Procurement Center

Farmer
 └── Farmer Crops

Center
 └── Center Crops

Farmer
 └── Bookings

Crop
 └── Bookings

Booking
 └── Booking Schedule

Booking
 └── Procurement
```

**Rationale for table separation (avoiding redundant tables):**

- `users` holds shared identity/auth fields (credentials, role, mobile number) common to both farmers and centers, avoiding duplicated auth logic; `farmers` and `procurement_centers` hold role-specific profile data, linked 1:1 to `users`.
- `farmer_crops` / `center_crops` are junction tables because a farmer can grow multiple crops and a center can accept multiple crops — a plain foreign key would not model this many-to-many relationship.
- `booking_schedule` is kept separate from `bookings` because scheduling attributes (assigned date/shift/slot, capacity bookkeeping) are owned and mutated by the Scheduling Service, while `bookings` itself represents the farmer's request and its core state. Separating them keeps the Scheduling Service's writes isolated from the Booking Service's writes, matching the layer/service boundaries in Section 5.
- `procurements` is separate from `bookings` because it represents a distinct real-world event (what actually happened at the center: actual weight, payment) that occurs after and independently of the booking, and does not exist until procurement begins.
- `otp_sessions` and `ivr_sessions` are separate, short-lived/session-scoped tables so that authentication/session churn does not pollute the core `users`/`bookings` tables.
- `notifications` stores a log of simulated SMS sends (for demo/debugging visibility), separate from the domain tables it references.

### 18.1 Mermaid — Database ER Diagram

```mermaid
erDiagram
    USERS ||--o| FARMERS : "is-a"
    USERS ||--o| PROCUREMENT_CENTERS : "is-a"
    FARMERS ||--o{ FARMER_CROPS : selects
    CROPS ||--o{ FARMER_CROPS : "selected in"
    PROCUREMENT_CENTERS ||--o{ CENTER_CROPS : accepts
    CROPS ||--o{ CENTER_CROPS : "accepted in"
    FARMERS ||--o{ BOOKINGS : creates
    CROPS ||--o{ BOOKINGS : "booked for"
    PROCUREMENT_CENTERS ||--o{ BOOKINGS : "assigned to"
    BOOKINGS ||--|| BOOKING_SCHEDULE : has
    BOOKINGS ||--o| PROCUREMENTS : results_in
    FARMERS ||--o{ OTP_SESSIONS : verifies
    FARMERS ||--o{ IVR_SESSIONS : uses
    BOOKINGS ||--o{ NOTIFICATIONS : triggers

    USERS {
        int user_id PK
        string mobile_number
        string password_hash
        string role
        timestamp created_at
    }
    FARMERS {
        int user_id PK
        string name
        string aadhaar
        string state
        string district
        string village_town
    }
    PROCUREMENT_CENTERS {
        int user_id PK
        string name
        string state
        string district
        string village_town
        int capacity
        string verification_status
    }
    CROPS {
        int crop_id PK
        string name
        decimal rate_per_quintal
        decimal time_per_quintal
        string season
        boolean is_active
    }
    BOOKINGS {
        int booking_id PK
        int farmer_id FK
        int crop_id FK
        decimal expected_quantity_quintal
        string booking_method
        string token
        int assigned_center FK
        date assigned_date
        string shift
        time start_time
        time end_time
        int estimated_time_minutes
        string status
        timestamp created_at
    }
    BOOKING_SCHEDULE {
        int schedule_id PK
        int booking_id FK
        date slot_date
        string shift
        int slot_index
    }
    PROCUREMENTS {
        int procurement_id PK
        int booking_id FK
        decimal actual_weight_quintal
        decimal rate_per_quintal
        decimal total_amount
        string payment_status
        timestamp completed_at
    }
```

---

## 19. Important Database Fields

**Crop**
- `crop_id`
- `name`
- `rate_per_quintal`
- `time_per_quintal`
- `season`
- `is_active`

**Farmer**
- `user_id`
- `name`
- `mobile_number`
- `aadhaar`
- `state`
- `district`
- `village_town`

**Center**
- `user_id`
- `name`
- `mobile_number`
- `state`
- `district`
- `village_town`
- `capacity`
- `verification_status`

**Booking**
- `booking_id`
- `farmer_id`
- `crop_id`
- `expected_quantity_quintal`
- `booking_method`
- `token`
- `assigned_center`
- `assigned_date`
- `shift`
- `start_time`
- `end_time`
- `estimated_time_minutes`
- `status`
- `created_at`

**Procurement**
- `procurement_id`
- `booking_id`
- `actual_weight_quintal`
- `rate_per_quintal`
- `total_amount`
- `payment_status`
- `completed_at`

---

## 20. Rate and Payment Architecture

- Crop rate is stored centrally in the crop configuration (`crops.rate_per_quintal`), expressed as **₹ / Quintal**.
- Final procurement amount:
  ```
  total_amount = actual_weight_quintal × rate_per_quintal
  ```
- For the prototype:
  - No real payment gateway
  - No bank integration
  - No UPI API
  - Payment status can remain `"pending"` indefinitely
  - The system only records the calculated `total_amount` and a `payment_status` field — no money actually moves.

---

## 21. Mock SMS Architecture

```
Booking Service
      ↓
Notification Service
      ↓
Mock SMS Generator
      ↓
Backend Terminal
```

**Example terminal output:**

```
==================================================
MOCK SMS
To: +91XXXXXXXXXX

Booking Confirmed

Token: TK-20260905-0012
Crop: Wheat
Quantity: 50 Quintal
Center: Center A
Date: 08-09-2026
Estimated Time: 250 minutes
==================================================
```

No external SMS provider is required. The Notification Service formats the message and prints it (e.g., via `print()` or the standard logger) to the backend process's stdout. Optionally, a row can be inserted into `notifications` for auditability within the app itself.

### 21.1 Mermaid — Authentication Flow (OTP via Mock SMS)

```mermaid
sequenceDiagram
    participant F as Farmer (Frontend)
    participant API as Auth API
    participant AS as Auth Service
    participant N as Notification Service
    participant DB as PostgreSQL

    F->>API: POST /api/auth/otp/request (mobile_number)
    API->>AS: generate_otp(mobile_number)
    AS->>DB: Save otp_sessions record
    AS->>N: notify(otp_message)
    N->>N: Print mock OTP SMS to terminal
    AS-->>API: OTP session created
    API-->>F: 200 OK

    F->>API: POST /api/auth/otp/verify (mobile_number, otp)
    API->>AS: verify_otp(mobile_number, otp)
    AS->>DB: Validate otp_sessions record
    AS->>AS: Issue JWT (role-bound)
    AS-->>API: JWT + role
    API-->>F: 200 OK + token
```

---

## 22. IVR Architecture

IVR is simulated entirely through REST APIs — there is no real telecom/IVR provider.

```
Mobile Number
 ↓
IVR Session
 ↓
Language
 ↓
Crop
 ↓
Quantity
 ↓
Booking Service
 ↓
Scheduling Service
 ↓
Booking Created
```

**Architectural rule:** The IVR booking path calls the **same** Booking Service and Scheduling Service used by the web flow. A second/parallel scheduling algorithm for IVR is explicitly disallowed — this guarantees identical, consistent scheduling behavior regardless of channel.

### 22.1 Mermaid — IVR Flow

```mermaid
flowchart TD
    A[Incoming mobile number] --> B[Create ivr_sessions record]
    B --> C[Prompt: select language]
    C --> D[Prompt: select crop]
    D --> E[Prompt: enter quantity]
    E --> F[IVR Simulation Service submits to Booking Service]
    F --> G[Booking Service validates request]
    G --> H[Scheduling Service - same engine as web]
    H --> I[Booking created + token generated]
    I --> J[Notification Service - mock SMS]
```

---

## 23. API Architecture

The API is REST-based over JSON. Endpoint groups:

```
/api/auth/*
/api/farmer/*
/api/center/*
/api/bookings/*
/api/procurement/*
/api/admin/*
/api/ivr/*
```

This document intentionally does **not** duplicate the complete API contract. The authoritative endpoint paths, request schemas, response schemas, and status codes are defined in the project's API contract document (`api-contract.md`, maintained alongside this project). If `api-contract.md` is not yet present in the repository, the backend API contract maintained alongside the project's route definitions is authoritative. No additional endpoints beyond what is defined there should be introduced by this architecture document.

---

## 24. Security Architecture

- **Password/OTP handling:** Passwords are hashed (e.g., bcrypt/werkzeug security helpers) before storage; OTPs are short-lived, single-use, and stored in `otp_sessions` with an expiry, never stored in plaintext logs beyond the mock SMS terminal print used for demo purposes.
- **JWT/session security:** JWTs are signed with a server-side secret (`JWT_SECRET`), carry role and user identity claims, and have an expiry. Tokens are validated on every protected request.
- **Authorization middleware:** A shared middleware validates the JWT and attaches the authenticated user/role to the request context before it reaches route handlers.
- **Role-based access:** Each route enforces which role(s) may call it (e.g., only `admin` may deactivate a crop; only `center` may mark arrival for its own bookings).
- **Input validation:** All request bodies are validated (types, required fields, ranges) at the API layer before being passed to services.
- **SQL parameterization/ORM:** All database access uses parameterized queries or an ORM (e.g., SQLAlchemy) — no string-concatenated SQL.
- **Aadhaar protection:** Aadhaar numbers are stored only where required (`farmers.aadhaar`) and are **not** included in center-facing API responses (Section 7.2). Where displayed at all, masking should be used.
- **No unnecessary sensitive data in frontend:** API responses to non-privileged roles omit fields like Aadhaar; the frontend never requests or renders fields a role isn't permitted to see.
- **CORS configuration:** CORS is configured for local development (allowing the frontend's local origin, e.g. `http://localhost:5500`) via `CORS_ORIGINS`.
- **Environment variables for secrets:** `DATABASE_URL`, `JWT_SECRET`, etc. are read from environment variables, never hard-coded.
- **Never commit secrets:** `.env` is git-ignored; `.env.example` documents required variables with placeholder values.

**Demo vs. production security:** This prototype uses reasonable baseline practices (hashing, JWTs, parameterized queries, role checks) suitable for a student demo. It explicitly does **not** implement production-grade concerns such as rate limiting, WAF protection, secrets management services, audit logging, penetration-tested Aadhaar handling, or compliance-grade encryption at rest — these belong to a future, production-hardening phase (Section 34).

---

## 25. Error Handling

```
Frontend
 ↓
API
 ↓
Validation
 ↓
Service
 ↓
Database
```

All error responses use a consistent structure:

```json
{
  "success": false,
  "message": "Booking could not be created",
  "error_code": "BOOKING_ERROR",
  "data": null
}
```

- The **frontend** displays a user-friendly message derived from `message` (never raw stack traces).
- The **backend** logs technical details (stack trace, request context) server-side for debugging, while returning only the safe, structured error to the client.
- Validation errors (bad input), business-rule errors (e.g., no eligible center), and system errors (DB failure) all map to this same shape with distinct `error_code` values, so `api.js` can handle them uniformly.

---

## 26. Concurrency

The backend must prevent two simultaneous requests from incorrectly receiving the same slot.

For the prototype:

- Use **database transactions** around the scheduling/allocation step.
- Perform the capacity check-and-assign for date/shift/slot **inside a transaction**.
- **Lock/recheck** the relevant schedule/capacity rows (e.g., `SELECT ... FOR UPDATE` on the relevant `booking_schedule`/capacity rows, or an equivalent row-level lock) immediately before final assignment, so two concurrent requests cannot both read "capacity available" and both write a conflicting assignment.
- **Commit only after successful allocation**; on conflict, retry the allocation or roll back and return a clear error.

This is intentionally minimal: no distributed locks, no message queues, no external coordination service. A single PostgreSQL instance with transactional row locking is sufficient at this scale.

---

## 27. Consistency Rule

The **backend is the single source of truth** for:

- Crop eligibility
- Season
- Rate
- Procurement time
- Center allocation
- Booking ordering
- Date
- Shift
- Slot
- Token
- Estimated time
- Procurement amount
- Payment status

The frontend only displays backend results. It never computes, infers, or overrides any of the values above.

---

## 28. Project Directory

**Backend**

```
backend/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
│
├── routes/
│   ├── auth.py
│   ├── farmer.py
│   ├── center.py
│   ├── booking.py
│   ├── procurement.py
│   ├── admin.py
│   └── ivr.py
│
├── services/
│   ├── auth_service.py
│   ├── farmer_service.py
│   ├── center_service.py
│   ├── crop_service.py
│   ├── booking_service.py
│   ├── scheduling_service.py
│   ├── procurement_service.py
│   ├── notification_service.py
│   └── ivr_service.py
│
├── models/
│
├── repositories/
│
├── middleware/
│
├── utils/
│
└── tests/
```

**Frontend**

```
frontend/
├── index.html
├── farmer/
├── center/
├── admin/
├── css/
├── js/
└── assets/
```

---

## 29. Local Deployment

The prototype runs entirely locally — no cloud infrastructure.

```
Frontend:  http://localhost:5500
Backend:   http://localhost:5000
Database:  PostgreSQL localhost:5432
```

```
Browser
 ↓
Frontend server (static file server, e.g. Live Server / http.server)
 ↓
Flask API (localhost:5000)
 ↓
PostgreSQL (localhost:5432)
```

Mock SMS/OTP messages appear directly in the backend terminal (the process running `app.py`), not in any external dashboard.

### 29.1 Mermaid — Deployment / Local Architecture

```mermaid
flowchart LR
    subgraph Browser
        A[Frontend Pages]
    end
    subgraph "localhost:5500"
        A
    end
    subgraph "localhost:5000"
        B[Flask Backend]
    end
    subgraph "localhost:5432"
        C[(PostgreSQL)]
    end
    D[Backend Terminal<br/>Mock SMS output]

    A -->|REST/JSON over HTTP| B
    B -->|SQL| C
    B -->|print/log| D
```

---

## 30. Configuration

Environment variables (via `.env`, loaded by `config.py`):

```
DATABASE_URL
JWT_SECRET
FLASK_ENV
CORS_ORIGINS
```

No production secrets are hard-coded anywhere in the codebase. A `.env.example` file is provided with placeholder values so the project is easy to set up locally, e.g.:

```
DATABASE_URL=postgresql://user:password@localhost:5432/procurement_db
JWT_SECRET=replace-with-a-local-dev-secret
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5500
```

---

## 31. Architecture Diagrams — Index

All diagrams referenced by this document (Mermaid, embedded above near their relevant sections):

1. System architecture — Section 3.1
2. Backend layered architecture — Section 5.3
3. Booking flow — Section 8.3
4. Scheduling flow — Section 9.3
5. Procurement flow — Section 31.1 (below)
6. Authentication flow — Section 21.1
7. Database ER diagram — Section 18.1
8. IVR flow — Section 22.1
9. Deployment/local architecture — Section 29.1

### 31.1 Mermaid — Procurement Flow

```mermaid
sequenceDiagram
    participant C as Center (Frontend)
    participant API as Procurement API
    participant PS as Procurement Service
    participant DB as PostgreSQL

    C->>API: POST /api/procurement/arrival (booking_id)
    API->>PS: mark_arrival(booking_id)
    PS->>DB: Update booking status = "arrived"

    C->>API: POST /api/procurement/complete (booking_id, actual_weight)
    API->>PS: complete_procurement(booking_id, actual_weight)
    PS->>DB: Read crop.rate_per_quintal
    PS->>PS: total_amount = actual_weight × rate_per_quintal
    PS->>DB: Insert procurements record (payment_status = "pending")
    PS->>DB: Update booking status = "completed"
    PS-->>API: procurement record
    API-->>C: 200 OK + total_amount
```

### 31.2 Basic layered/data-flow reference diagram

```mermaid
flowchart TD
    A[Farmer] --> B[Frontend]
    B --> C[Flask REST API]
    C --> D[Services]
    D --> E[Repositories]
    E --> F[(PostgreSQL)]
```

---

## 32. Non-Goals

This prototype explicitly does **not** include:

- Real SMS
- Twilio
- Real IVR
- Payment gateway
- Aadhaar API integration
- Government API integration
- Production cloud deployment
- Microservices
- Kubernetes
- Blockchain
- External AI chatbot
- Real-time GPS tracking

These may become future extensions (Section 34) but are out of scope for the current prototype.

---

## 33. Future Extensions

Possible future upgrades (not implemented in the prototype):

- Real SMS gateway
- Real IVR
- Payment integration
- Government procurement integration
- Multi-center scaling
- Advanced analytics
- Multilingual voice interface
- Production-grade authentication
- Cloud deployment
- Audit logging
- Real-time queue tracking

---

## 34. Architectural Principles

1. Backend is the source of truth.
2. Frontend does not implement business logic.
3. One scheduling engine is used by web and IVR.
4. Booking allocation is deterministic.
5. Scheduling uses 7-hour planning capacity.
6. Real center operation is approximately 8 hours.
7. The additional operational bandwidth handles real-world delays.
8. Farmers do not select dates or centers.
9. Rates are maintained centrally.
10. Procurement amount is calculated from actual weight.
11. No real SMS/IVR/payment integration is required for the prototype.
12. Keep the architecture simple and maintainable.

---

## 35. Output Requirements (met by this document)

- Single deliverable: `architecture.md`
- Well structured, technically accurate, and detailed enough to implement from
- Consistent with the PRD and the API contract (see Section 36 for consistency check results)
- Does not duplicate the API contract
- Does not introduce conflicting scheduling rules
- Does not introduce features outside project scope

---

## 36. Architecture Consistency Issues

An internal consistency check was performed against the PRD, the API contract, backend implementation conventions, and the frontend architecture described above, using only the information provided in this project's specification.

**Result: No conflicts identified within the provided specification.**

Notes on scope of this check:

- No `api-contract.md` or PRD document was supplied alongside this request for direct comparison. This architecture was written to be consistent with the endpoint groups, roles, and data model implied by the specification text itself (Sections 2–30), and defers all endpoint-level detail to the project's actual API contract document rather than inventing or duplicating one (Section 23).
- If an existing `PRD.md` or `api-contract.md` in the project defines endpoint names, field names, or role rules that differ from what is listed here (for example, different field names for the `bookings` table, or additional roles), those documents should be reconciled with this file before implementation begins, and any resulting discrepancy should be added to this section rather than silently resolved.
- All scheduling rules in this document (7-hour planning limit vs. 8-hour operational limit, First-Book-First-Serve ordering, same-time and different-crop tie-breakers, single shared scheduling engine for web and IVR) are internally consistent with one another as specified and were not altered or reinterpreted.
