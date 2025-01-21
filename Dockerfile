FROM amazonlinux:latest

RUN yum update -y && \
    yum install -y git python3-pip

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app

CMD ["python3", "main.py"]