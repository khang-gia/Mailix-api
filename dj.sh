#!/bin/bash
# Django management script wrapper
# This ensures commands always use the venv's Python

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="$SCRIPT_DIR/.venv/bin/python3"

# Run Django management command with venv's Python
$PYTHON "$SCRIPT_DIR/manage.py" "$@"
