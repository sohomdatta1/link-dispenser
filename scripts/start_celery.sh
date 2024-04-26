#!/bin/bash
celery -A jobs.celery_app worker --loglevel INFO --concurrency=30 -n worker@ld-sodium