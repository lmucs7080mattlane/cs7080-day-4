FROM python:3.6-slim

RUN pip3 install Flask pymongo

RUN mkdir /opt/code
WORKDIR /opt/code
ADD . /opt/code

ENV HOST_IP=0.0.0.0
ENV HOST_PORT=9999
ENV FLASK_APP=device_api.py

CMD flask run --host=$HOST_IP --port=$HOST_PORT
