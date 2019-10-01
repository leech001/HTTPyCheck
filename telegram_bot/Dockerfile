FROM python:3
MAINTAINER Bulanov Konstantin <leech001@gmail.com>

ADD builder /opt/builder
WORKDIR /opt/builder
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /opt/application
CMD [ "python3", "./main.py" ]
