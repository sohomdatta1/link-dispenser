web: gunicorn -w 4 -b 0.0.0.0 router:app --access-logfile -
crawljob: celery -A jobs.celery_app worker --loglevel INFO