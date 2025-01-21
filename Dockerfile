FROM amazonlinux:latest as build

RUN yum update -y && \
    yum install -y git python3-pip

WORKDIR /usr/src/bot

COPY requirements.txt /usr/src/bot/
RUN pip install -r /usr/src/bot/requirements.txt

COPY . /usr/src/bot

CMD ["python3", "main.py"]