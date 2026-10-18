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

## Open work

- Mentorship currently displays a form and needs a persisted application workflow.
- Job Board is a reviewed-content placeholder; it needs moderation and expiry fields before launch.
- Payment records still come from the official sheet and should gain a durable user link after the association defines a stable member identifier.
- Membership pricing and payment confirmation are not yet automated; approval remains an admin-reviewed workflow.

## Delivery rule

Keep changes in a local commit, run the targeted Django and Node tests plus `git diff --check`, and let the maintainer push `main`. The GitHub Actions workflow runs regression tests before triggering and verifying the Vercel production deployment.
