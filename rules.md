# rules.md
## Smart Online Procurement Slot Booking System for Farmers

**Purpose:** This document defines the authoritative business rules, constraints, validation rules, scheduling rules, role permissions, and system behavior for the project. It contains business/system rules only — it does not duplicate the API contract, database schema, or architecture documentation. Where implementation detail is needed, see `PRD.md`, `architecture.md`, and `api-contract.md`.

---

## 1. Core System Rules

1. The system is a prototype, not a production government platform.
2. Stack: Frontend (HTML/CSS/JavaScript), Backend (Python Flask), Database (PostgreSQL).
3. Backend business rules are authoritative.
4. The frontend must not independently implement or override business rules.
5. All booking, scheduling, capacity, procurement, payment, and permission decisions must be validated by the backend.
6. Unnecessary production-level complexity must not be introduced.

---

## 2. User Roles

Three roles: **Farmer**, **Procurement Center**, **Admin**. Each role may only perform actions permitted to that role.

### Farmer — can
- Register/login
- Maintain profile information
- Select/update eligible crops
- Enter exact crop quantity during booking
- View bookings
- View assigned procurement date/time
- View token/status
- Cancel/rebook according to system rules
- View procurement and payment status
- Use the help/chatbot feature
- Use the simulated toll-free/IVR booking flow

### Farmer — cannot
- Select an arbitrary procurement center
- Select an arbitrary procurement date
- Manually assign their own slot
- Change the procurement rate
- Change the system-generated token
- Override capacity or scheduling decisions
- Directly modify procurement records

### Procurement Center — can
- Manage crops handled by that center
- Configure/update procurement capacity
- View assigned farmers/bookings
- View its schedule
- Process farmer arrival
- Record actual crop weight
- Complete procurement
- Update procurement-related status

### Procurement Center — cannot
- Modify bookings belonging to another center
- Change system-wide farmer data without permission
- Override admin-only configuration
- Manually bypass booking/scheduling rules without an explicitly defined administrative action

### Admin — can
- Manage farmers
- Manage procurement centers
- Add/update/remove crops
- Manage center crop availability
- Modify relevant configuration data
- View/manage bookings
- View/manage procurement records
- Monitor system status
- Correct/manage configuration and operational data when required

Admin actions must still maintain database consistency.

---

## 3. Farmer Registration Rules

1. A farmer must provide the required registration information.
2. Each farmer must have a unique farmer/user identifier.
3. Example farmer ID format: `FA000125`.
4. Duplicate identifiers must not be accepted.
5. Required fields must be validated by the backend.
6. Invalid or incomplete registration data must be rejected.

---

## 4. Authentication / OTP Rules

1. OTP authentication is simulated for the prototype.
2. OTP must be generated and validated by the backend.
3. OTP must not be hardcoded into frontend logic.
4. Invalid OTP must be rejected.
5. Expired OTP must be rejected.
6. OTP verification must establish the appropriate authenticated user/session.
7. No integration with Twilio or any real SMS provider.

---

## 5. Crop Rules

1. The system supports multiple crops.
2. A farmer may select multiple eligible crops.
3. A procurement center may support multiple crops.
4. Only crops supported by the assigned procurement center can be booked there.
5. Crop details are managed by the admin.
6. Center-specific crop availability can be managed by the center/admin according to permissions.
7. Each crop can have its own procurement timing.
8. Each crop can have its own procurement rate per quintal.
9. Crop rate and timing must come from backend/database configuration.
10. Farmers must not manually modify crop rate or procurement timing.

---

## 6. Quantity Rules

1. Farmer enters an exact quantity.
2. Quantity is measured in **quintals**.
3. Example values: 5, 10, 30, 500 quintals.
4. No weight-range selection.
5. No quantity ranges for booking.
6. Quantity must be greater than zero.
7. Quantity must be validated by the backend.
8. The booking must store the requested quantity.

---

## 7. Procurement Time Rules

Each crop has a configured procurement time.

Single crop:
```
Estimated Time = Crop Procurement Time × Quantity
```
If stored per quintal:
```
Estimated Time = time_per_quintal × quantity_in_quintals
```
Multiple crops:
```
Total Estimated Time = Σ (crop procurement time × crop quantity)
```
Example: Crop A = a, Crop B = b, Crop C = c → `Total Time = a + b + c`.

The backend performs this calculation. The frontend may display the result but must not independently determine the authoritative scheduling result.

---

## 8. Procurement Center Working-Time Rules

Two distinct concepts:

- **Operational Working Period:** approximately **8 hours/day** — the practical, real-world working period of a center.
- **Normal Slot-Planning Capacity:** maximum **7 hours/day** — the limit used for normal slot allocation.

The remaining ~1 hour is operational bandwidth/buffer for late arrivals, delays, unexpected operational issues, and small scheduling deviations. Normal bookings must never be allocated beyond the 7-hour planning capacity.

---

## 9. Slot Allocation Rules

Slot allocation is controlled by the backend. The farmer does not select the date and does not manually choose the procurement center. The backend assigns the applicable date, center, and time.

**Primary ordering rule:** First-booked, first-served. The booking timestamp is the primary ordering factor — an earlier valid booking gets earlier scheduling priority.

**Same-timestamp rule, same crop:** Priority goes to the smaller quantity.
- Example: Farmer A (10 quintals) vs. Farmer B (30 quintals), equal timestamps, same crop → Farmer A gets priority.
- If quantity is also equal, use a deterministic secondary ordering such as user/booking ID.

**Different crops:** Compare calculated procurement durations. For the same center: `duration = crop procurement time × quantity`; the calculated duration is used to resolve scheduling order. If the bookings belong to different centers, there is no scheduling conflict between them.

---

## 10. Capacity Rules

The backend must calculate the total planned procurement time for each center and date. Normal planned bookings must not exceed **7 hours/day**.

If the next booking would cause the planned schedule to exceed 7 hours:
- Do not allocate that booking into the same day's normal schedule.
- Assign the booking to the next available date.
- The farmer cannot choose the alternative date manually.

Example: current planned time 6h40m + new booking 40m = 7h20m → exceeds the limit → the booking is assigned to the next available date, not placed in that day's normal planned schedule.

---

## 11. Date Assignment Rules

1. Farmer cannot select the procurement date.
2. Backend determines the date.
3. The system first attempts to allocate the booking under current scheduling rules.
4. If the current day's 7-hour planning capacity is full, the booking moves to the next available date.
5. Continue to the next available date until sufficient capacity exists.
6. The assigned date must be stored in the booking/schedule record.
7. The assigned date must be visible to the farmer.

---

## 12. Time Assignment Rules

1. Time windows are generated by the backend.
2. The first scheduled booking starts from the configured center operating start time.
3. Subsequent bookings are placed according to their calculated procurement durations.
4. Scheduling must not overlap normal planned booking windows.
5. The total normal planned schedule must remain within the 7-hour planning limit.
6. The remaining ~1-hour operational period may be used for late arrivals or operational delays.
7. The frontend must display the backend-assigned time rather than inventing a time.

---

## 13. Late Arrival Rules

If a farmer does not arrive during the assigned window:

1. The center checks whether operational bandwidth is still available.
2. If sufficient operational bandwidth remains, the center may process the farmer.
3. If no operational bandwidth remains:
   - The farmer cannot force the booking into the schedule.
   - The farmer must use the cancellation/rebooking process.
4. The backend determines the resulting booking status.

The frontend must only display the backend result.

---

## 14. Cancellation Rules

1. A farmer may cancel an eligible booking through the supported cancellation flow.
2. After cancellation, the booking status must change appropriately.
3. A cancelled booking must not continue occupying normal scheduling capacity.
4. The system must preserve the booking record for tracking/audit purposes.
5. A cancelled booking must not be treated as an active booking.

---

## 15. Rebooking Rules

1. Rebooking is used when a farmer needs another procurement opportunity.
2. A rebooking request must be processed by the backend.
3. The new booking must go through the normal scheduling and capacity rules.
4. The farmer cannot manually force a specific date or time.
5. The rebooking must receive a new applicable schedule/token according to the system rules.

---

## 16. Toll-Free / IVR Simulation Rules

The toll-free service is simulated — no real telecom integration.

Flow: start call → select language → identify farmer → select crop → enter quantity → submit booking → receive booking/scheduling result.

Cancellation/rebooking via IVR:
- Press "1" → Cancel
- Press "2" → Rebook

The IVR must use the same backend business rules as web booking. No separate scheduling algorithm may be created for IVR.

---

## 17. Notification / SMS Rules

1. SMS is simulated. No Twilio or external SMS provider.
2. When an SMS would normally be sent:
   - Backend generates the SMS message.
   - The message is printed/logged in the backend terminal.
   - UI may display a message such as "SMS generated successfully."
3. The system must not claim that an actual SMS was delivered.
4. The same rule applies to OTP and booking-related notifications.

---

## 18. Token Rules

1. Booking tokens are generated by the backend.
2. Token must be unique for the applicable booking context.
3. Farmer cannot manually choose or modify the token.
4. Token must be associated with the booking.
5. Token/status must be visible to the appropriate users.

---

## 19. Procurement Rules

Procurement is separate from booking. A booking represents the scheduled procurement request; a procurement record represents the actual procurement process.

Typical flow: **Booked → Scheduled → Arrived → Weighed → Procured/Completed.**

Exact status names must remain consistent with the backend implementation.

---

## 20. Actual Weight Rules

1. Farmer enters expected quantity during booking.
2. Actual procurement weight is recorded by the procurement center.
3. Payment calculation must use actual procured weight, not merely the originally requested quantity.
4. Actual weight must be stored separately from expected booking quantity.
5. Actual weight must be validated.

---

## 21. Rate Rules

1. Rate is calculated per quintal.
2. Rate comes from crop/system configuration.
3. Farmer cannot modify the rate.
4. Procurement center should not arbitrarily modify the rate unless backend/admin permissions explicitly allow configuration changes.
5. The rate used for a completed procurement should be traceable.

---

## 22. Payment Rules

1. Payment in this prototype is only a recorded/calculated status. No real payment gateway is required.
2. Amount owed:
   ```
   Payment Amount = Actual Weight (quintals) × Rate per Quintal
   ```
   Example: 20 quintals × ₹2,000/quintal = ₹40,000.
3. Statuses may include: Pending, Processed, Paid.
4. No real banking/payment integration unless explicitly requested later.

---

## 23. Data Integrity Rules

1. Foreign-key relationships must remain valid.
2. A booking must reference a valid farmer.
3. A booking must reference valid crop information.
4. A scheduled booking must have a valid assigned center.
5. Procurement must reference a valid booking.
6. Payment/procurement calculations must use stored authoritative values.
7. Invalid references must be rejected.
8. Deleting data that would break existing records must be prevented or handled safely.

---

## 24. Concurrency Rules

1. The backend must prevent two simultaneous booking requests from incorrectly exceeding the same center's 7-hour planning capacity.
2. Capacity validation and schedule assignment should be performed atomically where required.
3. Frontend validation alone must never be relied upon.

---

## 25. Validation Rules

Backend validation is mandatory for: authentication, registration, crop selection, quantity, booking, cancellation, rebooking, capacity, scheduling, procurement, actual weight, payment calculation, and role permissions.

Frontend validation exists for user experience only. Backend validation is authoritative.

---

## 26. Error Handling Rules

The system must return clear errors for situations such as: invalid login/OTP, missing required data, invalid farmer, invalid crop, unsupported crop at center, invalid quantity, booking not found, unauthorized action, booking already cancelled, invalid rebooking, no available capacity, invalid procurement state, and invalid actual weight.

Errors must not silently modify data.

---

## 27. Role-Based Access Rules

Every protected backend operation must verify the authenticated user's role.

Examples:
- Farmer cannot access another farmer's private booking data.
- Farmer cannot access admin configuration.
- Center cannot modify another center's operational data.
- Center cannot perform admin-only operations.
- Admin can access system-wide management functions.

Hiding frontend buttons must never be relied upon as the security mechanism.

---

## 28. Frontend Rules

1. Frontend must display backend results.
2. Frontend must not duplicate scheduling algorithms.
3. Frontend must not calculate authoritative capacity.
4. Frontend must not assign dates.
5. Frontend must not generate authoritative tokens.
6. Frontend must not determine final payment.
7. Frontend must not bypass role permissions.
8. Frontend should provide clear validation messages and status indicators.

---

## 29. Backend Rules

1. Backend is the source of truth for business logic.
2. Scheduling must happen on the backend.
3. Capacity must be checked on the backend.
4. Payment calculation must be validated on the backend.
5. Authentication/authorization must be enforced on the backend.
6. Database transactions should be used where necessary to maintain consistency.
7. IVR and web booking must use the same booking service/business logic.

---

## 30. Prototype Scope Rules

Do **not** implement unless explicitly requested:

- Real SMS gateway
- Twilio
- Real toll-free telecom service
- Real IVR telecom integration
- Real payment gateway
- Aadhaar integration
- Government API integration
- Bank API integration
- Advanced AI scheduling
- Machine-learning-based demand prediction
- Complex optimization algorithms
- Blockchain
- Production-grade distributed architecture

The goal is a clean, functional academic/SIH prototype.

---

## 31. Rule Priority

When conflicting requirements appear, follow this priority:

1. Explicit latest project requirement
2. `rules.md`
3. `PRD.md`
4. `architecture.md`
5. `api-contract.md`
6. Existing implementation details

If an existing backend implementation conflicts with the documented rules, do not silently change the backend. Clearly identify the inconsistency and request/update the relevant documentation or implementation deliberately.

---

## 32. Consistency Requirements

Before finalizing, this document was checked against:

- Booking rules being consistent with the PRD
- Scheduling rules being consistent with the architecture
- API behavior not being contradicted
- Quantity being consistently measured in quintals
- Rate being consistently per quintal
- No weight-range option being introduced
- Farmer not selecting the date
- Farmer not arbitrarily selecting the center
- The 7-hour planning capacity not being confused with the ~8-hour operational period
- Late-arrival behavior being consistent
- Web and IVR using the same booking rules
- SMS remaining simulated
- Payment remaining prototype-only
- No duplicated API contract being added

See Section 33 for the result of this check.

---

## 33. Documentation Consistency Issues

No conflicts were identified within the rules as specified in this request. All rules above are internally consistent (quantity in quintals throughout, rate per quintal throughout, the 7-hour planning limit vs. ~8-hour operational period kept distinct in every section that references it, farmer never selects date/center, web and IVR share one scheduling engine, SMS/payment remain simulated/prototype-only, and no API contract, schema, or endpoint content has been duplicated here).

This document was not cross-checked against the literal contents of `PRD.md`, `architecture.md`, or `api-contract.md`, as those files were not supplied for comparison. If those documents exist in the project and define conflicting details (e.g., different role permissions, a different tie-breaker order, or different status names for the procurement flow), that conflict should be recorded here explicitly rather than silently resolved, once those files are available for review.
