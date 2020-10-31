docker build -t istresearch/scrapy-cluster:rest-dev -f docker/rest/Dockerfile .

docker build -t istresearch/scrapy-cluster:kafka-monitor-dev -f docker/kafka-monitor/Dockerfile .

docker build -t istresearch/scrapy-cluster:redis-monitor-dev -f docker/redis-monitor/Dockerfile .

docker build -t istresearch/scrapy-cluster:crawler-dev -f docker/crawler/Dockerfile .
