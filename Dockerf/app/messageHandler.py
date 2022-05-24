from os import remove, makedirs, getenv
from os.path import exists, join
import traceback
import pika
import uuid
import base64

from numpy import array
from gRPCCalls import process_image
from PIL import Image

RABBIT_SERVER = getenv('RABBIT_SERVER', 'rabbitmq')
RABBIT_PORT = getenv('RABBIT_PORT', '5672')


URL = f'amqp://node-publisher:F]k[N$u6SMY2Rum-@{RABBIT_SERVER}:{RABBIT_PORT}'

conn = pika.BlockingConnection(pika.URLParameters(URL))
channel = conn.channel()

queue = channel.queue_bind('images.process', 'images')

TMP_FOLDER = 'tmp/'

if not exists(TMP_FOLDER):
    makedirs(TMP_FOLDER)


def on_request(ch, method, props, body):

    imname = uuid.uuid4()

    path = join(TMP_FOLDER, f'{imname}.png')

    with open(path, 'wb') as f:
        f.write(body)
        f.seek(0)

    img = Image.open(path, formats=['png']).convert('RGB')

    cropped = array(img.crop((0, 20, 480, 500)))

    processed = process_image(cropped)

    im_file = Image.fromarray(processed).crop((128, 128, 384, 384))
    im_file.save(path)

    with open(path, 'rb') as f:
        response = base64.b64encode(f.read())

    ch.basic_publish(
        exchange='images',
        routing_key='images.processed',
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id),
        body=response.decode('utf-8')
    )

    remove(path)

    print('[+] Processed image.')

    ch.basic_ack(delivery_tag=method.delivery_tag)


print('[*] Server started. Listening...')

channel.basic_consume(on_message_callback=on_request, queue='images.process')

try:
    channel.start_consuming()
except Exception as e:
    print('[ERR] Error: {}'.format(e))
    traceback.print_exc()
    channel.close()
    conn.close()
