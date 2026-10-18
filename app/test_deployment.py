from unittest import TestCase
from unittest.mock import patch, call

from scripts.vercel_build_gate import main, passed


class DeploymentGateTests(TestCase):
    revision = 'a' * 40

    def test_requires_exact_ci_pass_tag(self):
        matching = f'{self.revision} refs/tags/ci-passed/{self.revision}\n'
        self.assertTrue(passed(matching, self.revision))
        self.assertFalse(passed(f"{'b' * 40} refs/tags/ci-passed/{self.revision}\n", self.revision))
        self.assertFalse(passed('', self.revision))

    @patch.dict('os.environ', {'VERCEL_GIT_COMMIT_REF': 'main', 'VERCEL_GIT_COMMIT_SHA': 'a' * 40})
    @patch('scripts.vercel_build_gate.time.sleep')
    @patch('scripts.vercel_build_gate.subprocess.run', side_effect=OSError('Network unavailable'))
    def test_network_error_skips_build_instead_of_bypassing_tests(self, request, sleep):
        self.assertEqual(main(), 0)

    @patch.dict('os.environ', {'VERCEL_GIT_COMMIT_REF': 'feature', 'VERCEL_GIT_COMMIT_SHA': 'a' * 40})
    @patch('scripts.vercel_build_gate.subprocess.run')
    def test_nonproduction_branch_skips_without_network(self, request):
        self.assertEqual(main(), 0)
        request.assert_not_called()
