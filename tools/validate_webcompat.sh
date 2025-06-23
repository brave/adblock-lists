#!/usr/bin/env bash

# This script validates the contents of webcompat-exceptions.json
# to ensure it only contains allowed values for the exceptions key.

# Exit loudly and early on error.
set -euo pipefail

# This is from kWebcompatNamesToType in webcompat_exceptions_service.cc
allowed=(
  all-fingerprinting audio canvas device-memory eventsource-pool
  font hardware-concurrency keyboard language media-devices plugins
  referrer screen speech-synthesis usb-device-serial-number user-agent
  webgl webgl2 websockets-pool
)

target_file="brave-lists/webcompat-exceptions.json"

# Resolve repo root so the script works from any current directory.
repo_root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
file_path="${repo_root}/${target_file}"

# Build a single regex like ^(audio|canvas|...)$
allowed_regex="^($(printf '%s|' "${allowed[@]}" | sed 's/|$//'))$"

# Collect any unknown values into a variable.
exceptions=$(jq -r '..|objects|select(has("exceptions"))|.exceptions[]' "$file_path")
unknown=$(printf '%s\n' "$exceptions" | grep -Ev "$allowed_regex" || true)

if [[ -n "$unknown" ]]; then
  echo "::error::Unknown value(s) found in exceptions array:"
  echo "$unknown" | sed 's/^/  - /'
  exit 1
fi

echo "✅  webcompat-exceptions.json contains only allowed values for exceptions key."
