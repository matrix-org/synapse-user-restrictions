from importlib.metadata import PackageNotFoundError, version

from synapse_user_restrictions.module import UserRestrictionsModule

__all__ = ["UserRestrictionsModule"]

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass
