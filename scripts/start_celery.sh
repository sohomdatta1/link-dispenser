#!/bin/bash
celery -A jobs.celery_app worker --loglevel INFO --concurrency=50 -n worker@ld-sodium