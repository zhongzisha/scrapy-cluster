# Flask configuration
FLASK_LOGGING_ENABLED = True
FLASK_PORT = 5343 # Hex representation of 'SC'

# Redis host configuration
# REDIS_HOST = 'localhost'    # 单机
# REDIS_HOST = 'redis-service'    # docker
REDIS_HOST = 'master'    # 集群
REDIS_PORT = 6379
REDIS_DB = 0

# Kafka server information ------------
# KAFKA_HOSTS = ['localhost:9092']  # 单机
KAFKA_HOSTS = ['master:9092','slave2:9092','slave3:9092']  # 集群
KAFKA_TOPIC_PREFIX = 'demo'
KAFKA_FEED_TIMEOUT = 10

KAFKA_CONSUMER_AUTO_OFFSET_RESET = 'latest'
KAFKA_CONSUMER_TIMEOUT = 50
KAFKA_CONSUMER_COMMIT_INTERVAL_MS = 5000
KAFKA_CONSUMER_AUTO_COMMIT_ENABLE = True
KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
KAFKA_CONSUMER_SLEEP_TIME = 1

KAFKA_PRODUCER_TOPIC = 'demo.incoming'
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking

# logging setup
LOGGER_NAME = 'rest-service'
LOG_DIR = 'logs'
LOG_FILE = 'rest_service.log'
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUPS = 5
LOG_STDOUT = False  # True
LOG_USE_JSON = True # False
LOG_LEVEL = 'DEBUG'

# internal configuration
SLEEP_TIME = 5
HEARTBEAT_TIMEOUT = 120
DAEMON_THREAD_JOIN_TIMEOUT = 10
WAIT_FOR_RESPONSE_TIME = 5
SCHEMA_DIR = 'schemas/'
