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
import aiounittest

from tests import create_module


class RuleTest(aiounittest.AsyncTestCase):
    async def test_rules_allow_with_default_deny(self) -> None:
        """
        Tests allow rules when the defaults are to deny those permissions.
        """
        module = create_module(
            {
                "rules": [
                    {"match": "@a.*:.*", "allow": ["invite"]},
                    {"match": "@b.*:.*", "allow": ["create_room"]},
                ],
                "default_deny": ["invite", "create_room"],
            }
        )

        self.assertTrue(
            await module.callback_user_may_invite(
                "@alice:hs1", "@other:hs2", "!room1:hs1"
            )
        )
        self.assertFalse(
            await module.callback_user_may_invite(
                "@bob:hs1", "@other:hs2", "!room2:hs1"
            )
        )
        self.assertFalse(
            await module.callback_user_may_invite(
                "@kristina:hs1", "@other:hs2", "!room2:hs1"
            )
        )

        self.assertFalse(await module.callback_user_may_create_room("@alice:hs1"))
        self.assertTrue(await module.callback_user_may_create_room("@bob:hs1"))
        self.assertFalse(await module.callback_user_may_create_room("@kristina:hs1"))

    async def test_rules_deny_with_no_default(self) -> None:
        """
        Tests deny rules with no explicit defaults (which means all defaults
        are to allow).
        """
        module = create_module(
            {
                "rules": [
                    {"match": "@a.*:.*", "deny": ["invite"]},
                    {"match": "@b.*:.*", "deny": ["create_room"]},
                ],
            }
        )

        self.assertFalse(
            await module.callback_user_may_invite(
                "@alice:hs1", "@other:hs2", "!room1:hs1"
            )
        )
        self.assertTrue(
            await module.callback_user_may_invite(
                "@bob:hs1", "@other:hs2", "!room2:hs1"
            )
        )
        self.assertTrue(
            await module.callback_user_may_invite(
                "@kristina:hs1", "@other:hs2", "!room2:hs1"
            )
        )

        self.assertTrue(await module.callback_user_may_create_room("@alice:hs1"))
        self.assertFalse(await module.callback_user_may_create_room("@bob:hs1"))
        self.assertTrue(await module.callback_user_may_create_room("@kristina:hs1"))

    async def test_rules_ordered_top_to_bottom(self) -> None:
        """
        Tests that the rules are checked in top-to-bottom order.
        """

        module = create_module(
            {
                "rules": [
                    {"match": "@bruce.*:.*", "allow": ["create_room"]},
                    {"match": "@b.*:.*", "deny": ["create_room"]},
                ],
            }
        )

        self.assertTrue(await module.callback_user_may_create_room("@bruce:hs1"))
        self.assertFalse(await module.callback_user_may_create_room("@bob:hs1"))
