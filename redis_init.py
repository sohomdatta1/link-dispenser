import os
import redis

redis_url = ''

if 'NOTDEV' in os.environ:
    redis_url = 'redis://redis.svc.tools.eqiad1.wikimedia.cloud:6379/0'
else:
    redis_url = 'redis://localhost:6379/2'

rediscl = redis.Redis(host='localhost', port=6379, db=2)


if 'NOTDEV' in os.environ:
    rediscl = redis.Redis(
        host='redis.svc.tools.eqiad1.wikimedia.cloud',
        port=6379,
        db=0)

REDIS_KEY_PREFIX = 'mw-toolforge-link-dispenser'
