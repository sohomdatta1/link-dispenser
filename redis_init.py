import os
import redis

redis_url = 'redis://localhost:6379/9'

if 'NOTDEV' in os.environ:
    redis_password = os.environ.get('REDIS_PASSWORD', None)
    if redis_password:
        redis_url = f'redis://:{redis_password}@redis:6379/9'
    else:
        redis_url = 'redis://redis:6379/9'
elif 'DOCKER' in os.environ:
    redis_url = 'redis://redis:6379/9'

rediscl = redis.Redis(host='localhost', port=6379, db=9)


if 'NOTDEV' in os.environ:
    redis_password = os.environ.get('REDIS_PASSWORD', None)
    rediscl = redis.Redis(
        host='redis',
        port=6379,
        password=redis_password,
        db=9)
    
elif 'DOCKER' in os.environ:
    rediscl = redis.Redis(host='redis', port=6379, db=9)

REDIS_KEY_PREFIX = 'mw-toolforge-link-dispenser'
