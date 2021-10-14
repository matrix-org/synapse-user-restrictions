# -*- coding: utf-8 -*-
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
from typing import Any, Dict
from unittest import mock

from synapse.module_api import ModuleApi, UserID

from synapse_user_restrictions.module import UserRestrictionsModule


def create_module(
    config_dict: Dict[Any, Any], server_name: str = "example.com"
) -> UserRestrictionsModule:
    # OSTD is this useful to us?
    def get_qualified_user_id(localpart: str) -> str:
        return UserID(localpart, server_name).to_string()

    # Create a mock based on the ModuleApi spec, but override some mocked functions
    # because some capabilities (interacting with the database,
    # getting the current time, etc.) are needed for running the tests.
    module_api = mock.Mock(spec=ModuleApi)
    module_api.get_qualified_user_id.side_effect = get_qualified_user_id

    config = UserRestrictionsModule.parse_config(config_dict)

    return UserRestrictionsModule(config, module_api)
