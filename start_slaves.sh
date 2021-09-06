#　rsync -avP  --exclude-from=/usr/exclude.list

for node in slave1 slave2 slave3; do
  echo $node
  VBoxManage startvm $node --type headless
done