sudo mkdir -p /media/ubuntu/Working/mysql_root/conf
sudo mkdir -p /media/ubuntu/Working/mysql_root/logs
sudo mkdir -p /media/ubuntu/Working/mysql_root/data
sudo mkdir -p /media/ubuntu/Working/mysql_root/mysql-files
sudo docker run -p 3306:3306 --name mysql \
-v /media/ubuntu/Working/mysql_root/conf:/etc/mysql \
-v /media/ubuntu/Working/mysql_root/logs:/var/log/mysql \
-v /media/ubuntu/Working/mysql_root/data:/var/lib/mysql \
-v /media/ubuntu/Working/mysql_root/mysql-files:/var/lib/mysql-files \
-e MYSQL_ROOT_PASSWORD=zzs123456 \
-d mysql:latest

