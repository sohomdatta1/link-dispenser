import requests as req
from redis_init import rediscl as r
from jobs import alive
import random
import os

def ping_sohom(msg):
    if 'DISCORD_WEBHOOK' in os.environ:
        req.post(os.environ.get('DISCORD_WEBHOOK'), json={'content': f"!Error in link-dispenser!: {msg}"}, timeout=1)
        
if __name__ == '__main__':
    try:
        a = random.randint(0, 9)
        b = random.randint(0, 9)
        res = alive.delay(a, b)
        assert(res.get() == a+b)
    except Exception as e:
        ping_sohom(e)
        raise Exception('Failed')
    print('OK')
