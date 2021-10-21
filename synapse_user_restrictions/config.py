import abc
import enum
import re
from enum import Enum
from typing import Any, List, Pattern, Set, Type

import attr
import cattr
from attr import Attribute
from cattr import Converter


def make_cattr_converter() -> Converter:
    """
    Creates a cattr `Converter` instance, with custom registered hooks for
    regular expressions.
    """
    converter = cattr.Converter()

    def regex_structure_hook(value: Any, _kind: Type[Pattern[str]]) -> Pattern[str]:
        if not isinstance(value, str):
            raise ValueError("Regex patterns should be specified as strings.")

        try:
            return re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex '{value}': {e.msg}")

    converter.register_structure_hook(Pattern[str], regex_structure_hook)

    return converter


def check_all_permissions_understood(
    _instance: Any, _attribute: "Attribute[Set[str]]", permissions: Set[str]
) -> None:
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
    allow: Set[str] = attr.ib(factory=set, validator=check_all_permissions_understood)

    # permissions to deny
    deny: Set[str] = attr.ib(factory=set, validator=check_all_permissions_understood)

    def apply(self, user_id: str, permission: str) -> RuleResult:
        if not self.match.fullmatch(user_id):
            return RuleResult.NoDecision

        if permission in self.allow:
            return RuleResult.Allow

        if permission in self.deny:
            return RuleResult.Deny

        return RuleResult.NoDecision


@attr.s(auto_attribs=True, frozen=True)
class UserRestrictionsModuleConfig:
    """
    The root-level configuration.
    """

    # A list of rules. Right now, only regex matching rules are supported,
    # but in the future, we can use Union[RegexMatchRule, OtherRule] to be
    # able to support other kinds of rules and cattr will disambiguate them
    # as long as they have unique fields.
    rules: List[RegexMatchRule]

    # If the rules don't make a judgement about a user for a permission,
    # this is a list of denied-by-default permissions.
    default_deny: Set[str] = attr.ib(
        factory=set, validator=check_all_permissions_understood
    )


INVITE = "invite"
CREATE_ROOM = "create_room"
ALL_UNDERSTOOD_PERMISSIONS = frozenset({INVITE, CREATE_ROOM})
