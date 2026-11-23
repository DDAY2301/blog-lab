import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_repository_secrets import find_possible_secrets

class RepositorySecretScanTests(unittest.TestCase):
    def test_does_not_match_tail_of_common_word(self):
        url = "https://forums.sandisk.com/t/sandisk-" + "portable-ssd-support-guide"
        self.assertEqual(find_possible_secrets(url), set())

    def test_detects_realistic_key_shapes(self):
        self.assertIn("api_secret", find_possible_secrets("token=" + "sk-" + "a" * 28))
        self.assertIn("github_classic", find_possible_secrets("token=" + "ghp_" + "b" * 30))
        self.assertIn("github_fine_grained", find_possible_secrets("token=" + "github_pat_" + "c" * 40))

    def test_does_not_log_or_match_short_fragments(self):
        self.assertEqual(find_possible_secrets("sk-test or ghp_short or github_pat_short"), set())

if __name__ == "__main__":
    unittest.main()
