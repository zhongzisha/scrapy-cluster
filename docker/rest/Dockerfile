FROM python:3.8
MAINTAINER Madison Bahmer <madison.bahmer@istresearch.com>

# os setup
COPY sources.list /etc/apt/sources.list
RUN apt-get update
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install requirements
COPY rest/requirements.txt /usr/src/app/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# move codebase over
COPY rest /usr/src/app

# override settings via localsettings.py
COPY docker/rest/settings.py /usr/src/app/localsettings.py

# copy testing script into container
COPY docker/run_docker_tests.sh /usr/src/app/run_docker_tests.sh

# set up environment variables

# run command
CMD ["python", "rest_service.py"]