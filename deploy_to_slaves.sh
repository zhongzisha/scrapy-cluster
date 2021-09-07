#　rsync -avP  --exclude-from=/usr/exclude.list

for node in slave1 slave2 slave3; do
  echo $node
  rsync -av -e ssh --exclude='venv' --exclude='__pycache__' --exclude='scutils.egg-info' ../scrapy-cluster --exclude='*.pyc' ${node}:~/
  ssh $node "cd ~/scrapy-cluster; bash start_all.sh; "
  # ssh $node "cd ~/scrapy-cluster; "
done