# Synapse User Restrictions Module

This module allows restricting users, that match given regular expressions,
from performing actions such as creating rooms or sending invites.


## Installation

From the virtual environment that you use for Synapse, install this module with:
```shell
pip install path/to/synapse-user-restrictions
```

Then alter your homeserver configuration, adding to your `modules` configuration:
```yaml
modules:
  - module: synapse_user_restrictions.UserRestrictionsModule
    config:
      # List of rules. Earlier rules have a higher priority than later rules.
      rules:
        - match: "@admin.*:example.org"
          allow: [invite, create_room]

        - match: "@assistant.*:example.org"
          allow: [invite]

      # If no rules match, then these permissions are denied.
      # All other permissions are allowed by default.
      default_deny: [invite, create_room]
```

In this example:
- `@adminalice:example.org` could create rooms and invite users to
rooms;
- `@assistantbob:example.org` could invite users to rooms but NOT create rooms;
and
- `@plainoldjoe:example.org` could neither create rooms nor invite users.

### Configuration

Rules are applied top-to-bottom, with the first matching rule being used.

A rule matches if the regular expression (written in `match`) fully matches the
user's Matrix ID, and the permission being sought is either in the `allow` list
or the `deny` list.
The regular expression must match the full Matrix ID and not just a portion of it.

Valid permissions (as at the time of writing) are:

- `invite`: the user is trying to invite another user to a room
- `create_room`: the user is trying to create a room

If no rules match, then `default_deny` is consulted;
`default_deny` is useful for only allowing a select few listed user patterns to
be allowed to use certain features.


## Development

In a virtual environment, use:
```shell
pip install -e .[dev]
```

To run the unit tests, you can either use:
```shell
tox -e py
```
or
```shell
trial tests
```

To run the linters and `mypy` type checker, use `./scripts-dev/lint.sh`.

Don't forget to create a changelog entry ('news fragment') for your changes; consult
the [Synapse contributing guide][synapse_changelog_help] for more information.

[synapse_changelog_help]: https://matrix-org.github.io/synapse/latest/development/contributing_guide.html#changelog


## Releasing

The exact steps for releasing will vary; but this is an approach taken by the
Synapse developers (assuming a Unix-like shell):

 1. Set a shell variable to the version you are releasing (this just makes
    subsequent steps easier):
    ```shell
    version=X.Y.Z
    ```

 2. Branch off from `main` to `release-vX.Y.Z`:
    ```shell
    git checkout main
    git checkout -b release-v$version
    ```

 3. Update `setup.py` so that the `version` is correct.

 4. Invoke `towncrier --version v$version` to generate the changelog.
    It's OK for `towncrier` to remove the newsfragments.

 5. Check the changelog `CHANGES.md` and make corrections if necessary.

 6. Stage the changed files and commit.
    ```shell
    git add -u
    git commit -m v$version -n
    ```

 7. Push your changes.
    ```shell
    git push -u origin release-v$version
    ```

 8. You can still check the changelog here (or even ask others to do so).
    If you make any corrections, stage, commit and push them once more.

 9. When ready, create a signed tag for the release:
    ```shell
    git tag -s v$version
    ```
    Base the tag message on the changelog.

10. Push the tag.
    ```shell
    git push origin tag v$version
    ```

11. If applicable:
    Create a *release*, based on the tag you just pushed, on GitHub or GitLab.

12. If applicable:
    Create a source distribution and upload it to PyPI.
