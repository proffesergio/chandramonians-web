"""Verify the exact commit's CI proof tag using Git transport, without API quotas.

Vercel uses exit 0 to skip a build and exit 1 to proceed. GitHub Actions creates
the immutable ci-passed/<SHA> ref only after the regression job succeeds.
"""
import os
import re
import subprocess
import sys
import time

REPOSITORY = 'https://github.com/proffesergio/chandramonians-web.git'


def passed(references, revision):
    expected = f'refs/tags/ci-passed/{revision}'
    return any(line.split() == [revision, expected] for line in references.splitlines())


def main():
    revision = os.environ.get('VERCEL_GIT_COMMIT_SHA', '')
    if os.environ.get('VERCEL_GIT_COMMIT_REF') != 'main' or not re.fullmatch(r'[a-fA-F0-9]{40}', revision):
        print('Skipping: production requires the main branch and a Git commit revision.')
        return 0
    reference = f'refs/tags/ci-passed/{revision}'
    for attempt in range(3):
        try:
            result = subprocess.run(['git', 'ls-remote', '--exit-code', '--refs', REPOSITORY, reference],
                                    capture_output=True, text=True, timeout=20,
                                    env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
            if result.returncode == 0 and passed(result.stdout, revision):
                print('Verified: exact commit has a CI pass tag. Proceeding with build.')
                return 1
            if result.returncode in (0, 2):
                print('Skipping: CI pass tag is missing or points to a different commit. CI will trigger deployment after tests pass.')
                return 0
        except (OSError, subprocess.TimeoutExpired):
            pass
        if attempt < 2:
            time.sleep(attempt + 1)
    print('Skipping: Git transport could not verify the CI pass tag after 3 attempts. Check repository connectivity.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
