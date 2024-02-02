#!/bin/bash
celery -A jobs.celery_app worker --loglevel INFO --without-gossip --without-mingle --without-heartbeat