const { setTimeout: delay } = require('node:timers/promises');

async function recordCiPass(revision, headers) {
  const base = 'https://api.github.com/repos/proffesergio/chandramonians-web/git';
  const reference = `refs/tags/ci-passed/${revision}`;
  const read = () => fetch(`${base}/ref/tags/ci-passed/${revision}`, { headers });
  let response = await read();
  if (response.status === 404) {
    response = await fetch(`${base}/refs`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ ref: reference, sha: revision }) });
    if (response.status === 422) response = await read(); // A concurrent retry may have created the same ref.
  }
  if (!response.ok) throw new Error(`Could not record CI pass tag: HTTP ${response.status}. Check the deploy job's contents: write permission.`);
  const proof = await response.json();
  if (proof.ref !== reference || proof.object?.type !== 'commit' || proof.object?.sha !== revision) {
    throw new Error('Existing CI pass tag does not point to the tested commit. It was not overwritten.');
  }
  console.log(`Verified CI pass tag for ${revision.slice(0, 12)}.`);
}

async function main() {
  const hook = process.env.VERCEL_DEPLOY_HOOK;
  const revision = process.env.GITHUB_SHA;
  if (!hook || !revision) throw new Error('Missing VERCEL_DEPLOY_HOOK repository secret or GITHUB_SHA.');
  const headers = { Authorization: `Bearer ${process.env.GITHUB_TOKEN}`, Accept: 'application/vnd.github+json' };
  const latest = await fetch('https://api.github.com/repos/proffesergio/chandramonians-web/commits/main', { headers });
  if (!latest.ok) throw new Error('Could not verify the latest main commit.');
  if ((await latest.json()).sha !== revision) {
    console.log('A newer main commit exists. Its workflow will deploy after its own tests pass.');
    return;
  }
  await recordCiPass(revision, headers);
  let triggered;
  try { triggered = await fetch(hook, { method: 'POST', signal: AbortSignal.timeout(30000) }); }
  catch { throw new Error('Could not reach the deployment hook. Check Vercel connectivity.'); }
  if (!triggered.ok) throw new Error(`Vercel refused the deployment hook: HTTP ${triggered.status}.`);
  console.log('Production deployment requested. Waiting for the tested commit to become live.');
  const until = Date.now() + 15 * 60 * 1000;
  let lastStatus = 'No health response received.';
  let nextProgress = 0;
  while (Date.now() < until) {
    try {
      const response = await fetch(`https://www.chandramonians.com/health/?revision=${revision}`, {
        cache: 'no-store', signal: AbortSignal.timeout(15000)
      });
      if (!response.ok) {
        lastStatus = `Production health returned HTTP ${response.status}.`;
      } else if ((await response.json()).revision === revision) {
        const map = await fetch('https://www.chandramonians.com/alumni-map/', { signal: AbortSignal.timeout(15000) });
        if (!map.ok) {
          lastStatus = `Expected commit is live, but Alumni Map returned HTTP ${map.status}.`;
        } else {
          console.log('Verified production health and Alumni Map for the tested commit.');
          return;
        }
      } else {
        lastStatus = 'Production still serves a different commit.';
      }
    } catch { lastStatus = 'Production health could not be reached or returned invalid JSON.'; }
    if (Date.now() >= nextProgress) {
      console.log(`Waiting: ${lastStatus}`);
      nextProgress = Date.now() + 30000;
    }
    await delay(10000);
  }
  throw new Error(`The tested commit did not become live within 15 minutes. ${lastStatus} Check Vercel deployment/build logs for a canceled or failed build.`);
}

if (require.main === module) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
module.exports = { main, recordCiPass };
