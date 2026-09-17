# One Mac, Many Codex

A small, inspectable launcher for a second Codex account alongside your existing account on macOS. Uses the official installed ChatGPT/Codex app, with a standalone shell launcher and an optional Python alternative. No third-party account manager, credential copying, or app modification.

## Why this exists

Troubled by the OpenAI 20x upgrade pause and need more Codex usage? Want to stay with Codex without constantly logging out and back in?

This launcher lets you open a second account alongside your existing one on the same Mac, with separate account data for each.

## Requirements

- macOS with the official `ChatGPT.app` or `Codex.app` in `/Applications`.
- No extra runtime for the shell launcher: it uses the Bash and system tools included with macOS.
- Python 3.9 or newer only if you choose the Python launcher or run the Python test suite.
- Your own second account for the second window.

## Quick start

1. Download this repository using **Code → Download ZIP**, or clone it.
2. Unzip and keep the files together in a permanent folder.
3. Leave your usual Codex window open.

### Option 1: Shell launcher

Double-click **Open Second Account.command**, or run this from the repository folder:

```sh
bash launcher.sh launch
```

If the double-click file lost its executable permission during download, run `chmod +x "Open Second Account.command"`, or use the command above.

### Option 2: Python launcher

With Python 3.9 or newer installed, run:

```sh
python3 launcher.py launch
```

Both options use the same second-account profile. Choose either one; they do not create separate additional accounts. Avoid starting both launchers at the same instant.

### Sign in

The new window should start signed out. Sign in with your second account, selecting the correct account in the browser login flow. Check the account email in both windows before starting work.

If the new window unexpectedly shows the original account, stop and investigate; do not sign out of that window. The official app may give both instances the same Dock icon. Select their windows using Mission Control, and always open the second account through a launcher.

## How it works

```text
Your usual app launch → existing account and existing data
This launcher        → second account in a dedicated data folder
```

The launcher passes two environment settings only to the new application process:

- `CODEX_HOME`: a separate config and credential directory.
- `CODEX_ELECTRON_USER_DATA_PATH`: a separate desktop application data directory.

It also passes `--user-data-dir` to the official desktop app. All second-account state is outside this repository:

```text
~/Library/Application Support/Personal Codex Second Account/
├── codex/      # settings, account credentials and Codex state
└── desktop/    # desktop app state
```

The launcher creates private directories (0700) and its initial files (0600), and sets `cli_auth_credentials_store = "file"` for this profile. Credentials are sensitive local files; do not share or commit that state directory. The official credential-storage documentation is at https://learn.chatgpt.com/docs/auth#credential-storage.

It does not read or copy tokens, move your original profile, edit shell startup files, create symlinks to your primary configuration, install software, download updates, or make network requests itself. The official app handles login, networking and its own updates. Inherited API keys and agent-specific environment variables are not passed through.

## Commands

Run from this repository folder:

```sh
bash launcher.sh check      # read-only app discovery; no launch
bash launcher.sh launch     # open the second account with no Python
bash launcher.sh status     # report whether the second process is running
```

Python alternative:

```sh
python3 launcher.py check    # read-only app discovery; no launch
python3 launcher.py launch   # create/use the second profile and open the app
python3 launcher.py status   # report whether the second process is running
python3 -m unittest -v       # offline tests using temporary folders
```

The launcher refuses unrecognized existing profile folders and symlinked profile paths. It stops if its explicit file-based credential-store setting has been removed instead of overwriting your changes.

## Safety by design

The launcher is deliberately small and easy to inspect:

- Uses macOS system tools or Python's standard library, with no third-party packages.
- Launches the official installed app without modifying it.
- Keeps the second account's data in a separate, private folder.
- Does not read, copy or swap your credentials, or migrate your existing setup.
- Has no telemetry, downloads or automatic updates of its own.

**Two 5x subscriptions are still two separate 5x allowances—not the same as a 20x plan.**

## Troubleshooting

If process inspection is blocked, run the launcher from your own Terminal or Finder.

If a shell launch is forcibly interrupted, an empty `.shell-launch.lock` directory may remain inside the second-account state folder. After confirming no launch is in progress, remove only that empty directory with `rmdir`.

## Validation status

**Experimental:** offline safety tests pass, but simultaneous signed-in accounts have not yet been verified end to end. The desktop isolation setting is an implementation detail that may change after an app update. This project is independent of OpenAI and does not merge subscription allowances.

Eleven offline tests cover private file permissions, preservation of existing data, refusal of unknown folders and symlinks, changed auth-store configuration, environment isolation, and process detection, including shell profile preparation and refusal paths. App discovery was checked on a Mac with the official ChatGPT app. Live testing stopped before opening an app because the test environment blocked process inspection. No completed two-account login test is claimed.

## Removal

Deleting this repository removes the launcher only. It leaves the second account's state intact. There is deliberately no automatic migration, cleanup or deletion command. Keep an independent backup before manually removing any account data.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). MIT licensed. Written independently; no code from AI Profiles is included.
