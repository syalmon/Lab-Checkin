#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"
exec uv run --locked --no-sync report_entry.py "$@"
