FROM python:3.11.0b1-slim-buster
COPY app/ /app
RUN pip install pika pillow numpy tensorflow tensorflow-serving-api
WORKDIR /app
CMD ["python3", "-u", "messageHandler.py"]