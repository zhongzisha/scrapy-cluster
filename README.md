# Scrapy Cluster

[![Build Status](https://travis-ci.org/istresearch/scrapy-cluster.svg?branch=master)](https://travis-ci.org/istresearch/scrapy-cluster) [![Documentation](https://readthedocs.org/projects/scrapy-cluster/badge/?version=latest)](http://scrapy-cluster.readthedocs.io/en/latest/) [![Join the chat at https://gitter.im/istresearch/scrapy-cluster](https://badges.gitter.im/istresearch/scrapy-cluster.svg)](https://gitter.im/istresearch/scrapy-cluster?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Coverage Status](https://coveralls.io/repos/github/istresearch/scrapy-cluster/badge.svg?branch=master)](https://coveralls.io/github/istresearch/scrapy-cluster?branch=master) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/istresearch/scrapy-cluster/blob/master/LICENSE) [![Docker Pulls](https://img.shields.io/docker/pulls/istresearch/scrapy-cluster.svg)](https://hub.docker.com/r/istresearch/scrapy-cluster/)

This Scrapy project uses Redis and Kafka to create a distributed on demand scraping cluster.

The goal is to distribute seed URLs among many waiting spider instances, whose requests are coordinated via Redis. Any other crawls those trigger, as a result of frontier expansion or depth traversal, will also be distributed among all workers in the cluster.

The input to the system is a set of Kafka topics and the output is a set of Kafka topics. Raw HTML and assets are crawled interactively, spidered, and output to the log. For easy local development, you can also disable the Kafka portions and work with the spider entirely via Redis, although this is not recommended due to the serialization of the crawl requests.

## Dependencies

Please see the ``requirements.txt`` within each sub project for Pip package dependencies.

Other important components required to run the cluster

- Python 2.7: https://www.python.org/downloads/
- Redis: http://redis.io
- Zookeeper: https://zookeeper.apache.org
- Kafka: http://kafka.apache.org

## Core Concepts

This project tries to bring together a bunch of new concepts to Scrapy and large scale distributed crawling in general. Some bullet points include:

- The spiders are dynamic and on demand, meaning that they allow the arbitrary collection of any web page that is submitted to the scraping cluster
- Scale Scrapy instances across a single machine or multiple machines
- Coordinate and prioritize their scraping effort for desired sites
- Persist data across scraping jobs
- Execute multiple scraping jobs concurrently
- Allows for in depth access into the information about your scraping job, what is upcoming, and how the sites are ranked
- Allows you to arbitrarily add/remove/scale your scrapers from the pool without loss of data or downtime
- Utilizes Apache Kafka as a data bus for any application to interact with the scraping cluster (submit jobs, get info, stop jobs, view results)
- Allows for coordinated throttling of crawls from independent spiders on separate machines, but behind the same IP Address
- Enables completely different spiders to yield crawl requests to each other, giving flexibility to how the crawl job is tackled

## Scrapy Cluster test environment

To set up a pre-canned Scrapy Cluster test environment, make sure you have the latest **Virtualbox** + **Vagrant >= 1.7.4** installed.  Vagrant will automatically mount the base **scrapy-cluster** directory to the **/vagrant** directory, so any code changes you make will be visible inside the VM. Please note that at time of writing this will not work on a [Windows](http://docs.ansible.com/ansible/intro_installation.html#control-machine-requirements) machine.

### Steps to launch the test environment:
1.  `vagrant up` in base **scrapy-cluster** directory.
2.  `vagrant ssh` to ssh into the VM.
3.  `sudo supervisorctl status` to check that everything is running.
4.  `virtualenv sc` to create a virtual environment
5.  `source sc/bin/activate` to activate the virtual environment
6.  `cd /vagrant` to get to the **scrapy-cluster** directory.
7.  `pip install -r requirements.txt` to install Scrapy Cluster dependencies.
8.  `./run_offline_tests.sh` to run offline tests.
9.  `./run_online_tests.sh` to run online tests (relies on kafka, zookeeper, redis).

## Documentation

Please check out the official [Scrapy Cluster 1.2.1 documentation](http://scrapy-cluster.readthedocs.org/en/latest/) for more information on how everything works!

## Branches

The `master` branch of this repository contains the latest stable release code for `Scrapy Cluster 1.2.1`.

The `dev` branch contains bleeding edge code and is currently working towards [Scrapy Cluster 1.3](https://github.com/istresearch/scrapy-cluster/milestone/3). Please note that not everything may be documented, finished, tested, or finalized but we are happy to help guide those who are interested.

## Cluster 集群部署

3台节点：slave1, slave2, slave3

3台节点的独立zookeeper集群，3台节点的独立kafka集群，redis部署在master的docker容器内。
先在slave1, slave2, slave3上启动zookeeper集群；
在master, slave2, slave3上启动kafka集群； `./kafka-server-start.sh ../config/server.properties`
在master上开启hadoop集群；
在master上开启hbase集群；
jps查看每个节点的进程。
部署好这两个集群后，
在master上单机运行爬虫，是可以的。
```
python kafka-monitor.py run
python redis-monitor.py
python rest-monitor.py
scrapy runspider crawling/spiders/link_spider.py
python kafka-monitor.py dump -t demo.incoming -p
python kafka-monitor.py dump -t demo.crawled_firehose -p
python kafka-monitor.py dump -t demo.outbound_firehose -p
curl http://localhost:5343   # 查看restful服务状态
# 向集群提交一个爬取请求
curl http://localhost:5343/feed -H "Content-Type: application/json" -d '{"url": "http://msn.com", "appid":"testapp", "crawlid":"ABC1234", "maxdepth":2}'
```

在slave1, slave2, slave3上进行以下操作，可以看到每个机器都在进行爬取
```
apt install build-essential gcc g++ python3-virtualenv python3-dev
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e scutils-1.2.0
```

修改了kafka_monitor的maxdepth，然后搞了一个简单网站，所有链接到网页都能爬到。似乎可行了。

curl http://localhost:5343/feed -H "Content-Type: application/json" -d '{"url": "http://10.0.7.216:8082", "appid":"testapp", "crawlid":"ABC1234", "maxdepth":20}'

如果爬取中断了，重启master。然后依次
1. 先启动zk集群。进入slave1,slave2,slave3启动每一台机器的zk。
```
ssh slave1
cd /opt/apache-zookeeper-3.6.2-bin/bin
./zkServer.sh start
```

2. 启动kafka集群。进入master,slave2,slave3启动每一台机器的kafka。

```
cd /opt/kafka_2.13-2.6.0-bin/bin
./kafka-server-start.sh ../config/server.properties
```

3. 启动hadoop和hbase集群。进入master。

```
cd /opt/hadoop-2.10.1-bin/sbin
./start-dfs.sh
./start-yarn.sh

cd /opt/hbase-2.3.3/bin
./start-hbase.sh
```

3. 启动ELK。进入master, 启动es, logstask, kibana，然后进入master/slave1/slave2/slave3启动filebeat。

```
cd /media/ubuntu/Working/elasticsearch/elasticsearch-7.10.0/bin
./elasticsearch
```

```
cd /media/ubuntu/Working/elasticsearch/logstash-7.10.0
./bin/logstash -f config/logstash_scrapy_cluster.conf
```

```
cd /media/ubuntu/Working/elasticsearch/kibana-7.10.0-linux-x86_64/bin
./kibana
```

```
cd /media/ubuntu/Working/elasticsearch/filebeat-7.10.0-linux-x86_64
./filebeat
```

4. 进入master, 运行deploy_to_slaves.sh，在slave1/slave2/slave3上启动爬虫。
5. 进入master，运行start_all.sh，即可重新开始爬取进程。这时如果docker的resis-service中数据没有丢失，队列里还有需要爬的网址时，可以继续爬。


