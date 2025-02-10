#!/bin/bash
PORT=8000
lsof -n -i4TCP:${PORT} | grep LISTEN | awk '{ print $2 }' | xargs kill
source ./.venv/bin/activate
gunicorn tttmail.asgi:application -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:${PORT} --workers 3 --timeout 300 --capture-output --error-logfile logs/error.log --access-logfile logs/access.log -D
