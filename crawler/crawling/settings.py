from __future__ import absolute_import

# This file houses all default settings for the Crawler
# to override please use a custom localsettings.py file

# Scrapy Cluster Settings
# ~~~~~~~~~~~~~~~~~~~~~~~

# Redis host configuration
# REDIS_HOST = 'localhost'    # 单机
# REDIS_HOST = 'redis-service'    # docker
REDIS_HOST = 'master'  # 集群
REDIS_PORT = 6379
REDIS_DB = 0

# Kafka server information
# KAFKA_HOSTS = ['localhost:9092']  # 单机
KAFKA_HOSTS = ['master:9092', 'slave2:9092', 'slave3:9092']  # 集群
KAFKA_TOPIC_PREFIX = 'demo'
KAFKA_APPID_TOPICS = False
# base64 encode the html body to avoid json dump errors due to malformed text
KAFKA_BASE_64_ENCODE = True
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking

ZOOKEEPER_ASSIGN_PATH = '/scrapy-cluster/crawler/'
ZOOKEEPER_ID = '1'
# 　ZOOKEEPER_HOSTS = 'localhost:2181'   # 单机
ZOOKEEPER_HOSTS = 'slave1:2181,slave2:2181,slave3:2181'  # 集群  zkServer.sh status

PUBLIC_IP_URL = 'http://ip.42.pl/raw'
IP_ADDR_REGEX = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# seconds to wait between seeing new queues, cannot be faster than spider_idle time of 5
SCHEDULER_QUEUE_REFRESH = 10

# throttled queue defaults per domain, x hits in a y second window
QUEUE_HITS = 10
QUEUE_WINDOW = 60

# we want the queue to produce a consistent pop flow
QUEUE_MODERATED = True

# how long we want the duplicate timeout queues to stick around in seconds
DUPEFILTER_TIMEOUT = 600

# how often to refresh the ip address of the scheduler
SCHEDULER_IP_REFRESH = 60

# whether to add depth >= 1 blacklisted domain requests back to the queue
SCHEDULER_BACKLOG_BLACKLIST = True

'''
----------------------------------------
The below parameters configure how spiders throttle themselves across the cluster
All throttling is based on the TLD of the page you are requesting, plus any of the
following parameters:

Type: You have different spider types and want to limit how often a given type of
spider hits a domain

IP: Your crawlers are spread across different IP's, and you want each IP crawler clump
to throttle themselves for a given domain

Combinations for any given Top Level Domain:
None - all spider types and all crawler ips throttle themselves from one tld queue
Type only - all spiders throttle themselves based off of their own type-based tld queue,
    regardless of crawler ip address
IP only - all spiders throttle themselves based off of their public ip address, regardless
    of spider type
Type and IP - every spider's throttle queue is determined by the spider type AND the
    ip address, allowing the most fined grained control over the throttling mechanism
'''
# add Spider type to throttle mechanism
SCHEDULER_TYPE_ENABLED = True

# add ip address to throttle mechanism
SCHEDULER_IP_ENABLED = True
'''
----------------------------------------
'''

# how many times to retry getting an item from the queue before the spider is considered idle
SCHEUDLER_ITEM_RETRIES = 3

# how long to keep around stagnant domain queues
SCHEDULER_QUEUE_TIMEOUT = 3600

# log setup scrapy cluster crawler
SC_LOGGER_NAME = 'sc-crawler'
SC_LOG_DIR = '/tmp/scrapy-cluster/logs/'
SC_LOG_FILE = 'sc_crawler.log'
SC_LOG_MAX_BYTES = 10 * 1024 * 1024
SC_LOG_BACKUPS = 5
SC_LOG_STDOUT = False  # True
SC_LOG_USE_JSON = True  # False
SC_LOG_LEVEL = 'DEBUG'  # 'INFO'

# stats setup
STATS_STATUS_CODES = True
STATS_RESPONSE_CODES = [
    200,
    404,
    403,
    504,
]
STATS_CYCLE = 5
# from time variables in scutils.stats_collector class
STATS_TIMES = [
    'SECONDS_15_MINUTE',
    'SECONDS_1_HOUR',
    'SECONDS_6_HOUR',
    'SECONDS_12_HOUR',
    'SECONDS_1_DAY',
    'SECONDS_1_WEEK',
]

# Scrapy Settings
# ~~~~~~~~~~~~~~~
# Scrapy settings for distributed_crawling project
#
BOT_NAME = 'crawling'

SPIDER_MODULES = ['crawling.spiders']
NEWSPIDER_MODULE = 'crawling.spiders'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "crawling.distributed_scheduler.DistributedScheduler"

# Store scraped item in redis for post-processing.
ITEM_PIPELINES = {
    'crawling.pipelines.KafkaPipeline': 100,
    'crawling.pipelines.LoggingBeforePipeline': 1,
}

SPIDER_MIDDLEWARES = {
    # disable built-in DepthMiddleware, since we do our own
    # depth management per crawl request
    'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
    'crawling.meta_passthrough_middleware.MetaPassthroughMiddleware': 100,
    'crawling.redis_stats_middleware.RedisStatsMiddleware': 101
}

DOWNLOADER_MIDDLEWARES = {
    # Handle timeout retries with the redis scheduler and logger
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'crawling.redis_retry_middleware.RedisRetryMiddleware': 510,
    # exceptions processed in reverse order
    'crawling.log_retry_middleware.LogRetryMiddleware': 520,
    # custom cookies to not persist across crawl requests
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'crawling.custom_cookies.CustomCookiesMiddleware': 700,
}

# Disable the built in logging in production
LOG_ENABLED = False

# Allow all return codes
HTTPERROR_ALLOW_ALL = True

RETRY_TIMES = 3

DOWNLOAD_TIMEOUT = 10

# Avoid in-memory DNS cache. See Advanced topics of docs for info
DNSCACHE_ENABLED = True

# Local Overrides
# ~~~~~~~~~~~~~~~

try:
    from .localsettings import *
except ImportError:
    pass
