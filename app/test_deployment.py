from unittest import TestCase
from unittest.mock import patch

from scripts.vercel_build_gate import main, passed


class DeploymentGateTests(TestCase):
    revision = 'a' * 40

    def check(self, **changes):
        row = {'id': 1, 'name': 'Production regression tests', 'head_sha': self.revision,
               'app': {'slug': 'github-actions'}, 'status': 'completed', 'conclusion': 'success'}
        row.update(changes)
        return row

    def test_requires_successful_check_for_exact_commit_from_github_actions(self):
        self.assertTrue(passed([self.check()], self.revision))
        for changes in ({'head_sha': 'b' * 40}, {'app': {'slug': 'another-app'}},
                        {'status': 'in_progress'}, {'conclusion': 'failure'}, {'name': 'Unrelated test'}):
            with self.subTest(changes=changes):
                self.assertFalse(passed([self.check(**changes)], self.revision))

    def test_newer_failed_or_running_rerun_blocks_an_older_pass(self):
        self.assertFalse(passed([self.check(), self.check(id=2, conclusion='failure')], self.revision))
        self.assertFalse(passed([self.check(), self.check(id=2, status='in_progress')], self.revision))
        self.assertFalse(passed([], self.revision))

    @patch.dict('os.environ', {'VERCEL_GIT_COMMIT_REF': 'main', 'VERCEL_GIT_COMMIT_SHA': 'a' * 40})
    @patch('scripts.vercel_build_gate.urlopen', side_effect=OSError('Network unavailable'))
    def test_network_error_skips_build_instead_of_bypassing_tests(self, request):
        self.assertEqual(main(), 0)

    @patch.dict('os.environ', {'VERCEL_GIT_COMMIT_REF': 'feature', 'VERCEL_GIT_COMMIT_SHA': 'a' * 40})
    @patch('scripts.vercel_build_gate.urlopen')
    def test_nonproduction_branch_skips_without_network(self, request):
        self.assertEqual(main(), 0)
        request.assert_not_called()
