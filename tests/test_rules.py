import unittest

from tests import create_module


class RuleTest(unittest.IsolatedAsyncioTestCase):
    async def test_rules_allow_with_default_deny(self) -> None:
        """
        Tests allow rules when the defaults are to deny those permissions.
        :return:
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
