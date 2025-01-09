"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-10517.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com',
    port=10517,
    decode_responses=True,
    username="default",
    password="ejjWDDXsKPbXenk5YLNLOghtkVMZfF4K",
)

success = r.hset('users', 'shakil', 'yolobunda')
# True

result = r.hget('users', 'shakil')
print(result)
# >>> bar

