from typing import Dict, List

from setuptools import setup

BASE_DEPENDENCIES: List[str] = ["attrs"]

TEST_DEPENDENCIES: List[str] = ["matrix-synapse>=1.44.0", "tox", "twisted"]

MYPY_DEPENDENCIES: List[str] = [
    "mypy==0.910",
    "types-setuptools",
]

LINT_DEPENDENCIES: List[str] = [
    "black==21.9b0",
    "flake8==4.0.1",
    "isort==5.9.3",
]

DEV_DEPENDENCIES: List[str] = (
    LINT_DEPENDENCIES + TEST_DEPENDENCIES + MYPY_DEPENDENCIES + ["towncrier"]
)

EXTRA_DEPENDENCIES: Dict[str, List[str]] = {
    "dev": DEV_DEPENDENCIES,
    "lint": LINT_DEPENDENCIES,
    "test": TEST_DEPENDENCIES,
    "mypy": MYPY_DEPENDENCIES,
}

setup(
    name="synapse_user_restrictions",
    description="This module allows restricting users from performing actions"
    " such as creating rooms or sending invites.",
    version="0.0.0",
    packages=["synapse_user_restrictions"],
    url="https://github.com/matrix-org/synapse-user-restrictions",
    classifiers=[
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=BASE_DEPENDENCIES,
    extras_require=EXTRA_DEPENDENCIES,
)
