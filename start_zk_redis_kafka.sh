#docker stop kafka-service && docker rm kafka-service
#
#docker stop redis-service && docker rm redis-service
#
#docker stop zookeeper-service && docker rm zookeeper-service
#
#docker run -d --name zookeeper-service -p 2181:2181 zookeeper
#
#docker run -d --name redis-service -p 6379:6379 redis
#
#docker run -d --name kafka-service -e KAFKA_ADVERTISED_PORT=9092 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
#-e KAFKA_BROKER_ID=1 -e KAFKA_ZOOKEEPER_CONNECT=zk:2181 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
#-e KAFKA_LISTENERS=PLAINTEXT://:9092 --link zookeeper-service:zk  -p 9092:9092 -t wurstmeister/kafka


ssh slave1 "cd /opt/apache-zookeeper-3.7.0-bin/bin; ./zkServer.sh start"
sleep 2
ssh slave2 "cd /opt/apache-zookeeper-3.7.0-bin/bin; ./zkServer.sh start"
sleep 2
ssh slave3 "cd /opt/apache-zookeeper-3.7.0-bin/bin; ./zkServer.sh start"
sleep 2


SESSION=kafka
tmux new-session -d -s $SESSION bash      # 开启一个会话，单个窗口
tmux split-window -h bash     # 水平分裂一个窗口，左右两个窗口
tmux select-pane -L           # 选中左边窗口
tmux split-window -v bash     # 左边窗口分裂成上下两个窗口
tmux select-pane -R           # 选中左边窗口
tmux split-window -v bash     # 右边窗口分裂成上下两个窗口
#sends keys to first and second terminals
# 从左到右，从上到下，编号依次为0,1,2,3,4,5,6,7
tmux send -t $SESSION:0.0 "cd /opt/kafka_2.13-2.8.0/bin/; ./kafka-server-start.sh ../config/server.properties" C-m
sleep 5
tmux send -t $SESSION:0.1 "ssh slave2 \"cd /opt/kafka_2.13-2.8.0/bin/; ./kafka-server-start.sh ../config/server.properties\"" C-m
sleep 5
tmux send -t $SESSION:0.2 "ssh slave3 \"cd /opt/kafka_2.13-2.8.0/bin/; ./kafka-server-start.sh ../config/server.properties\"" C-m

tmux send -t $SESSION:0.3 "top" C-m
# tmux -2 attach-session -d

tmux detach   # 关闭当前tmux窗口，但是会后台运行
# tmux kill-windows  # 关闭所有会话

#tmux new-session -d bash \
#tmux send -t $SESSION:0.0 "source venv/bin/activate | cd kafka-monitor; ls -alt" C-m

