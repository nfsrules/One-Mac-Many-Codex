# Security

This is an experimental local launcher, not a security boundary between accounts.
It neither migrates credentials nor modifies the official app. The second profile
contains sensitive account state and must never be included in bug reports or ZIPs.

When reporting an issue, include only the macOS version, official app version,
Python version and a redacted error message. Never attach `auth.json`, API keys,
login URLs containing codes, account identifiers, profile folders or session logs.

For a suspected credential exposure, use GitHub's private vulnerability reporting
if enabled for the repository. Otherwise ask the maintainer for a private reporting
channel without posting the secret or exploit details publicly.

No third-party dependency audit or successful end-to-end multi-account login
verification is claimed. See the README for current validation status.
