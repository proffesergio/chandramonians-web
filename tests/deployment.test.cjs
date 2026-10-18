const test = require('node:test');
const assert = require('node:assert/strict');
const { main } = require('../scripts/deploy_production.cjs');

function setup(t) {
  const previousFetch = global.fetch;
  const previous = { hook: process.env.VERCEL_DEPLOY_HOOK, sha: process.env.GITHUB_SHA, token: process.env.GITHUB_TOKEN };
  process.env.VERCEL_DEPLOY_HOOK = 'https://example.invalid/private-deployment-hook';
  process.env.GITHUB_SHA = 'a'.repeat(40);
  process.env.GITHUB_TOKEN = 'test-only-token';
  t.after(() => {
    global.fetch = previousFetch;
    for (const [name, value] of Object.entries({ VERCEL_DEPLOY_HOOK: previous.hook, GITHUB_SHA: previous.sha, GITHUB_TOKEN: previous.token })) {
      if (value === undefined) delete process.env[name]; else process.env[name] = value;
    }
  });
}

test('successful deployment waits for matching live revision and checks map', async t => {
  setup(t);
  const calls = [];
  global.fetch = async (url, options) => {
    calls.push([url, options]);
    if (url.includes('api.github.com')) return { ok: true, json: async () => ({ sha: process.env.GITHUB_SHA }) };
    if (url.includes('/health/')) return { ok: true, json: async () => ({ status: 'ok', revision: process.env.GITHUB_SHA }) };
    return { ok: true };
  };
  await main();
  assert.equal(calls.length, 4);
  assert.equal(calls[1][0], process.env.VERCEL_DEPLOY_HOOK);
  assert.equal(calls[1][1].method, 'POST');
  assert.equal(calls[3][0], 'https://www.chandramonians.com/alumni-map/');
  assert.equal(calls[1][1].headers, undefined, 'GitHub token must not be sent to the Vercel hook');
});

test('superseded main commit never invokes deployment hook', async t => {
  setup(t);
  let requests = 0;
  global.fetch = async () => { requests++; return { ok: true, json: async () => ({ sha: 'b'.repeat(40) }) }; };
  await main();
  assert.equal(requests, 1);
});

test('hook rejection fails without disclosing private hook URL', async t => {
  setup(t);
  global.fetch = async url => url.includes('api.github.com')
    ? { ok: true, json: async () => ({ sha: process.env.GITHUB_SHA }) }
    : { ok: false, status: 403 };
  await assert.rejects(main(), error => error.message.includes('HTTP 403') && !error.message.includes('private-deployment-hook'));
});

test('missing hook secret fails before making network requests', async t => {
  setup(t);
  delete process.env.VERCEL_DEPLOY_HOOK;
  global.fetch = async () => { assert.fail('No network request should be made'); };
  await assert.rejects(main(), /Missing VERCEL_DEPLOY_HOOK/);
});
