#!/bin/bash
PORT=8000
lsof -n -i4TCP:${PORT} | grep LISTEN | awk '{ print $2 }' | xargs kill
