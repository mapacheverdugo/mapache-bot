FROM amazonlinux:latest

RUN yum update -y && \
    yum install -y git python3-pip

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .