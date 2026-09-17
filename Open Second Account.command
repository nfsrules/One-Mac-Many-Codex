#!/bin/bash
set -eu
cd -- "$(/usr/bin/dirname -- "$0")"
if ! /bin/bash ./launcher.sh launch; then
  printf '\nLauncher stopped. Press Return to close.\n'
  read -r unused
  exit 1
fi
