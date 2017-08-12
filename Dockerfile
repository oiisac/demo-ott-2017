FROM python:alpine
MAINTAINER Oleg Nikitin <helgi@oiisac.com>

ENV PYTHONUNBUFFERED 1
ENV REDIS_HOST redis_db

ADD ./app /opt/app
RUN pip3 install redis
WORKDIR /opt/app
