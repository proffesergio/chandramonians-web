const { setTimeout: delay } = require('node:timers/promises');

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
  let triggered;
  try { triggered = await fetch(hook, { method: 'POST', signal: AbortSignal.timeout(30000) }); }
  catch { throw new Error('Could not reach the deployment hook. Check Vercel connectivity.'); }
  if (!triggered.ok) throw new Error(`Vercel refused the deployment hook: HTTP ${triggered.status}.`);
  console.log('Production deployment requested. Waiting for the tested commit to become live.');
  const until = Date.now() + 15 * 60 * 1000;
  while (Date.now() < until) {
    try {
      const response = await fetch(`https://www.chandramonians.com/health/?revision=${revision}`, {
        cache: 'no-store', signal: AbortSignal.timeout(15000)
      });
      if (response.ok && (await response.json()).revision === revision) {
        const map = await fetch('https://www.chandramonians.com/alumni-map/', { signal: AbortSignal.timeout(15000) });
        if (!map.ok) throw new Error('The deployed Alumni Map returned an error.');
        console.log('Verified production health and Alumni Map for the tested commit.');
        return;
      }
    } catch { /* Build or edge promotion may still be in progress. */ }
    await delay(10000);
  }
  throw new Error('The tested commit did not become live within 15 minutes. Check Vercel deployment/build logs.');
}

if (require.main === module) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
module.exports = { main };
