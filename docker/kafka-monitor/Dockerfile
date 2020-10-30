FROM python:3.8
MAINTAINER Madison Bahmer scrapy-cluster-tech@istresearch.com

# os setup
COPY sources.list /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8
RUN apt-get update
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install requirements
COPY kafka-monitor/requirements.txt /usr/src/app/
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
COPY scutils-1.2.0 /usr/src/app/scutils
RUN pip3 install -e /usr/src/app/scutils

# move codebase over
COPY kafka-monitor /usr/src/app

# override settings via localsettings.py
COPY docker/kafka-monitor/settings.py /usr/src/app/localsettings.py

# copy testing script into container
COPY docker/run_docker_tests.sh /usr/src/app/run_docker_tests.sh

# set up environment variables

# run command
CMD ["python", "kafka_monitor.py", "run"]