# Smart Online Procurement Slot Booking System
# Design System & UI/UX Specification

## 1. Purpose

This document defines the visual design system and UI/UX rules for the project.

The design must be based on the **existing HTML, CSS, and JavaScript implementation in the GitHub repository**:

- `home.html`
- `home.css`
- `home.js`
- `index.html`
- `style.css`
- `script.js`

The existing FASAL visual language is the source of truth for the application's appearance.

### Design Rule

When new pages, dashboards, forms, cards, tables, modals, booking screens, or components are created, they must look like they belong to the existing FASAL website.

Do **not** introduce a completely different theme, color palette, typography system, or visual style.

The design may be extended for new functionality, but the existing visual identity must remain recognizable.

---

# 2. Current Design Identity

The existing website uses a:

- Natural agricultural aesthetic
- Clean editorial layout
- Warm cream/paper backgrounds
- Green agricultural accents
- Harvest/orange call-to-action colors
- Brown/soil typography
- Soft borders
- Rounded cards
- Subtle shadows
- Minimal, spacious layouts
- Responsive design
- Simple SVG agricultural illustrations

The overall feeling should be:

**Natural + trustworthy + modern + simple + farmer-friendly**

Avoid:

- Neon colors
- Heavy gradients
- Glassmorphism-heavy interfaces
- Excessive shadows
- Overly futuristic dashboards
- Dark-tech/SaaS visual language
- Excessive animations
- Unnecessary decorative elements

---

# 3. Brand

## Brand Name

Primary brand:

**FASAL**

Use the existing FASAL wordmark style.

The existing logo uses a simple leaf/plant SVG combined with the FASAL text.

When a reusable logo component is needed, preserve:

- Leaf/plant symbol
- Agricultural identity
- Brown/green/orange color relationship
- Fraunces-style display typography

Do not replace the FASAL identity with a generic agricultural logo.

---

# 4. Color System

Use the existing CSS variables as the primary design tokens.

## Main Website Palette

```css
--harvest: #C97A2B;
--harvest-dark: #A5601C;
--wheat: #E8B54D;
--soil: #4A2E1E;
--sprout: #5C8A3A;
--sky-top: #EFF3E6;
--sky-bottom: #E1E9D4;
--ink: #2A2E22;
--muted: #6E7460;
--line: #DCD9C6;
--paper: #FBF9F2;
```

## Registration/Form Palette

The registration page currently uses:

```css
--soil: #3B2C1F;
--leaf-dark: #2C4A22;
--leaf: #4E7A38;
--leaf-light: #8CAE5C;
--wheat: #D9A441;
--cream: #F7F2E7;
--ink: #26301F;
--muted: #6E7A5E;
--line: #DCD4BF;
--error: #A8442C;
```

Use these existing values when extending the registration/form visual language.

## Color Usage

### Harvest Orange

Use for:

- Primary CTA
- Registration buttons
- Important action highlights
- Selected language indication where appropriate

### Sprout Green

Use for:

- Agricultural feature icons
- Positive states
- Secondary agricultural accents
- Focus states
- Success states

### Soil Brown

Use for:

- Main headings
- Brand identity
- Strong text
- Dark CTA strips
- Agricultural visual grounding

### Wheat

Use for:

- Warm accent
- Decorative highlights
- Sun/harvest illustrations
- Secondary emphasis

### Paper/Cream

Use for:

- Main backgrounds
- Cards
- Forms
- Content surfaces

### Muted

Use for:

- Supporting text
- Descriptions
- Hints
- Metadata

### Error

Use the existing error red for:

- Invalid form fields
- Validation messages
- Failed operations

Do not introduce arbitrary colors without a clear design reason.

---

# 5. Typography

The existing project uses Google Fonts:

- **Fraunces** — display/headings/brand
- **Inter** — body/UI text

## Display Font

Use Fraunces for:

- FASAL brand
- Hero headings
- Section headings
- Major page titles
- Important agricultural/editorial headings

## Body Font

Use Inter for:

- Body text
- Labels
- Buttons
- Navigation
- Tables
- Form controls
- Dashboard data
- Status labels

## Typography Characteristics

Headings should be:

- Strong
- Warm
- Editorial
- Not excessively bold
- Spacious

Body text should be:

- Clear
- Readable
- Moderate in size
- High contrast
- Comfortable for mobile users

Avoid introducing another font family.

---

# 6. Layout System

The current home page uses a maximum content width of approximately:

`1180px`

Use a similar max-width for major desktop layouts.

Typical structure:

```text
Full-width section
    ↓
Centered content container
    ↓
Maximum width ~1180px
    ↓
Responsive padding
```

Use generous whitespace.

Do not make the interface feel crowded.

---

# 7. Header / Navigation

The existing homepage uses a fixed header.

Characteristics:

- Fixed to top
- Height approximately 68px
- Paper/cream translucent background
- Subtle backdrop blur
- Bottom border
- FASAL brand on the left
- Navigation on the right
- Registration CTA
- Language selector
- Mobile hamburger menu

Desktop navigation includes:

- Home
- About
- Contact
- Help
- Registration
- Language selector

For authenticated application pages, the navigation may be adapted to:

- Dashboard
- Bookings
- Profile
- Help
- Logout

However, the visual styling must remain consistent with the existing FASAL header.

---

# 8. Mobile Navigation

The existing project switches to a hamburger navigation around the tablet/mobile breakpoint.

Mobile navigation should:

- Expand vertically
- Use the paper background
- Preserve borders
- Keep links large enough for touch
- Provide the registration/action button
- Keep language selection accessible

Do not replace the existing mobile behavior with a completely different navigation style.

---

# 9. Responsive Design

The application must be responsive.

Existing design behavior includes:

- Desktop multi-column hero
- Mobile single-column hero
- Desktop navigation becoming hamburger navigation
- Three-column feature cards becoming one column
- Responsive form width
- Responsive padding

Recommended breakpoints should follow the existing CSS where practical rather than introducing many arbitrary breakpoints.

The interface must work well on:

- Desktop
- Laptop
- Tablet
- Android/mobile browsers

Farmer-facing pages should prioritize mobile usability.

---

# 10. Buttons

Buttons should inherit the existing visual language.

## Primary Button

Use the harvest orange:

`#C97A2B`

Characteristics:

- White text
- Medium/bold Inter
- Rounded corners around 7–8px
- Comfortable horizontal/vertical padding
- Subtle hover darkening

Example visual role:

- Register
- Book slot
- Confirm booking
- Submit
- Continue

## Secondary Button

Use a light/ghost style:

- Transparent or paper background
- Soil text
- Thin line border
- Green hover state

## Success Button/Action

May use the existing green palette where appropriate.

## Danger Button

Use the existing error color only for destructive operations such as:

- Cancel booking
- Delete
- Remove

Avoid making every button colorful.

---

# 11. Cards

The existing design uses clean cards with:

- Cream/paper or white surface
- Thin border
- Rounded corners
- Subtle shadow when needed
- Comfortable internal padding

Typical radius:

`8px – 14px`

Use cards for:

- Booking summary
- Farmer profile
- Schedule
- Crop information
- Procurement information
- Dashboard statistics
- Notifications
- Forms

Do not overuse cards. Related information can remain in simple sections.

---

# 12. Forms

The registration page establishes the form language.

Form controls should use:

- White input background
- Thin light border
- Rounded corners
- Inter font
- Clear labels
- Supporting hints
- Green focus ring
- Error border for invalid fields

Existing input style is approximately:

- 12px vertical padding
- 14px horizontal padding
- 8px border radius

Maintain similar sizing.

## Form Labels

Labels should be:

- Clear
- Medium weight
- Above the field
- Short and descriptive

## Hints

Use muted text below inputs for additional explanation.

## Errors

Errors should:

- Be directly associated with the field
- Use the existing error color
- Be concise
- Explain what needs correction

Do not rely only on red color; use text.

---

# 13. Registration Design

The existing registration page is a multi-step card.

Current visual flow:

```text
Step 1
Name
Aadhaar
Phone
Get OTP
      ↓
Step 2
OTP
Verify
      ↓
Step 3
Password
FARM ID
Create account
      ↓
Step 4
Success
FARM ID
Continue
```

Future backend integration should preserve the same visual flow.

The frontend functionality may change from demo behavior to API-backed behavior, but the visual design should remain consistent.

---

# 14. Hero Section

The homepage currently uses:

- Soft green/cream background
- Large Fraunces heading
- Small green kicker
- Supporting paragraph
- Primary CTA
- Ghost secondary CTA
- Agricultural SVG artwork
- Field-shaped decorative band

New public-facing landing sections should maintain this agricultural visual language.

Do not replace the existing illustration style with stock photos unless specifically requested.

---

# 15. Agricultural Illustrations

The existing website uses lightweight SVG illustrations.

Preferred visual elements:

- Leaves
- Crops
- Fields
- Sun
- Soil
- Wheat
- Agricultural rows

Illustrations should be:

- Simple
- Flat
- Minimal
- Warm
- Consistent with the current SVG style

Avoid highly detailed photorealistic illustrations for normal UI decoration.

---

# 16. Feature Sections

The current homepage uses three feature cards.

Each feature includes:

- Small icon container
- Icon/SVG
- Heading
- Description

The feature cards use:

- White surface
- Light border
- Rounded corners
- Green icon background
- Muted supporting text

This component pattern can be reused for:

- Procurement benefits
- Booking steps
- Dashboard features
- Help information

---

# 17. Dashboard Design

The existing public homepage is not yet a full dashboard, so dashboard pages should extend the same design language rather than inventing a new theme.

Recommended dashboard structure:

```text
FASAL Header
    ↓
Page title + short description
    ↓
Summary/stat cards
    ↓
Main content section
    ↓
Tables/cards/forms
```

Use:

- Cream/paper background
- White/cream cards
- Green/orange accents
- Fraunces for major headings
- Inter for data
- Thin borders
- Moderate corner radius

---

# 18. Farmer Dashboard

The farmer dashboard should prioritize the most important information first.

Suggested visual hierarchy:

### Top

- Welcome
- Farmer ID
- Current booking status

### Main

- Next procurement slot
- Date
- Time
- Procurement center
- Token
- Crop
- Quantity

### Secondary

- Booking history
- Procurement status
- Payment status
- Notifications
- Help/chatbot

The next assigned slot should be visually prominent.

Do not allow the UI to imply that the farmer can manually choose a date or override scheduling.

---

# 19. Booking Interface

The booking screen should follow the registration form style.

Suggested structure:

```text
Page heading
Short explanation

Crop selection
Quantity in quintals

Selected crops
Estimated procurement duration

Booking summary

Confirm booking
```

Important:

- Quantity must be entered as an exact value in quintals.
- Do not create a weight-range selector.
- Date must not be presented as a user-selectable field.
- Final scheduling result comes from the backend.

After successful booking, show:

- Booking ID
- Assigned center
- Assigned date
- Assigned time/window
- Token
- Booking status

---

# 20. Schedule Display

Schedule information should be easy to scan.

Use a clean schedule card or table.

Suggested columns:

- Token
- Farmer
- Crop
- Quantity
- Estimated duration
- Assigned time
- Status

For mobile:

Convert dense tables into stacked cards or horizontally scrollable tables.

Do not make the schedule visually complicated.

---

# 21. Status Design

Use clear status badges.

Suggested semantic mapping:

### Pending

Neutral/muted style.

### Scheduled

Green/leaf style.

### Arrived

Wheat/orange accent.

### Processing

Warm accent.

### Completed

Green.

### Cancelled

Error/neutral style.

### Rebooking Required

Harvest/error emphasis.

Do not use random colors.

Status should include text, not color alone.

---

# 22. Admin Dashboard Design

The admin interface should visually match the farmer interface.

Possible sections:

- Overview
- Farmers
- Procurement Centers
- Crops
- Bookings
- Scheduling
- Procurement
- Payments
- Notifications
- Configuration

Admin can have denser tables than the farmer interface, but should still use:

- Same color tokens
- Same typography
- Same border/radius system
- Same buttons
- Same cards

Avoid creating a completely separate admin theme.

---

# 23. Procurement Center Dashboard

The center interface should prioritize daily operations.

Suggested hierarchy:

```text
Center name
Today's capacity / planned usage

Today's schedule

Upcoming farmers

Arrival actions

Weighing

Procurement completion
```

Operational actions should be visually clear but not oversized.

Use the same FASAL agricultural visual identity.

---

# 24. Tables

Tables should use:

- White/cream background
- Light borders
- Inter typography
- Clear headers
- Moderate row spacing
- Subtle hover state

Avoid excessive borders.

On small screens:

- Prefer responsive cards, or
- Allow horizontal scrolling.

---

# 25. Notifications

Notifications should be visually lightweight.

Use:

- Small cards
- Clear title
- Supporting text
- Timestamp/status
- Appropriate semantic indicator

Examples:

- Booking confirmed
- Schedule assigned
- Procurement completed
- Payment updated
- Rebooking required

Do not use intrusive popups for every normal event.

---

# 26. Language Selector

The existing homepage already provides multilingual support.

Current supported languages:

- English
- हिन्दी
- தமிழ்
- ਪੰਜਾਬੀ
- অসমীয়া
- తెలుగు

The language selector uses:

- Globe icon
- Language code
- Dropdown menu on desktop
- Language grid on mobile
- Active-language highlight
- Small instructional tooltip/pulse

Future pages should use the same language system where multilingual content is implemented.

Do not create a second unrelated language selector.

---

# 27. Help / Chatbot

The project includes a help/chatbot feature.

The chatbot UI should match FASAL.

Recommended style:

- Cream/white panel
- Green/orange accents
- Rounded container
- Simple readable messages
- Inter font
- Minimal shadow
- Mobile-friendly

Avoid a generic bright-blue AI chatbot appearance.

---

# 28. Icons

Preferred:

- Simple SVG icons
- Thin/medium stroke
- Rounded line style
- Agricultural/natural visual language

Existing icons should be reused where applicable.

Avoid mixing many unrelated icon libraries.

---

# 29. Shadows

Use shadows sparingly.

The existing project uses soft shadows such as:

```css
box-shadow: 0 18px 40px -18px rgba(...);
```

Use shadows mainly for:

- Main cards
- Dropdowns
- Floating elements
- Important overlays

Most normal cards can rely on borders instead.

---

# 30. Borders and Radius

Existing visual language uses thin warm borders.

Preferred:

```text
Border: 1px solid light warm neutral
Radius: 7px–14px
```

Use larger radius only for major containers or special UI elements.

---

# 31. Animation

Animations should be subtle.

Existing examples include:

- Button hover transitions
- Language-selector pulse
- Mobile menu expansion
- Small active-state transitions

Allowed:

- opacity transitions
- transform transitions
- subtle hover effects
- small menu animations

Avoid:

- Continuous large animations
- Bouncing UI
- Excessive parallax
- Distracting loaders
- Heavy animated backgrounds

---

# 32. Accessibility

Maintain:

- Semantic HTML
- Proper labels
- Keyboard focus
- Visible focus states
- Accessible buttons
- `aria` attributes where appropriate
- Sufficient text contrast
- Touch-friendly controls
- Clear error messages

Do not sacrifice accessibility for visual styling.

---

# 33. Mobile-First Considerations

Because farmers may primarily use mobile devices:

- Buttons should be easy to tap.
- Form fields should be large enough.
- Important booking information should appear near the top.
- Avoid dense desktop-only tables.
- Avoid tiny text.
- Navigation must work without hover.
- Language selection must be accessible.
- Booking confirmation should be easy to understand.

The mobile interface should feel like the same FASAL product, not a separate mobile design.

---

# 34. Existing Repository as Visual Source of Truth

Before implementing any new page:

1. Inspect the existing HTML.
2. Inspect the existing CSS.
3. Reuse the existing CSS variables.
4. Reuse existing typography.
5. Reuse existing button/card/form patterns.
6. Reuse existing responsive behavior.
7. Reuse existing logo/brand treatment.
8. Extend components rather than creating unrelated styles.

The existing repository currently contains the homepage and registration visual implementations that establish the baseline design. The homepage uses the FASAL agricultural palette, Fraunces/Inter typography, fixed navigation, language switching, hero artwork, feature cards, responsive mobile navigation, and a dark soil-colored CTA section. The registration page uses the same identity with a cream card, agricultural field background, multi-step form, validation states, and success state. 

---

# 35. Do Not Change Existing Design Without Reason

When adding functionality:

### Allowed

- Add new pages.
- Add dashboard components.
- Add booking components.
- Add tables.
- Add status badges.
- Add forms.
- Add cards.
- Add navigation items.
- Extend responsive behavior.
- Add required system-specific UI.

### Not Allowed

- Replace the color palette.
- Replace Fraunces/Inter without a strong reason.
- Replace FASAL branding.
- Introduce a completely different dashboard theme.
- Convert the interface into a generic blue SaaS dashboard.
- Add unnecessary gradients.
- Add excessive glass effects.
- Replace the agricultural identity.
- Remove the existing responsive behavior.
- Make the UI unnecessarily complex.

---

# 36. Component Reuse

Create reusable components/styles for:

- Header
- Brand/logo
- Buttons
- Cards
- Form fields
- Inputs
- Selects
- Status badges
- Tables
- Notifications
- Modals
- Language selector
- Mobile navigation
- Dashboard statistic cards
- Booking summary
- Schedule items

Components should use the existing design tokens rather than hard-coded unrelated colors.

---

# 37. Frontend Architecture Rule

The visual design and business logic are separate concerns.

HTML/CSS/JS should control:

- Layout
- Appearance
- Interaction
- Form presentation
- Loading states
- Error display
- API responses

Backend controls:

- Authentication
- Authorization
- Scheduling
- Capacity
- Booking decisions
- Procurement
- Payment calculation
- Business rules

Do not move backend business logic into the frontend merely to simplify UI development.

---

# 38. Design Consistency Checklist

Before completing any new frontend page, verify:

- [ ] FASAL branding is present where appropriate.
- [ ] Fraunces is used for major display headings.
- [ ] Inter is used for body/UI text.
- [ ] Existing color tokens are reused.
- [ ] Buttons match the current design.
- [ ] Cards match the current design.
- [ ] Form controls match the registration page.
- [ ] Borders/radius are consistent.
- [ ] Shadows are subtle.
- [ ] Responsive behavior is implemented.
- [ ] Mobile navigation remains consistent.
- [ ] Language support uses the existing pattern.
- [ ] Status colors are semantic.
- [ ] No unnecessary animation was introduced.
- [ ] No unrelated design system was introduced.
- [ ] Existing pages were not visually broken.

---

# 39. Final Design Principle

The final application should feel like one unified product:

**FASAL**

A user moving from:

`Homepage → Registration → Login → Farmer Dashboard → Booking → Schedule → Procurement → Payment`

should feel that every screen belongs to the same application.

The existing GitHub HTML/CSS/JS design is the baseline. New functionality should be added **inside that visual language**, not by replacing it.
