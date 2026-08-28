"""Tests for the billing refusal.

Every other failure in this probe announces itself — a build breaks, a mount
is denied, a version does not print. A billing mistake does not: the run
succeeds and the bill arrives later. So this is the part worth testing.

Run with: python3 -m unittest discover tests
"""

import unittest

from probe import billing


class TestMeteredEnvVars(unittest.TestCase):
    def test_ordinary_environment_is_clean(self):
        self.assertEqual(billing.metered_env_vars({"HOME": "/home/geoff"}), [])

    def test_api_key_is_caught(self):
        env = {"ANTHROPIC_API_KEY": "sk-whatever"}
        self.assertEqual(billing.metered_env_vars(env), ["ANTHROPIC_API_KEY"])

    def test_oauth_token_is_allowed(self):
        """It is a subscription credential, so it must not be refused."""
        self.assertEqual(billing.metered_env_vars({"CLAUDE_CODE_OAUTH_TOKEN": "x"}), [])

    def test_empty_value_counts_as_unset(self):
        self.assertEqual(billing.metered_env_vars({"ANTHROPIC_API_KEY": ""}), [])

    def test_every_listed_name_is_caught(self):
        """Guards against a name being listed but misspelled."""
        for name in billing.BILLING_ENV_VARS:
            with self.subTest(name=name):
                self.assertEqual(billing.metered_env_vars({name: "x"}), [name])


class TestMeteredSettingsKeys(unittest.TestCase):
    def test_ordinary_settings_are_clean(self):
        self.assertEqual(billing.metered_settings_keys({"model": "opus"}), [])

    def test_every_listed_key_is_caught(self):
        for key in billing.CREDENTIAL_SETTINGS_KEYS:
            with self.subTest(key=key):
                self.assertEqual(billing.metered_settings_keys({key: "x"}), [key])


class TestRefuseIfMetered(unittest.TestCase):
    def test_clean_run_is_allowed(self):
        billing.refuse_if_metered({"HOME": "/home/geoff"}, {"model": "opus"})

    def test_env_var_refuses(self):
        with self.assertRaises(billing.MeteredBilling):
            billing.refuse_if_metered({"ANTHROPIC_API_KEY": "sk-x"}, {})

    def test_settings_key_refuses(self):
        with self.assertRaises(billing.MeteredBilling):
            billing.refuse_if_metered({}, {"apiKeyHelper": "/bin/mint-a-key"})

    def test_message_names_every_problem(self):
        with self.assertRaises(billing.MeteredBilling) as caught:
            billing.refuse_if_metered({"ANTHROPIC_API_KEY": "x"}, {"apiKeyHelper": "y"})
        self.assertIn("ANTHROPIC_API_KEY", str(caught.exception))
        self.assertIn("apiKeyHelper", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
