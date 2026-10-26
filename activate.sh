#!/bin/bash
# Activate script for TTT-mail-api
# Usage: source ./activate.sh

# Activate the virtual environment
source .venv/bin/activate

# Clear the command hash table to ensure python3 is resolved from venv
hash -r

# Verify activation
echo "✓ Virtual environment activated"
echo "Python path: $(which python3)"
echo "Python version: $(python3 --version)"
echo ""
echo "You can now use:"
echo "  python3 manage.py runserver"
echo "  python3 manage.py makemigrations"
echo "  python3 manage.py migrate"
