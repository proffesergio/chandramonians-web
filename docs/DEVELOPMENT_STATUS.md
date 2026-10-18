# Development status

This file is the handoff record for ongoing feature work and production fixes.

## Current release candidate

- Alumni payment matching is conservative: an account receives a payment record only when the full name or phone match is unambiguous.
- Alumni Dashboard now contains private activity analytics, profile completion, membership linking state, and reduced-motion-safe animation.
- Alumni directory, jobs, and mentorship routes require the alumni role. Payment and membership pages remain scoped to the signed-in alumni.
- Production deployment is gated by the tested commit's immutable `ci-passed/<SHA>` tag, then verified through `/health/` and `/alumni-map/`.

## Open work

- Mentorship currently displays a form and needs a persisted application workflow.
- Job Board is a reviewed-content placeholder; it needs moderation and expiry fields before launch.
- Payment records still come from the official sheet and should gain a durable user link after the association defines a stable member identifier.

## Delivery rule

Keep changes in a local commit, run the targeted Django and Node tests plus `git diff --check`, and let the maintainer push `main`. The GitHub Actions workflow runs regression tests before triggering and verifying the Vercel production deployment.
