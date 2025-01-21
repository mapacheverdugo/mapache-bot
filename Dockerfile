FROM --platform=linux/amd64 python:3.9.21-slim as build

RUN apt-get -qq update 

WORKDIR /usr/src/bot

COPY requirements.txt /usr/src/bot/

RUN pip3 --quiet install --requirement requirements.txt \
    --force-reinstall --upgrade

COPY . /usr/src/bot

CMD ["python3", "main.py"]