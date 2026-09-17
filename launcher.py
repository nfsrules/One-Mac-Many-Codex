#!/usr/bin/python3
"""Personal, single-profile Codex launcher. Python standard library only."""
import argparse
import fcntl
import os
from pathlib import Path
import pwd
import stat
import subprocess
import sys

LABEL = "Personal Codex Second Account"
MARKER = b"personal-codex-launcher-v1\n"
CONFIG = b'cli_auth_credentials_store = "file"\n'


def private_directory(path):
    # Refuse symlinks, including symlinked ancestors, before creating anything.
    for part in list(reversed(path.parents)) + [path]:
        if part.is_symlink():
            raise RuntimeError("Refusing a symlinked profile path: " + str(part))
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError("Profile directory is not owned by this user: " + str(path))
    path.chmod(0o700)


def create_private_file(path, content):
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)


def check_private_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise RuntimeError("Expected a private, user-owned regular file: " + str(path))


def prepare(root):
    marker = root / ".launcher-owner"
    if root.exists() or root.is_symlink():
        if root.is_symlink() or not marker.exists():
            raise RuntimeError("Existing profile folder is not recognized; nothing changed.")
        check_private_file(marker)
        if marker.read_bytes() != MARKER:
            raise RuntimeError("Profile marker does not match; nothing changed.")
    private_directory(root)
    if not marker.exists():
        create_private_file(marker, MARKER)
    for name in ("codex", "desktop"):
        private_directory(root / name)
    config = root / "codex" / "config.toml"
    if not config.exists() and not config.is_symlink():
        create_private_file(config, CONFIG)
    check_private_file(config)
    # Keep the explicit file-store setting; do not silently overwrite user edits.
    if CONFIG.decode().strip() not in config.read_text().splitlines():
        raise RuntimeError("Profile config changed: restore cli_auth_credentials_store = \"file\".")


def installed_app():
    for name in ("ChatGPT", "Codex"):
        bundle = Path("/Applications") / (name + ".app")
        if (bundle / "Contents" / "MacOS" / name).is_file():
            return bundle, name
    raise RuntimeError("Install the official ChatGPT/Codex Mac app in /Applications first.")


def running_pids(root, bundle, executable):
    try:
        result = subprocess.run(["/bin/ps", "-axo", "pid=,command="],
                                check=True, capture_output=True, text=True)
    except PermissionError as error:
        raise RuntimeError("Process inspection is blocked in this sandbox. "
                           "Open the .command launcher yourself from Finder.") from error
    binary = str(bundle / "Contents" / "MacOS" / executable)
    flag = "--user-data-dir=" + str(root / "desktop")
    found = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[1].startswith(binary + " ") and flag in parts[1]:
            found.append(int(parts[0]))
    return found


def launch(root, home, bundle):
    # Scoped child environment, never a global shell setting or launchctl setting.
    # In particular, do not inherit API keys or the current agent's CODEX_* values.
    user = pwd.getpwuid(os.getuid()).pw_name
    env = {"HOME": str(home), "USER": user, "LOGNAME": user,
           "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "en_US.UTF-8"}
    args = ["/usr/bin/open", "-n",
            "--env", "CODEX_HOME=" + str(root / "codex"),
            "--env", "CODEX_ELECTRON_USER_DATA_PATH=" + str(root / "desktop"),
            "-a", str(bundle), "--args", "--user-data-dir=" + str(root / "desktop")]
    subprocess.run(args, env=env, check=True, timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("launch", "status", "check"), default="launch")
    args = parser.parse_args()
    if sys.platform != "darwin":
        raise RuntimeError("This launcher is for macOS only.")
    home = Path(pwd.getpwuid(os.getuid()).pw_dir)
    root = home / "Library" / "Application Support" / LABEL
    bundle, executable = installed_app()
    print("Official app:", bundle)
    print("Second-account data:", root)
    if args.action == "check":
        print("Read-only check complete. No folders created and no app launched.")
        return
    if args.action == "status":
        pids = running_pids(root, bundle, executable)
        print("Second instance PIDs:", pids or "not running")
        print("Profile initialized:", (root / ".launcher-owner").exists())
        return
    os.umask(0o077)
    prepare(root)
    lock_path = root / ".launch.lock"
    fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if running_pids(root, bundle, executable):
            print("Second account is already open. Select its window using Mission Control.")
            return
        launch(root, home, bundle)
    print("Launched. Sign in with your SECOND account in the new window.")
    print("Check the account email before starting work. This launcher never copies credentials.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print("Launcher stopped:", error, file=sys.stderr)
        sys.exit(1)
