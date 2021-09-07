for node in master slave1 slave2 slave3; do
  echo $node
  # rsync -av -e ssh --exclude='venv' --exclude='__pycache__' ../scrapy-cluster --exclude='*.pyc' ${node}:~/
  ssh $node "tmux kill-session -t sc"
  ssh $node "cd ~/scrapy-cluster; rm -rf venv; "
done