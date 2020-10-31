docker stop kafka-service && docker rm kafka-service
docker stop redis-service && docker rm redis-service
docker stop zookeeper-service && docker rm zookeeper-service
#docker run -d --name zookeeper-service -p 2181:2181 zookeeper
#docker run -d --name redis-service -p 6379:6379 redis
#docker run -d --name kafka-service -e KAFKA_ADVERTISED_PORT=9092 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
#-e KAFKA_BROKER_ID=1 -e KAFKA_ZOOKEEPER_CONNECT=zk:2181 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
#-e KAFKA_LISTENERS=PLAINTEXT://:9092 --link zookeeper-service:zk  -p 9092:9092 -t wurstmeister/kafka
