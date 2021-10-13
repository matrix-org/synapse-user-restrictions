from typing import Any, Dict

import attr
import cattr
from synapse.module_api import ModuleApi
from synapse.module_api.errors import ConfigError


@attr.s(auto_attribs=True, frozen=True)
class UserRestrictionsModuleConfig:
    example_option: bool = False


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
    def parse_config(config: Dict[Any, Any]) -> UserRestrictionsModuleConfig:
        try:
            return cattr.structure(config, UserRestrictionsModuleConfig)
        except (TypeError, ValueError) as e:
            raise ConfigError("Failed to parse module config") from e

    async def callback_user_may_create_room(self, user: str) -> bool:
        return True

    async def callback_user_may_invite(
        self, inviter: str, invitee: str, room_id: str
    ) -> bool:
        return True
