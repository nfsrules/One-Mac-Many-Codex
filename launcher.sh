#!/bin/bash
# Standalone macOS launcher. No Python, downloads, credential copying or migration.
set -euo pipefail

fail() { printf 'Launcher stopped: %s\n' "$*" >&2; exit 1; }

no_symlinks() {
  local current="$1"
  [[ "$current" = /* ]] || fail 'Expected an absolute profile path.'
  while [[ "$current" != / ]]; do
    [[ ! -L "$current" ]] || fail "Symlinked profile path: $current"
    current="$(/usr/bin/dirname "$current")"
  done
}

private_dir() {
  no_symlinks "$1"
  /bin/mkdir -p "$1"
  [[ -d "$1" && "$(/usr/bin/stat -f '%u' "$1")" = "$(/usr/bin/id -u)" ]] || fail 'Invalid directory owner.'
  /bin/chmod 700 "$1"
}

private_file() {
  [[ ! -L "$1" && -f "$1" ]] || fail "Expected a regular file: $1"
  [[ "$(/usr/bin/stat -f '%u' "$1")" = "$(/usr/bin/id -u)" ]] || fail 'Invalid file owner.'
  [[ "$(/usr/bin/stat -f '%Lp' "$1")" = 600 ]] || fail "Expected permissions 600: $1"
}

prepare_profile() {
  local root="$1" marker="$1/.launcher-owner" config="$1/codex/config.toml"
  no_symlinks "$root"
  if [[ -e "$root" ]]; then
    private_file "$marker"
    [[ "$(/bin/cat "$marker")" = personal-codex-launcher-v1 ]] || fail 'Unrecognized profile; nothing changed.'
  fi
  private_dir "$root"
  if [[ ! -e "$marker" ]]; then
    (set -o noclobber; printf 'personal-codex-launcher-v1\n' > "$marker")
  fi
  private_dir "$root/codex"
  private_dir "$root/desktop"
  if [[ ! -e "$config" && ! -L "$config" ]]; then
    (set -o noclobber; printf 'cli_auth_credentials_store = "file"\n' > "$config")
  fi
  private_file "$config"
  /usr/bin/grep -Fqx 'cli_auth_credentials_store = "file"' "$config" || fail 'Restore the file credential-store setting; config was not overwritten.'
}

main() {
  local action="${1:-launch}" app='' executable='' task_home="$HOME" root process_list command_line
  [[ $# -le 1 ]] || fail 'Usage: launcher.sh [launch|check|status]'
  case "$action" in launch|check|status) ;; *) fail 'Usage: launcher.sh [launch|check|status]' ;; esac
  [[ "$(/usr/bin/uname -s)" = Darwin ]] || fail 'macOS is required.'
  [[ "$(/usr/bin/id -u)" != 0 ]] || fail 'Run as yourself, without sudo.'
  root="$task_home/Library/Application Support/Personal Codex Second Account"
  for executable in ChatGPT Codex; do
    app="/Applications/$executable.app"
    [[ -x "$app/Contents/MacOS/$executable" ]] && break
    app=''
  done
  [[ -n "$app" ]] || fail 'Install the official ChatGPT/Codex app in /Applications.'
  printf 'Official app: %s\nSecond-account data: %s\n' "$app" "$root"
  if [[ "$action" = check ]]; then
    printf 'Read-only check complete. No folders created or app launched.\n'
    return
  fi
  if [[ "$action" = launch ]]; then
    umask 077
    prepare_profile "$root"
    /bin/mkdir "$root/.shell-launch.lock" 2>/dev/null || fail 'Another shell launch is in progress, or a stale .shell-launch.lock remains after an interrupted launch.'
    trap '/bin/rmdir "$root/.shell-launch.lock" 2>/dev/null || true' EXIT
  fi
  process_list="$(/bin/ps -axo command=)" || fail 'Process inspection unavailable. Run from your own Terminal or Finder.'
  while IFS= read -r command_line; do
    if [[ "$command_line" = "$app/Contents/MacOS/$executable "* && "$command_line" = *"--user-data-dir=$root/desktop"* ]]; then
      printf 'Second account is already running. Select its window using Mission Control.\n'
      if [[ "$action" = launch ]]; then /bin/rmdir "$root/.shell-launch.lock"; trap - EXIT; fi
      return
    fi
  done <<< "$process_list"
  if [[ "$action" = status ]]; then printf 'Second account is not running.\n'; return; fi
  /usr/bin/env -i HOME="$task_home" USER="$(/usr/bin/id -un)" LOGNAME="$(/usr/bin/id -un)" \
    PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 \
    /usr/bin/open -n --env "CODEX_HOME=$root/codex" \
    --env "CODEX_ELECTRON_USER_DATA_PATH=$root/desktop" \
    -a "$app" --args "--user-data-dir=$root/desktop"
  /bin/rmdir "$root/.shell-launch.lock"
  trap - EXIT
  printf 'Launched. Verify the new window is signed out, then sign into your SECOND account.\n'
}

if [[ "${BASH_SOURCE[0]}" = "$0" ]]; then main "$@"; fi
