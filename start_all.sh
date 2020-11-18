LOG_DIR=/tmp/scrapy-cluster/logs/

# rm -rf $LOG_DIR
# mkdir -p ${LOG_DIR}
if [ ! -d ${LOG_DIR} ]; then
  mkdir -p ${LOG_DIR}
fi

if [ ! -d venv ]; then
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
  pip install -e scutils-1.2.0
else
  source venv/bin/activate
fi

SESSION=scrapy_cluster

tmux new-session -d -s $SESSION bash      # 开启一个会话，单个窗口
tmux split-window -h bash     # 水平分裂一个窗口，左右两个窗口
tmux select-pane -L           # 选中左边窗口
tmux split-window -v bash     # 左边窗口分裂成上下两个窗口
tmux select-pane -U           # 选中上面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
tmux select-pane -D           # 移动到下面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
#sends keys to first and second terminals
tmux send -t $SESSION:0.0 "source venv/bin/activate; cd kafka-monitor; python kafka_monitor.py run" C-m
tmux send -t $SESSION:0.1 "source venv/bin/activate; cd redis-monitor; python redis_monitor.py" C-m
tmux send -t $SESSION:0.2 "source venv/bin/activate; cd rest; python rest_service.py" C-m
tmux send -t $SESSION:0.3 "source venv/bin/activate; cd crawler; scrapy runspider crawling/spiders/link_spider.py" C-m
# tmux send -t $SESSION:0.4 "source venv/bin/activate; cd kafka-monitor; python kafkadump.py dump -t demo.crawled_firehose -p" C-m

# tmux -2 attach-session -d

tmux detach   # 关闭当前tmux窗口，但是会后台运行
# tmux kill-windows  # 关闭所有会话

#tmux new-session -d bash \
#tmux send -t $SESSION:0.0 "source venv/bin/activate | cd kafka-monitor; ls -alt" C-m