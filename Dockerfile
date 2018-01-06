FROM ubuntu:trusty
RUN apt-get update
# Install dependencies for PPA
RUN apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository ppa:ethereum/ethereum
RUN apt-get install -y tmux python-setuptools
# C compilers required for cmake `build-essential`
RUN apt-get install -y build-essential automake pkg-config libtool libffi-dev libgmp-dev python3-cffi
RUN apt-get install -y python-dev libssl-dev python3-pip
RUN apt-get install -y systemd libpam-systemd
RUN apt-get install -y git wget unzip vim curl openssl

# Download Python, extract, configure, compile, test, and install the build
# Reference - https://passingcuriosity.com/2015/installing-python-from-source/
ARG PYTHON_VERSION=3.6.4
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
# Ignore `make test`
RUN tar xf Python-${PYTHON_VERSION}.tgz && cd Python-${PYTHON_VERSION} && ./configure && make && make install
# Source the bash_profile in linux with `. ~/.bash_profile`
RUN echo 'PATH="$HOME/bin/python3:$PATH"; export PATH' >> ~/.bash_profile && . ~/.bash_profile
# Fixes https://trello.com/c/K6jmmjvo/29-conflicts-due-to-cached-pyc-files
RUN echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.bash_profile && . ~/.bash_profile

RUN which python3; which pip3
RUN python3 --version; pip3 --version
RUN git clone --depth=50 https://github.com/ethereum/sharding.git ethereum/sharding
RUN pip3 install setuptools==37

COPY ./requirements.txt .
COPY ./setup.py .
COPY ./dev_requirements.txt .

RUN USE_PYETHEREUM_DEVELOP=1 python3 setup.py develop
RUN pip3 install -r dev_requirements.txt;

WORKDIR /code
