"""Regression tests for the publisher guardian secret scanner."""

import unittest

from scripts.check_repo_secrets import find_secrets


class SecretScannerTests(unittest.TestCase):
    def test_sandisk_forum_url_is_not_a_secret(self):
        url = (
            "https://forums.sandisk.com/t/"
            "sandisk-ultra-3-0-usb-stick-painfully-slow-transfer-speeds/34060"
        )
        self.assertEqual(find_secrets(url.encode()), [])

    def test_realistic_api_key_is_detected(self):
        token = b"sk-" + b"A1b2C3d4" * 4
        findings = find_secrets(b"API_TOKEN=" + token + b"\n")
        self.assertEqual(findings, [("API key", 1)])

    def test_github_token_families_are_detected(self):
        classic = b"ghp_" + b"Xy9Z" * 6
        fine_grained = b"github_pat_" + b"Xy9Z" * 6
        self.assertEqual(find_secrets(b"token=" + classic), [("GitHub classic token", 1)])
        self.assertEqual(
            find_secrets(b"token=" + fine_grained),
            [("GitHub fine-grained token", 1)],
        )

    def test_prefix_inside_word_is_not_a_token(self):
        long_suffix = b"AlphaNum9" * 4
        self.assertEqual(find_secrets(b"task-" + long_suffix), [])
        self.assertEqual(find_secrets(b"prefixghp_" + long_suffix), [])

    def test_line_numbers_are_reported_without_secret_values(self):
        token = b"sk-" + b"T3stKey" * 5
        findings = find_secrets(b"ordinary text\nAPI_KEY=" + token)
        self.assertEqual(findings, [("API key", 2)])
        self.assertNotIn(token.decode(), repr(findings))


if __name__ == "__main__":
    unittest.main()
