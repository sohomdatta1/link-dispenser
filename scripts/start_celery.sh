#!/bin/bash
echo "Running without heartbeat, mingle and gossip"
celery -A jobs.celery_app worker --loglevel INFO --without-gossip --without-mingle --without-heartbeat