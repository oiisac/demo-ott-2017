FROM python:alpine
MAINTAINER Oleg Nikitin <helgi@oiisac.com>

ENV PYTHONUNBUFFERED 1
ENV REDIS_HOST redis_db

ADD . /opt/
WORKDIR /opt/
RUN pip3 install -e .
