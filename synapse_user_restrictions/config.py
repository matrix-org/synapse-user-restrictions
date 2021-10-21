import abc
import enum
import re
from enum import Enum
from typing import Any, Dict, Iterable, List, Pattern, Set, Type, TypeVar, cast

import attr

ConfigDict = Dict[str, Any]


def check_and_compile_regex(value: Any) -> Pattern[str]:
    """
    Given a value from the configuration, which is validated to be a string,
    compiles and returns a regular expression.
    """
    if not isinstance(value, str):
        raise ValueError("Regex patterns should be specified as strings.")

    try:
        return re.compile(value)
    except re.error as e:
        raise ValueError(f"Invalid regex '{value}': {e.msg}")


def check_all_permissions_understood(permissions: Iterable[str]) -> None:
    """
    Checks that all the permissions contained in the list of permissions are
    ones that we understand and recognise.
    """
    for permission in permissions:
        if permission not in ALL_UNDERSTOOD_PERMISSIONS:
            nice_list_of_understood_permissions = ", ".join(
                sorted(ALL_UNDERSTOOD_PERMISSIONS)
            )
            raise ValueError(
                f"{permission!r} is not a permission recognised "
                f"by the User Restrictions module; "
                f"try one of: {nice_list_of_understood_permissions}"
            )


T = TypeVar("T")


def check_list_elements(
    input: List[Any], type_to_check: Type[T], failure_message: str
) -> List[T]:
    """
    Checks that all elements in a list are of the specified type, casting it upon
    success.
    """
    for ele in input:
        if not isinstance(ele, type_to_check):
            raise ValueError(failure_message)

    return cast(List[T], input)


class RuleResult(Enum):
    NoDecision = enum.auto()
    Allow = enum.auto()
    Deny = enum.auto()


class Rule(abc.ABC):
    def apply(self, user_id: str, permission: str) -> RuleResult:
        """
        Applies a rule, returning a result.

        Arguments:
            user_id: the full user ID (@bob:example.org) of the user being checked
            permission: permission string identifying what kind of permission
                is being sought
        """
        ...


@attr.s(auto_attribs=True, frozen=True)
class RegexMatchRule(Rule):
    """
    A single rule that performs a regex match.
    """

    # regex pattern to match users against
    match: Pattern[str]

    # permissions to allow
    allow: Set[str]

    # permissions to deny
    deny: Set[str]

    def apply(self, user_id: str, permission: str) -> RuleResult:
        if not self.match.fullmatch(user_id):
            return RuleResult.NoDecision

        if permission in self.allow:
            return RuleResult.Allow

        if permission in self.deny:
            return RuleResult.Deny

        return RuleResult.NoDecision

    @staticmethod
    def from_config(rule: ConfigDict) -> "RegexMatchRule":
        if "match" not in rule:
            raise ValueError("Rules must have a 'match' field")
        match_pattern = check_and_compile_regex(rule["match"])

        if "allow" in rule:
            if not isinstance(rule["allow"], list):
                raise ValueError("Rule's 'allow' field must be a list.")

            allow_list = check_list_elements(
                rule["allow"], str, "Rule's 'allow' field must be a list of strings."
            )
            check_all_permissions_understood(allow_list)
        else:
            allow_list = []

        if "deny" in rule:
            if not isinstance(rule["deny"], list):
                raise ValueError("Rule's 'deny' field must be a list.")

            deny_list = check_list_elements(
                rule["deny"], str, "Rule's 'deny' field must be a list of strings."
            )
            check_all_permissions_understood(deny_list)
        else:
            deny_list = []

        return RegexMatchRule(
            match=match_pattern, allow=set(allow_list), deny=set(deny_list)
        )


@attr.s(auto_attribs=True, frozen=True)
class UserRestrictionsModuleConfig:
    """
    The root-level configuration.
    """

    # A list of rules.
    rules: List[RegexMatchRule]

    # If the rules don't make a judgement about a user for a permission,
    # this is a list of denied-by-default permissions.
    default_deny: Set[str]

    @staticmethod
    def from_config(config_dict: ConfigDict) -> "UserRestrictionsModuleConfig":
        if "rules" not in config_dict:
            raise ValueError("'rules' list not specified in module configuration.")

        rules = []
        for index, rule in enumerate(config_dict["rules"]):
            if not isinstance(rule, dict):
                raise ValueError(
                    f"Rules should be dicts. "
                    f"Rule number {index + 1} is not (found: {type(rule).__name__})."
                )

            # For now, only one kind of rule exists
            # In the future, we can check which keys exist in the rule to determine
            # what kind it is (each rule kind should have a unique main key).
            rules.append(RegexMatchRule.from_config(rule))

        if not isinstance(config_dict["rules"], list):
            raise ValueError("'rules' should be a list.")

        default_deny = config_dict.get("default_deny")
        if default_deny is not None and not isinstance(default_deny, list):
            raise ValueError("'default_deny' should be a list (or unspecified).")

        return UserRestrictionsModuleConfig(
            rules=rules,
            default_deny=set(default_deny) if default_deny is not None else set(),
        )


INVITE = "invite"
CREATE_ROOM = "create_room"
ALL_UNDERSTOOD_PERMISSIONS = frozenset({INVITE, CREATE_ROOM})
