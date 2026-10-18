"""Vercel ignored-build step: proceed only after this commit passes CI.

Vercel uses exit 0 to skip a build and exit 1 to proceed. The repository is
public, so no GitHub or Vercel credential is required for this read-only check.
"""
import json
import os
import re
import sys
from urllib.request import Request, urlopen

CHECK_NAME = 'Production regression tests'


def passed(checks, revision):
    candidates = [check for check in checks if check.get('name') == CHECK_NAME
                  and check.get('head_sha') == revision
                  and check.get('app', {}).get('slug') == 'github-actions']
    if not candidates:
        return False
    latest = max(candidates, key=lambda check: check.get('id', 0))
    return latest.get('status') == 'completed' and latest.get('conclusion') == 'success'


def main():
    revision = os.environ.get('VERCEL_GIT_COMMIT_SHA', '')
    if os.environ.get('VERCEL_GIT_COMMIT_REF') != 'main' or not re.fullmatch(r'[a-fA-F0-9]{40}', revision):
        print('Skipping: production requires the main branch and a Git commit revision.')
        return 0
    url = f'https://api.github.com/repos/proffesergio/chandramonians-web/commits/{revision}/check-runs?per_page=100'
    try:
        request = Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'ChandramoniansBuildGate/1.0',
                                        'X-GitHub-Api-Version': '2022-11-28'})
        with urlopen(request, timeout=20) as response:
            checks = json.load(response).get('check_runs', [])
    except Exception:
        print('Skipping: could not verify GitHub regression checks. Retry after checking GitHub Actions.')
        return 0
    if passed(checks, revision):
        print('Verified: this commit passed the production regression tests. Proceeding with build.')
        return 1
    print('Skipping: this commit has not passed the production regression tests yet. CI will trigger the deployment hook after success.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
