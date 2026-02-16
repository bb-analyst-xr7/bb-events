#!/bin/sh
set -eu

# Use a repo-local uv cache to avoid permission issues on locked-down home dirs.
UV_CACHE_DIR="${UV_CACHE_DIR:-./.uv-cache}"
export UV_CACHE_DIR

# Forward all args to uv run
exec uv run "$@"
