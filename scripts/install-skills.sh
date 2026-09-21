#!/usr/bin/env bash
# Shim: install-skills.py is the implementation. Git Bash passes a Windows-style
# $0 through, so the backslashes are normalized before dirname sees it.
exec "$(command -v python3 || command -v python)" "$(dirname -- "${0//\\//}")/install-skills.py" "$@"
