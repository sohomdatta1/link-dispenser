#!/bin/sh
tmux new-session -d './scripts/start_celery.sh'
tmux split-window -v './scripts/start_gunicorn.sh'
tmux split-window -h 'cd client && npm run build:dev'
tmux -2 attach-session -d