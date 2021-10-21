import re
import unittest

from synapse.module_api.errors import ConfigError

from synapse_user_restrictions import UserRestrictionsModule
from synapse_user_restrictions.config import (
    RegexMatchRule,
    UserRestrictionsModuleConfig,
)

from tests import create_module


class ConfigTest(unittest.IsolatedAsyncioTestCase):
    def test_config_error_exceptions(self) -> None:
        """
        Check that configuration errors raise exceptions.
        """
        with self.assertRaisesRegex(ConfigError, ".*unterminated.*"):
            create_module({"rules": [{"match": "@srtsrt[a-z", "allow": "invite"}]})

        with self.assertRaisesRegex(
            ConfigError, "'nonsense' is not a permission recognised"
        ):
            # The `nonsense` permission doesn't exist.
            create_module({"rules": [{"match": "@bob:test", "allow": ["nonsense"]}]})

        with self.assertRaises(ConfigError):
            create_module({})

        with self.assertRaises(ConfigError):
            create_module({"roooolz": []})

        with self.assertRaises(ConfigError):
            create_module(
                {
                    "rules": True,
                }
            )

        with self.assertRaises(ConfigError):
            create_module(
                {
                    "rules": [False],
                }
            )

        with self.assertRaises(ConfigError):
            create_module(
                {
                    "rules": [{"maaartch": "bleh"}],
                }
            )

    def test_config_correct(self) -> None:
        self.assertEqual(
            UserRestrictionsModule.parse_config(
                {
                    "rules": [
                        {
                            "match": "@unprivileged[0-9]+:.*",
                            "allow": ["invite"],
                            "deny": ["create_room"],
                        }
                    ],
                    "default_deny": {"invite", "create_room"},
                }
            ),
            UserRestrictionsModuleConfig(
                rules=[
                    RegexMatchRule(
                        re.compile("@unprivileged[0-9]+:.*"),
                        allow={"invite"},
                        deny={"create_room"},
                    )
                ],
                default_deny={"invite", "create_room"},
            ),
        )
