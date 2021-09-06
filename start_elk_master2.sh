LOG_DIR=/tmp/scrapy-cluster/logs/

# rm -rf $LOG_DIR
# mkdir -p ${LOG_DIR}
if [ ! -d ${LOG_DIR} ]; then
  mkdir -p ${LOG_DIR}
fi

if [ ! -d venv ]; then
  sudo apt install -y build-essential gcc g++ python3-virtualenv python3-dev
  virtualenv venv
  source venv/bin/activate
  pip install pip -U
  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  # pip install -r requirements_has_versions.txt
  pip install -r requirements.txt
  pip install -e scutils-1.2.0
else
  source venv/bin/activate
fi

SESSION=elk

tmux new-session -d -s $SESSION bash      # 开启一个会话，单个窗口
tmux split-window -h bash     # 水平分裂一个窗口，左右两个窗口
tmux select-pane -L           # 选中左边窗口
tmux split-window -v bash     # 左边窗口分裂成上下两个窗口
tmux select-pane -U           # 选中上面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
tmux select-pane -D           # 移动到下面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
tmux select-pane -R           # 选中左边窗口
tmux split-window -v bash     # 右边窗口分裂成上下两个窗口
tmux select-pane -U           # 选中上面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
tmux select-pane -D           # 移动到下面窗口
tmux split-window -v bash     # 分裂成上下两个窗口
#sends keys to first and second terminals
# 从左到右，从上到下，编号依次为0,1,2,3,4,5,6,7
tmux send -t elk:0.0 "cd /home/ubuntu/es/elasticsearch-7.14.1/bin/; ./elasticsearch" C-m
tmux send -t elk:0.1 "cd /home/ubuntu/es/logstash-7.14.1/; ./bin/logstash -f ./config/logstash_scrapy_cluster.conf" C-m
tmux send -t elk:0.2 "cd /home/ubuntu/es/kibana-7.14.1-linux-x86_64/bin/; ./kibana" C-m
tmux send -t $SESSION:0.3 "docker ps" C-m
tmux send -t $SESSION:0.4 "cd /home/ubuntu/es/filebeat-7.14.1-linux-x86_64/; ./filebeat" C-m
tmux send -t $SESSION:0.5 "ssh slave1 \"cd /home/ubuntu/filebeat-7.14.1-linux-x86_64/; ./filebeat\"" C-m
tmux send -t $SESSION:0.6 "ssh slave2 \"cd /home/ubuntu/filebeat-7.14.1-linux-x86_64/; ./filebeat\"" C-m
tmux send -t $SESSION:0.7 "ssh slave3 \"cd /home/ubuntu/filebeat-7.14.1-linux-x86_64/; ./filebeat\"" C-m

# tmux -2 attach-session -d

tmux detach   # 关闭当前tmux窗口，但是会后台运行
# tmux kill-windows  # 关闭所有会话

#tmux new-session -d bash \
#tmux send -t $SESSION:0.0 "source venv/bin/activate | cd kafka-monitor; ls -alt" C-m
