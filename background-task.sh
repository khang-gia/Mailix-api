#!/bin/bash
spath=`readlink -f "${BASH_SOURCE:-$0}"`
DIR_PATH=`dirname $spath`
cd $DIR_PATH

ps aux | grep -i 'manage.py process_tasks' | awk '{ print $2 }' | xargs kill

source .venv/bin/activate

nohup python3 manage.py process_tasks -v 3 --duration 3600