# One Mac, Many Codex

A minimal, private macOS launcher to run two Codex accounts at the same time, without constantly logging out and back in. One shell script you can inspect before running. No Python needed.

## Why this exists

Troubled by the OpenAI 20x upgrade pause and need more Codex usage? Want to stay with Codex without constantly logging out and back in?

This launcher opens a second account alongside your existing one, with separate account data.

## Quick start

You need macOS, the official `ChatGPT.app` or `Codex.app` in `/Applications`, and your own second account.

1. Download this repository using **Code → Download ZIP**, or clone it. Keep the files together.
2. Read [launcher.sh](launcher.sh), then leave your usual Codex window open.
3. From the repository folder, run:

   ```sh
   bash launcher.sh launch
   ```

   You can also double-click **Open Second Account.command**. If needed, first run `chmod +x "Open Second Account.command"`.

4. On first launch, sign into your second account. Check the account email in both windows before starting work. On later launches, the second profile is reused.

If the new window unexpectedly shows your original account, stop; do not sign out of that window. Always use this launcher to open the second account. Mission Control can help distinguish the windows.

## What the script does

- Launches the official installed app unchanged, using macOS system tools.
- Sets `CODEX_HOME`, `CODEX_ELECTRON_USER_DATA_PATH`, and `--user-data-dir` for the new instance, pointing to a dedicated folder:

  ```text
  ~/Library/Application Support/Personal Codex Second Account/
  ├── codex/      # settings, credentials and Codex state
  └── desktop/    # desktop app state
  ```

- Creates private folders (0700) and initial files (0600), and selects file-based credential storage for the second profile.
- Refuses unknown existing profile folders and symlinked paths; preserves existing configuration and data.
- Does not copy credentials, modify your original profile, download software, or send telemetry. The official app handles login and networking.

Keep the profile folder private; never commit it or include it in bug reports. Deleting this repository removes only the launcher, leaving account data intact.

## Checks and troubleshooting

```sh
bash launcher.sh check      # find the installed app without launching it
bash launcher.sh status     # check whether the second instance is running
```

If process inspection is blocked, run from your own Terminal or Finder. If a launch is forcibly interrupted, remove only the empty `.shell-launch.lock` directory inside the profile folder with `rmdir`, after confirming no launch is in progress.

## Validation

Four offline tests cover private permissions, preservation of existing data, and refusal of unknown folders and symlinked paths. Developers can run them with Python 3.9 or newer; Python is not needed to use the launcher:

```sh
python3 -m unittest discover -s tests -v
bash -n launcher.sh "Open Second Account.command"
```

**Experimental:** simultaneous signed-in accounts have not yet been verified end to end. The desktop isolation setting may change after app updates. This project is independent of OpenAI. Use it at your own risk.

Keep contributions small and dependency-free, and run the checks above before submitting changes. [MIT licensed](LICENSE).
