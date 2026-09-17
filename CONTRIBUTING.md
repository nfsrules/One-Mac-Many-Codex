# Contributing

Keep the launcher small and dependency-free (macOS shell tools or Python standard library). Do not add credential copying,
automatic account rotation, migration, telemetry or automatic updates.

Run `python3 -m unittest -v` and `bash -n launcher.sh "Open Second Account.command"` before
submitting changes. Tests must use temporary directories and mocked app launches;
never run against real account data. Exercise failure paths that might overwrite
files or mix account state. Document any newly required permissions.

Compatibility reports should specify the official app version and whether both
windows' account identities were verified, without including account identifiers.
