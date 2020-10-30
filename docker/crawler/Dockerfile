FROM python:3.8
MAINTAINER Madison Bahmer <madison.bahmer@istresearch.com>

# os setup
COPY sources.list /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8
RUN apt-get update && apt-get -y install \
  python3-lxml \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev \
  libxml2-dev \
  libxslt1-dev \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install requirements
COPY crawler/requirements.txt /usr/src/app/
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
COPY scutils-1.2.0 /usr/src/app/scutils
RUN pip3 install -e /usr/src/app/scutils

# move codebase over
COPY crawler /usr/src/app

COPY utils /usr/src/app/utils
WORKDIR /usr/src/app/utils
RUN python setup.py install
WORKDIR /usr/src/app

# override settings via localsettings.py
COPY docker/crawler/settings.py /usr/src/app/crawling/localsettings.py

# copy testing script into container
COPY docker/run_docker_tests.sh /usr/src/app/run_docker_tests.sh

# set up environment variables

# run the spider
CMD ["scrapy", "runspider", "crawling/spiders/link_spider.py"]