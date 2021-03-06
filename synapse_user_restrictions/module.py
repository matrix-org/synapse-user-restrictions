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
from synapse.module_api import ModuleApi
from synapse.module_api.errors import ConfigError

from synapse_user_restrictions.config import (
    ALL_UNDERSTOOD_PERMISSIONS,
    CREATE_ROOM,
    INVITE,
    ConfigDict,
    RuleResult,
    UserRestrictionsModuleConfig,
)


class UserRestrictionsModule:
    def __init__(self, config: UserRestrictionsModuleConfig, api: ModuleApi):
        # Keep a reference to the config and Module API
        self._api = api
        self._config = config

        # Register callbacks here
        api.register_spam_checker_callbacks(
            user_may_create_room=self.callback_user_may_create_room,
            user_may_invite=self.callback_user_may_invite,
        )

    @staticmethod
    def parse_config(config: ConfigDict) -> UserRestrictionsModuleConfig:
        try:
            return UserRestrictionsModuleConfig.from_config(config)
        except (TypeError, ValueError) as e:
            raise ConfigError(f"Failed to parse user restrictions module config: {e}")

    def _apply_rules(self, user_id: str, permission: str) -> bool:
        """
        Apply the rules in-order, returning a boolean result.
        If no rules make a decision, the permission will be allowed by default.

        Arguments:
            user_id: the Matrix ID (@bob:example.org) of the user seeking
                permission
            permission: the string ID representing the permission being sought

        Returns:
            True if the rules allow the user to use that permission
                or do not make a decision,
            False if the user is denied from using that permission.
        """
        if permission not in ALL_UNDERSTOOD_PERMISSIONS:
            raise ValueError(f"Permission not recognised: {permission!r}")

        for rule in self._config.rules:
            rule_result = rule.apply(user_id, permission)
            if rule_result == RuleResult.Allow:
                return True
            elif rule_result == RuleResult.Deny:
                return False

        if permission in self._config.default_deny:
            return False

        return True

    async def callback_user_may_create_room(self, user: str) -> bool:
        return self._apply_rules(user, CREATE_ROOM)

    async def callback_user_may_invite(
        self, inviter: str, invitee: str, room_id: str
    ) -> bool:
        return self._apply_rules(inviter, INVITE)
