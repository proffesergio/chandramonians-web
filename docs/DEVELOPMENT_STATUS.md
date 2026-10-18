# Development status

This file is the handoff record for ongoing feature work and production fixes.

## Current release candidate

- Alumni payment matching is conservative: an account receives a payment record only when the full name or phone match is unambiguous.
- Alumni Dashboard now contains private activity analytics, profile completion, membership linking state, and reduced-motion-safe animation.
- Alumni directory, jobs, and mentorship routes require the alumni role. Payment and membership pages remain scoped to the signed-in alumni.
- Production deployment is gated by the tested commit's immutable `ci-passed/<SHA>` tag, then verified through `/health/` and `/alumni-map/`.
- Vercel Web Analytics is wired into both Django root layouts through the official HTML bootstrap and `/_vercel/insights/script.js`; enable Web Analytics once in the Vercel project settings.
- The Super Admin area is titled `Admin Dashboard`, with animated operational metrics and grouped People, Membership, Payments, Content, and Communication navigation.
- Membership applications support General, Life, and Board of Trustee Membership, with validated payment method/date, duplicate-pending protection, applicant history, and animated admin review cards.
- Public header displays the round logo emblem beside the Bangla brand, with the association's full Bangla tagline and responsive text wrapping.
- Alumni Map country clusters now animate into a selected region and open public profile cards, with keyboard-accessible close/reset controls, reduced-motion support, and a working link fallback without JavaScript.
- Registration rejects email duplicates regardless of capitalization, normalizes new email addresses, and handles concurrent username/email conflicts without creating orphaned profiles. Legacy ambiguous emails fail authentication safely.
- Alumni can edit parents' names, current/permanent addresses, phone, blood group, education, profession, workplace, and SSC batch. Each field has an independently revocable public visibility switch; new sensitive fields are private by default. Existing public batch/profession/workplace settings are preserved until changed.
- Public profiles, directories, map payloads, and search filters respect visibility. Alumni profile writes are owner-scoped and validated separately from account/password/photo updates.
- Private, revocable donor-programme interest and blood-group fields are available for administrators to filter; no live donor matching or emergency notification service is enabled.
- Public alumni profiles now group shared details into icon-led family, education/career, and contact cards with compact Bangla labels. Privacy switches still control every displayed field.
- A scalable book-and-sun favicon is shared by public, dashboard, and authentication layouts. Header tagline is the single-line school name, with keyboard-friendly navigation hover/focus effects and reduced-motion support.

## Open work

- Mentorship currently displays a form and needs a persisted application workflow.
- Job Board is a reviewed-content placeholder; it needs moderation and expiry fields before launch.
- Payment records still come from the official sheet and should gain a durable user link after the association defines a stable member identifier.
- Membership pricing and payment confirmation are not yet automated; approval remains an admin-reviewed workflow.
- Blood donation roadmap: review donor consent and eligibility workflow, voluntary current availability, region-based requests, verified request moderation, and private contact delivery before enabling emergency matching. Never infer donor availability from a stored blood group.
- Optional direct support chats and group chats are displayed as coming soon on the map. Before activation they need participant opt-in, membership authorization, persistent messages, moderation, blocking/reporting, and delivery controls. Current location consent supports country-level grouping; finer regional clustering requires optional city/region data and explicit sharing consent.

## Delivery rule

Keep changes in a local commit, run the targeted Django and Node tests plus `git diff --check`, and let the maintainer push `main`. The GitHub Actions workflow runs regression tests before triggering and verifying the Vercel production deployment.
