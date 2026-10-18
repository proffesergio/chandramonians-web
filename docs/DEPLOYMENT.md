# Push-to-production deployment

The repository is configured for **manual local push → GitHub tests → Vercel
production deployment**. The workflow lives in
`../.github/workflows/production.yml`.

## One-time connection

The repository `proffesergio/chandramonians-web` now has an encrypted repository
secret named `VERCEL_DEPLOY_HOOK`. It targets the verified
`chandramonians/chandramonians-web` project, its connected GitHub repository,
and the `main` production branch serving `https://www.chandramonians.com`.
The secret URL is not stored in source files. If the hook is revoked, create a
replacement in Vercel's project Git settings and update `VERCEL_DEPLOY_HOOK` in
[GitHub Actions secrets](https://github.com/proffesergio/chandramonians-web/settings/secrets/actions).
No Vercel personal access token is required. Temporary token secrets from setup
were removed: the CLI login is short-lived, and its application cannot create
permanent personal access tokens. Deployment revision system variables are enabled.

These source changes are intentionally left uncommitted and unpushed for the
owner to review. The workflow becomes active when its file is committed and
pushed. Existing local account/environment files stay ignored. Do not stage the
modified local SQLite backup; it is already tracked historically despite the
ignore rule. Vercel uploads exclude SQLite, local media, and environment files.

## Every subsequent release

1. Commit the intended source changes, new migrations, generated map assets,
   country-data JSON, and workflow. Include previous pending security/email fixes
   in this release. Review the staged file list before committing.
2. Push the commit yourself: `git push origin main`.
3. Open [GitHub Actions](https://github.com/proffesergio/chandramonians-web/actions).
   **Test and deploy production** runs configuration checks, migration-drift
   checks, all Django tests against a disposable SQLite database, and JavaScript
   interaction tests. The tests have no production database credentials.
4. After success, the deployment job invokes the private deployment hook. Vercel
   fetches `main` from GitHub and builds using its existing production settings.
   `scripts/vercel_build_gate.py` checks the public GitHub check runs for that
   exact revision. Vercel's ignored-build command skips untested commits, and
   `build.py` repeats the check before any migration in case an ignore step is
   bypassed. Network errors or missing/failed checks do not pass this gate.
   `build.py` then applies committed PostgreSQL migrations before the deployment
   becomes live. It refuses a missing database URL or a SQLite target.
5. The workflow waits up to 15 minutes for `/health/` to report the tested Git
   revision, then checks `/alumni-map/` on the production domain.
   Failed checks turn the workflow red; they do not automatically reverse a
   deployment or database migration. Review the Vercel build logs on failure.

Pull requests targeting `main` run tests without deploying. A workflow dispatch
on `main` provides a manual retry. Production runs are serialized and are not
cancelled halfway through migrations. Vercel's Git integration remains enabled
because deploy hooks require it. Its initial automatic deployment may be marked
cancelled while the regression tests run; the hook requests the build after they
pass. If an initial build waits in a queue until tests have already passed, it
can also proceed safely. Do not rename the workflow check **Production regression
tests** without updating `CHECK_NAME` in `scripts/vercel_build_gate.py`.

No production deployment was triggered as part of this local change. The first
push is still needed to verify the complete hosted pipeline. Use additive,
backwards-compatible migrations; a Vercel rollback does not undo schema/data
changes. Keep database backups, including the new avatar table.

## Alumni Map and photos

`/alumni-map/` lists all active registered Alumni profiles, including profiles
without shared locations. Successfully registered new alumni appear
automatically. Spreadsheet-only memberships are a separate directory.
Users choose **Profile → Current country → Share my country** to add a country
marker. Countries can be filtered alongside names/professions and batch years;
marker and list navigation works without JavaScript. Email, phone, and private
addresses are not included. Clearing the sharing checkbox removes the location
from the public map. Markers represent approximate country label positions,
not home or city coordinates.

The home page, public navigation, and alumni sidebar link to the map. Geographic
assets are served locally with Natural Earth attribution and require no map API
key. Generated files are committed so deployment does not download geographic
data. To rebuild them from Natural Earth Admin 0 GeoJSON:

```powershell
python scripts/build_alumni_map.py PATH_TO_NATURAL_EARTH_COUNTRIES.geojson
```

Profile pictures use a dedicated PostgreSQL-backed storage class. JPEG, PNG,
WebP, and GIF inputs up to 3 MB and 20 megapixels are normalized to at most
512×512 WebP images. Metadata is not carried into the output. UUID-based URLs
serve the bytes through Django in production; uploads survive function restarts
and redeployments without another storage account. The database table stores
only avatars; gallery photos and learning-material uploads still need their
own durable object-storage setup. Existing production photo-reference count
was zero during this update, so no old profile files required migration.

This approach is suitable for small avatars; monitor PostgreSQL usage and move
larger media to object storage as usage grows. The 3 MB input limit also stays
below Vercel's function payload limit, allowing for multipart form overhead.
Password changes now use Django validators and preserve the user's session.

## Validation

- 55 Django regression tests passed, including upload/readback from a fresh
  storage instance, invalid/oversized uploads, password sessions, map consent,
  filtering, inactive accounts, and new signup visibility.
- Nine JavaScript interaction/deployment tests passed, including hook failure,
  superseded commits, matching live revision, and keeping credentials separated.
- `actionlint` validated the workflow; Django reported no migration drift.
- A separate local preview database was used; the owner's `db.sqlite3` was not
  migrated or overwritten. No browser surface was enabled in this session, so
  a fresh desktop/mobile visual check remains after the first deployment.

References: [Vercel deploy hooks](https://vercel.com/docs/deploy-hooks),
[Git deployment configuration](https://vercel.com/docs/project-configuration/git-configuration),
[Function limits](https://vercel.com/docs/functions/limitations),
[Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/).
