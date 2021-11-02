# Copyright 2021 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        """
        A correct configuration is parsed into the correct shape.
        """
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
                    "default_deny": ["invite", "create_room"],
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
