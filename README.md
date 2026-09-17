# One Mac, Many Codex

A minimal, private macOS launcher for launching two Codex accounts side by side on one Mac.

This initial version provides one dedicated second-account profile alongside your existing account.

A small, inspectable launcher for a second Codex account alongside your existing account on macOS. Uses the official installed ChatGPT/Codex app and Python's standard library. No third-party account manager, credential copying, or app modification.

## Why this exists

Troubled by the OpenAI 20x upgrade pause and need more Codex usage? Want to stay with Codex without constantly logging out and back in?

This launcher lets you open a second account alongside your existing one on the same Mac, with separate account data for each.

This describes the situation that inspired the project, not a live announcement about OpenAI plan availability. It doesn't unlock 20x, reset limits, pool subscriptions, or turn two 5x plans into 20x. Each account keeps its own allowance and remains subject to the provider's terms.

**Experimental:** offline safety tests pass, but simultaneous signed-in accounts have not yet been verified end to end. The desktop isolation setting is an implementation detail that may change after an app update. This project is independent of OpenAI and does not merge subscription allowances.

## Requirements

- macOS with the official `ChatGPT.app` or `Codex.app` in `/Applications`.
- Python 3.9 or newer. The double-click launcher uses `/usr/bin/python3`; if your Python is installed elsewhere, use `python3 launcher.py launch` in Terminal instead.
- Your own second account for the second window.

## Quick start

1. Download this repository using **Code → Download ZIP**, or clone it.
2. Unzip and keep the files together in a permanent folder.
3. Leave your usual Codex window open.
4. Double-click **Open Second Account.command**. If the executable permission was lost during download, run `chmod +x "Open Second Account.command"` from this folder, or use `python3 launcher.py launch`.
5. The new window should start signed out. Sign in with your second account, selecting the correct account in the browser login flow.
6. Check the account email in both windows before starting work.

If the new window unexpectedly shows the original account, stop and investigate; do not sign out of that window. The official app may give both instances the same Dock icon. Select their windows using Mission Control, and always open the second account through this launcher.

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
python3 launcher.py check    # read-only app discovery; no launch
python3 launcher.py launch   # create/use the second profile and open the app
python3 launcher.py status   # report whether the second process is running
python3 -m unittest -v       # offline tests using temporary folders
```

The launcher refuses unrecognized existing profile folders and symlinked profile paths. It stops if its explicit file-based credential-store setting has been removed instead of overwriting your changes.

## Safety and limitations

- Account separation is not a filesystem sandbox. Both instances run as the same macOS user.
- Use separate projects or git worktrees if agents work concurrently; simultaneous edits to the same checkout can conflict.
- Primary-account settings, plugins, history and permissions are not imported. Configure the second account separately.
- Test account separation again after official app updates. No source-to-binary modifications or signatures are involved: the original installed app is launched unchanged.
- Some sandboxes block `ps`, which the launcher uses to avoid opening duplicate second-account instances. Run from your own Terminal or Finder in that case.
- Do not bypass macOS security controls merely to try this project; inspect the source and use a normal trusted local execution workflow.

## Validation status

Seven offline tests cover private file permissions, preservation of existing data, refusal of unknown folders and symlinks, changed auth-store configuration, environment isolation, and process detection. App discovery was checked on a Mac with the official ChatGPT app. Live testing stopped before opening an app because the test environment blocked process inspection. No completed two-account login test is claimed.

## Removal

Deleting this repository removes the launcher only. It leaves the second account's state intact. There is deliberately no automatic migration, cleanup or deletion command. Keep an independent backup before manually removing any account data.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). MIT licensed. Written independently; no code from AI Profiles is included.
