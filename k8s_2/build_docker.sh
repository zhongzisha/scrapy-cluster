current_dir=`pwd`
cd ..
docker build -f docker/rest/Dockerfile -t istresearch/scrapy-cluster:rest-1.2.2 .
docker build -f docker/kafka-monitor/Dockerfile -t istresearch/scrapy-cluster:kafka-monitor-1.2.2 .
docker build -f docker/redis-monitor/Dockerfile -t istresearch/scrapy-cluster:redis-monitor-1.2.2 .


docker build -f docker/crawler/Dockerfile -t istresearch/scrapy-cluster:crawler-1.2.3 .

cd $current_dir

