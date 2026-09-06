# Smart Online Procurement Slot Booking System for Farmers
# Development Phases

## 1. Purpose

This document defines the implementation roadmap, development order, dependencies, milestones, testing checkpoints, and definition of done for the project.

The project is a prototype/SIH system using:

- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python Flask
- Database: PostgreSQL
- Development environment: Linux/Fedora + VS Code

Documentation responsibilities:

- `PRD.md` — product requirements and features
- `architecture.md` — system structure and technical architecture
- `api-contract.md` — API endpoints and request/response contract
- `rules.md` — authoritative business rules and constraints
- `phase.md` — implementation roadmap and progress

Do not duplicate the complete contents of those documents here.

---

# 2. Development Principles

1. Build the database and backend foundation before dependent frontend features.
2. Implement business logic before UI polish.
3. Complete and test each logical phase before moving to dependent phases.
4. Keep the prototype simple and practical.
5. Backend is authoritative for business rules.
6. Frontend must consume backend APIs rather than duplicate business logic.
7. Web booking and simulated IVR booking must use the same backend booking/scheduling services.
8. Avoid unnecessary production-level integrations and architecture.
9. Every major phase must have a testing checkpoint.
10. Do not silently change requirements when documentation conflicts are found.

---

# 3. Phase Overview

| Phase | Name | Main Goal |
|---|---|---|
| 0 | Project Preparation | Prepare repository and development environment |
| 1 | PostgreSQL Database | Establish database foundation |
| 2 | Flask Backend Foundation | Establish backend structure |
| 3 | Authentication & User Management | Implement login, OTP and roles |
| 4 | Farmer Module | Implement farmer-side backend functionality |
| 5 | Crop & Center Management | Implement crop and center configuration |
| 6 | Booking System | Implement booking workflow |
| 7 | Scheduling & Slot Allocation | Implement deterministic scheduling |
| 8 | Procurement & Payment | Implement actual procurement and payment calculation |
| 9 | Simulated SMS & IVR | Implement prototype communication flows |
| 10 | Admin Dashboard | Build admin interface |
| 11 | Center Dashboard | Build procurement-center interface |
| 12 | Farmer Frontend | Build farmer-facing interface |
| 13 | Integration & E2E Testing | Verify complete system |
| 14 | Security & Validation | Harden prototype |
| 15 | UI/UX Polish | Improve usability and presentation |
| 16 | Demo Preparation | Prepare final SIH/college demonstration |

---

# 4. Phase 0 — Project Preparation

## Objectives

Prepare the repository and development environment.

## Tasks

- Create/verify project directory structure.
- Configure Git.
- Create Python virtual environment.
- Configure Flask application.
- Configure PostgreSQL connection.
- Establish environment-variable configuration.
- Add `.gitignore`.
- Separate frontend and backend appropriately.
- Establish documentation structure.

## Dependencies

None.

## Completion Criteria

- Project starts locally.
- Flask starts successfully.
- PostgreSQL configuration is ready.
- Repository structure is clear.
- Secrets are not committed.

## Testing Checkpoint

Verify:

- Python environment works.
- Flask starts.
- PostgreSQL is reachable.
- Configuration loads correctly.

---

# 5. Phase 1 — PostgreSQL Database

## Objectives

Create the database foundation according to the approved schema and existing implementation.

## Logical Areas

- Users
- Farmers
- Procurement centers
- Crops
- Farmer-crop relationships
- Center-crop relationships
- Bookings
- Scheduling
- Procurements
- Notifications
- OTP sessions
- IVR sessions

Use the actual approved database design. Do not invent unnecessary tables.

## Rules

- Maintain referential integrity.
- Use appropriate primary keys and foreign keys.
- Add required unique constraints.
- Store required timestamps.
- Store booking quantity in quintals.
- Keep expected booking quantity separate from actual procurement weight.

## Completion Criteria

- Database can be created.
- Tables initialize successfully.
- Relationships work.
- Sample/test data can be inserted.
- Flask can read and write records.

## Testing Checkpoint

Test CRUD operations and database relationships.

---

# 6. Phase 2 — Flask Backend Foundation

## Objectives

Create the backend application structure.

## Tasks

Implement:

- Flask application entry point.
- Configuration management.
- Database connection layer.
- Models/repositories as appropriate.
- Service/business-logic layer.
- API/controller layer.
- Authentication middleware.
- Role-based authorization.
- Common response/error handling.
- Logging.

Follow `architecture.md`.

## Completion Criteria

- Flask application starts.
- Database connection works.
- Basic API endpoint works.
- Common errors are handled consistently.
- Authentication/authorization foundation exists.

---

# 7. Phase 3 — Authentication & User Management

## Objectives

Implement authentication and role management.

## Tasks

Implement:

- OTP generation.
- OTP verification.
- Farmer registration.
- User/session handling.
- Role identification.
- Farmer profile.
- Center profile.
- Admin access.

OTP is simulated.

Do not integrate Twilio or real SMS services.

## Testing

Test:

- Valid OTP.
- Invalid OTP.
- Expired OTP.
- Duplicate registration.
- Unauthorized access.
- Farmer access.
- Center access.
- Admin access.

## Completion Criteria

Each role can authenticate and access only permitted functionality.

---

# 8. Phase 4 — Farmer Module

## Objectives

Implement farmer-side backend functionality.

## Tasks

- Farmer profile.
- Farmer crop selection.
- Eligible crop retrieval.
- Crop updates.
- Farmer booking history.
- Booking details.
- Booking status.
- Token information.

## Important Rules

Refer to `rules.md`.

Key constraints:

- Farmer enters exact quantity.
- Quantity is measured in quintals.
- Farmer cannot select an arbitrary procurement date.
- Farmer cannot arbitrarily select the final procurement center.
- Farmer cannot modify rate or scheduling values.

## Completion Criteria

A farmer can authenticate, manage crops, and view relevant booking information.

---

# 9. Phase 5 — Crop & Center Management

## Objectives

Implement crop and center configuration.

## Tasks

Implement:

- Crop creation.
- Crop update.
- Safe crop removal.
- Crop procurement rate.
- Crop procurement timing.
- Center crop availability.
- Center capacity configuration.
- Center profile.

Admin has system-wide management capability.

Center manages permitted crop/capacity information according to its role.

## Testing

Verify:

- Crops can be configured.
- Centers can support selected crops.
- Invalid crop-center combinations are rejected.
- Rate and timing are retrieved from backend configuration.
- Capacity configuration is persisted correctly.

---

# 10. Phase 6 — Booking System

## Objectives

Implement the core booking workflow.

## Booking Flow

`Farmer → Select Crop(s) → Enter Quantity → Submit Booking → Backend Validation → Scheduling → Booking Confirmation`

## Tasks

- Create booking.
- Validate farmer.
- Validate crops.
- Validate quantities.
- Calculate estimated procurement duration.
- Assign applicable center.
- Generate token.
- Create booking record.
- Return booking result.
- View booking.
- Cancel booking.
- Rebook booking.

## Rules

- Quantity is exact and measured in quintals.
- No weight-range selection.
- Booking timestamp is stored.
- Backend performs validation.
- Backend performs scheduling.
- Farmer cannot select the date.
- Farmer cannot manually force the final center.
- Frontend must not contain a second scheduling algorithm.

## Completion Criteria

A valid booking can be created, scheduled, stored, and retrieved through the backend.

---

# 11. Phase 7 — Scheduling & Slot Allocation

This is a core business-logic phase.

## Objectives

Implement deterministic backend scheduling.

## Core Rules

Follow `rules.md`.

Important concepts include:

- Approximately 8 hours/day operational working period.
- Maximum 7 hours/day for normal planned slot allocation.
- Approximately 1 hour operational buffer.
- First-booked, first-served.
- Booking timestamp is the primary priority.
- Same timestamp + same crop: smaller quantity gets priority.
- Same timestamp + different crops at the same center: compare calculated procurement duration.
- Different centers do not compete for the same center's capacity.
- Farmer cannot choose the date.
- If normal 7-hour planning capacity is full, assign the booking to the next available date.
- Late arrivals may use remaining operational bandwidth if available.
- If no bandwidth remains, rebooking is required.

## Multi-Crop Calculation

For each crop:

`crop duration = crop procurement time × crop quantity`

For multiple crops:

`total estimated duration = sum of all crop durations`

## Tasks

- Implement scheduling service.
- Implement planned-capacity calculation.
- Implement date assignment.
- Implement time-window generation.
- Implement deterministic priority ordering.
- Implement cancellation impact on schedule.
- Implement rebooking.
- Handle late arrivals according to backend rules.

## Testing Checkpoint

Test at minimum:

1. One booking.
2. Multiple bookings.
3. Different booking timestamps.
4. Same timestamp + same crop.
5. Same timestamp + different crops.
6. Different centers.
7. Exactly 7 hours of planned capacity.
8. Booking that would exceed 7 hours.
9. Cancellation freeing capacity.
10. Rebooking.
11. Late arrival with available operational bandwidth.
12. Late arrival without available operational bandwidth.
13. Multiple-crop booking.

Scheduling must be deterministic and reproducible.

---

# 12. Phase 8 — Procurement & Payment

## Objectives

Implement actual procurement processing.

## Procurement Flow

`Scheduled → Arrived → Weighed → Completed`

## Tasks

- Record farmer arrival.
- Record actual weight.
- Validate actual weight.
- Complete procurement.
- Store procurement record.
- Calculate payment amount.
- Maintain payment status.

## Payment Formula

`Payment Amount = Actual Weight in Quintals × Rate per Quintal`

Payment is only simulated/recorded.

No real payment gateway is required.

## Testing

Verify:

- Actual weight is separate from booking quantity.
- Correct rate is used.
- Payment amount is correct.
- Invalid procurement state transitions are rejected.
- Payment status is stored correctly.

---

# 13. Phase 9 — Simulated SMS & IVR

## Objectives

Implement communication features without external telecom services.

## SMS Rules

When an SMS would normally be sent:

1. Generate the message in the backend.
2. Print/log the message in the backend terminal.
3. Return an appropriate application result.
4. UI may state that an SMS was generated.
5. Never claim that an actual SMS was delivered.

Do not use Twilio.

## IVR Flow

Simulate:

`Start → Language → Farmer → Crop → Quantity → Booking`

Cancellation/rebooking:

- `1` → Cancel
- `2` → Rebook

The IVR must call the same backend booking and scheduling services as web booking.

Do not duplicate business logic.

## Testing

Verify web and IVR flows produce consistent booking/scheduling behavior.

---

# 14. Phase 10 — Admin Dashboard

## Objectives

Build the admin interface.

## Features

Admin should be able to manage/monitor:

- Farmers
- Procurement centers
- Crops
- Crop configuration
- Center crop availability
- Capacity
- Bookings
- Scheduling
- Procurement
- Payment status
- Notifications
- System statistics

Use backend APIs.

Do not put authoritative business rules in frontend JavaScript.

---

# 15. Phase 11 — Procurement Center Dashboard

## Objectives

Build the center-side interface.

## Features

- Center profile.
- Supported crops.
- Capacity configuration.
- Daily schedule.
- Assigned farmers.
- Booking details.
- Farmer arrival.
- Actual weighing.
- Procurement completion.
- Procurement/payment status.

Center users must only access their authorized center data.

---

# 16. Phase 12 — Farmer Frontend

## Objectives

Build the farmer-facing web interface.

## Features

- Login/OTP.
- Registration.
- Profile.
- Crop selection.
- Exact quantity entry.
- Booking.
- Booking confirmation.
- Assigned date/time.
- Token.
- Booking history.
- Cancellation.
- Rebooking.
- Procurement status.
- Payment status.
- Help/chatbot.

The UI must clearly communicate:

- Assigned schedule.
- Booking status.
- Required farmer action.
- SMS generation status.
- Rebooking requirement when applicable.

Do not provide controls for values the farmer is not allowed to modify.

---

# 17. Phase 13 — Integration & End-to-End Testing

## Objectives

Verify that the complete system works together.

## Farmer Workflow

`Register → Login → Select Crops → Enter Quantity → Book → Receive Schedule → View Status`

## Center Workflow

`Login → View Schedule → Farmer Arrives → Weigh → Complete Procurement`

## Payment Workflow

`Procurement Complete → Calculate Amount → Update Payment Status`

## Cancellation Workflow

`Booking → Cancel → Schedule/Capacity Updated`

## Rebooking Workflow

`Booking → Rebook → New Scheduling Decision`

## IVR Workflow

`Start IVR → Identify Farmer → Select Crop → Enter Quantity → Booking`

## Testing Types

- Unit testing
- API testing
- Database testing
- Integration testing
- Role/permission testing
- Scheduling testing
- Validation testing
- Error handling testing
- End-to-end testing

## Completion Criteria

The major workflows work from frontend through Flask to PostgreSQL and back.

---

# 18. Phase 14 — Security, Validation & Error Handling

## Objectives

Harden the prototype before demonstration.

Verify:

- Authentication.
- Authorization.
- Input validation.
- Safe database access.
- Session/token handling.
- Role isolation.
- Invalid-request handling.
- Duplicate booking protection.
- Concurrent booking/capacity protection.
- Database transaction consistency.
- Safe configuration/secrets handling.

Do not introduce unnecessary production-grade complexity.

---

# 19. Phase 15 — UI/UX & Final Polish

## Objectives

Improve usability after functionality is stable.

## Tasks

- Responsive layout.
- Mobile-friendly farmer UI.
- Clear navigation.
- Loading indicators.
- Error messages.
- Success messages.
- Empty states.
- Booking status indicators.
- Schedule visualization.
- Dashboard cards/tables.
- Accessibility basics.
- Consistent styling.

Do not redesign core business logic during this phase.

---

# 20. Phase 16 — Deployment/Demo Preparation

## Objectives

Prepare the project for SIH/college demonstration.

## Tasks

- Verify clean installation.
- Verify database initialization.
- Verify environment configuration.
- Add sample/demo data.
- Test complete demo workflow.
- Prepare screenshots.
- Verify documentation.
- Prepare demo credentials if appropriate.
- Verify frontend/backend startup commands.
- Verify no secrets are committed.
- Verify all major features work locally.

## Recommended Demo Flow

1. Farmer registration/login.
2. Crop selection.
3. Quantity entry.
4. Booking.
5. Backend scheduling.
6. Assigned date/time.
7. Token.
8. Center dashboard.
9. Farmer arrival.
10. Actual weighing.
11. Procurement completion.
12. Payment calculation/status.
13. Simulated SMS output.
14. Cancellation/rebooking.
15. Admin management.

---

# 21. Phase Dependencies

Primary dependency chain:

`Project Setup → Database → Backend Foundation → Authentication → Farmer/Crop/Center Modules → Booking → Scheduling → Procurement → Communication → Dashboards → Integration Testing → Final Polish`

More specifically:

- Phase 1 depends on Phase 0.
- Phase 2 depends on Phase 1.
- Phase 3 depends on Phase 2.
- Phases 4 and 5 depend on Phase 3.
- Phase 6 depends on Phases 4 and 5.
- Phase 7 depends on Phase 6.
- Phase 8 depends on Phase 7.
- Phase 9 depends on the relevant backend services from Phases 6–8.
- Phases 10–12 depend on their corresponding backend functionality.
- Phase 13 depends on the major frontend/backend/database workflows being available.
- Phase 14 should be performed before final demonstration.
- Phase 15 should be performed after core functionality is stable.
- Phase 16 is the final preparation phase.

---

# 22. Definition of Done

A phase is complete only when:

- Required implementation is finished.
- Relevant APIs work.
- Database operations work where applicable.
- Validation works.
- Role permissions work where applicable.
- Relevant tests/checks pass.
- No known blocking error remains.
- Documentation remains consistent.

Code existing in the repository does not by itself mean the phase is complete.

---

# 23. Progress Tracking

Update this section during development.

| Phase | Status | Dependencies | Blocking Issues | Test Status |
|---|---|---|---|---|
| 0 — Project Preparation | Not Started | None | — | Not Tested |
| 1 — PostgreSQL Database | Not Started | Phase 0 | — | Not Tested |
| 2 — Flask Backend Foundation | Not Started | Phase 1 | — | Not Tested |
| 3 — Authentication & User Management | Not Started | Phase 2 | — | Not Tested |
| 4 — Farmer Module | Not Started | Phase 3 | — | Not Tested |
| 5 — Crop & Center Management | Not Started | Phase 3 | — | Not Tested |
| 6 — Booking System | Not Started | Phases 4–5 | — | Not Tested |
| 7 — Scheduling & Slot Allocation | Not Started | Phase 6 | — | Not Tested |
| 8 — Procurement & Payment | Not Started | Phase 7 | — | Not Tested |
| 9 — Simulated SMS & IVR | Not Started | Phases 6–8 | — | Not Tested |
| 10 — Admin Dashboard | Not Started | Backend modules | — | Not Tested |
| 11 — Center Dashboard | Not Started | Center backend | — | Not Tested |
| 12 — Farmer Frontend | Not Started | Farmer backend | — | Not Tested |
| 13 — Integration & E2E Testing | Not Started | Phases 6–12 | — | Not Tested |
| 14 — Security & Validation | Not Started | Core functionality | — | Not Tested |
| 15 — UI/UX Polish | Not Started | Core functionality | — | Not Tested |
| 16 — Demo Preparation | Not Started | All required phases | — | Not Tested |

Allowed status values:

- Not Started
- In Progress
- Blocked
- Complete

Allowed test status values:

- Not Tested
- Partial
- Passed
- Failed

---

# 24. Documentation Consistency Check

Before starting or completing a phase, check the relevant requirements against:

- `PRD.md`
- `rules.md`
- `architecture.md`
- `api-contract.md`
- Existing backend implementation
- Existing frontend implementation

If a conflict is found, do not silently change the implementation.

Record it under:

## Phase Planning Issues

For each issue document:

- Conflict
- Affected phase
- Affected component
- Recommended resolution
- Current decision/status

---

# 25. Project Completion Criteria

The project is considered ready for final demonstration when:

- PostgreSQL database works.
- Flask backend works.
- Authentication works.
- Farmer workflow works.
- Crop and center management works.
- Booking works.
- Backend scheduling works according to `rules.md`.
- 7-hour normal planning limit is enforced.
- Next available date is assigned when required.
- Procurement workflow works.
- Actual weight and payment calculation work.
- SMS simulation works.
- IVR simulation works.
- Admin dashboard works.
- Center dashboard works.
- Farmer dashboard works.
- Role permissions work.
- End-to-end testing passes.
- Major blocking errors are resolved.
- Documentation is consistent.
- Demo can be completed locally from a clean setup.
