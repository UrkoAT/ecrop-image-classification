FROM python:3.9.12-slim-buster
COPY app/ /app
RUN pip install pika pillow numpy tensorflow tensorflow-serving-api
WORKDIR /app
CMD "python3 -u messageHandler.py"