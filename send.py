import json
import uuid
import numpy as np

import pika


URL = 'amqp://node-publisher:F]k[N$u6SMY2Rum-@localhost:5672'

conn = pika.BlockingConnection(pika.URLParameters(URL))
channel = conn.channel()


channel.basic_publish(
    exchange='images',
    routing_key='images.process',
    body=str(np.random.random(1000))
)

print('[+] Image sent!!!!!')

conn.close()