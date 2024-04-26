#!/bin/bash
celery -A jobs.celery_app worker --loglevel INFO --concurrency=20 -n worker@ld-sodium