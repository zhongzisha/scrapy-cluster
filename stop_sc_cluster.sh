for node in master3 slave1 slave2 slave3; do
  echo $node
  # rsync -av -e ssh --exclude='venv' --exclude='__pycache__' ../scrapy-cluster --exclude='*.pyc' ${node}:~/
  # ssh $node "cd ~/scrapy-cluster; bash start_all.sh; "
  ssh $node "tmux kill-session -t sc"
done