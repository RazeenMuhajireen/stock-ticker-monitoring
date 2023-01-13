import redis

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    )


cron_jobs = r.zrange('cron_jobs', 0, -1)

for job in cron_jobs:
    split = job.split('|')
    print(split)