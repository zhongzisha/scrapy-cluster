mkdir -p /tmp/scrapy-cluster/logs/
if [ ! -d venv ]; then
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
  pip install -e scutils-1.2.0
fi

tmux new-session -d bash
tmux split-window -h bash
tmux select-pane -L
tmux split-window -v bash
tmux select-pane -U
tmux split-window -v bash
tmux select-pane -D
tmux split-window -v bash
#sends keys to first and second terminals
tmux send -t 0:0.0 "source venv/bin/activate; cd kafka-monitor; python kafka_monitor.py run" C-m
tmux send -t 0:0.1 "source venv/bin/activate; cd redis-monitor; python redis_monitor.py" C-m
tmux send -t 0:0.2 "source venv/bin/activate; cd rest; python rest_service.py" C-m
tmux send -t 0:0.3 "source venv/bin/activate; cd crawler; scrapy runspider crawling/spiders/link_spider.py" C-m
tmux send -t 0:0.4 "source venv/bin/activate; cd kafka-monitor; python kafkadump.py dump -t demo.crawled_firehose -p" C-m


tmux -2 attach-session -d


#tmux new-session -d bash \
#tmux send -t 0:0.0 "source venv/bin/activate | cd kafka-monitor; ls -alt" C-m