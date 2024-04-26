#!/bin/bash
celery -A jobs.celery_app worker --loglevel INFO -n worker@ld-sodium