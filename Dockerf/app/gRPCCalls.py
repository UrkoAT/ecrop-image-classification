from enum import Enum
from os import getenv
from typing import Union

from numpy import expand_dims, argmax, array, squeeze, zeros, uint8, ndarray
from grpc import insecure_channel
from tensorflow import make_tensor_proto
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


class MaskColorMap(Enum):
    Urban = (0, 255, 255)  # Cyan
    Agriculture = (255, 255, 0)  # Amarillo
    Rangeland = (255, 0, 255)  # Morado
    Forest = (0, 255, 0)  # Verde
    Water = (0, 0, 255)  # Azul
    Barren = (255, 255, 255)  # Blanco
    Uknown = (0, 0, 0)  # Negro


def __rgb_encode_mask(mask):
    rgb_encode_image = zeros((mask.shape[0], mask.shape[1], 3))

    for j, cls in enumerate(MaskColorMap):
        rgb_encode_image[(mask == j)] = array(cls.value) / 255.
    return rgb_encode_image


OPTIONS = [('grpc.max_receive_message_length', 100*1024*1024)]


MODEL = getenv('MODEL_NAME', 'ecrop-main-serving')
VERSION = int(getenv('MODEL_VERSION', 1))

INPUT_LAYER = getenv('MODEL_INPUT_LAYER', 'input_1')
OUTPUT_LAYER = getenv('MODEL_OUTPUT_LAYER', 'conv2d_18')

GRPC_SERVER = getenv('GRPC_SERVER', 'localhost')
GRPC_PORT = getenv('GRPC_PORT', '8500')

channel = insecure_channel(f'{GRPC_SERVER}:{GRPC_PORT}', options=OPTIONS)

stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


def process_image(image: Union[list, ndarray]) -> ndarray:
    request = predict_pb2.PredictRequest()
    request.model_spec.name = MODEL
    request.model_spec.version.value = VERSION

    sendable = expand_dims(image, 0)

    request.inputs[INPUT_LAYER].CopyFrom(make_tensor_proto(
        sendable, shape=sendable.shape, dtype=float))

    pred = stub.Predict(request, 10)
    arr = pred.outputs[OUTPUT_LAYER].float_val
    arr = array(arr).reshape((480, 480, 7))
    arr = argmax(arr, axis=-1)
    arr = __rgb_encode_mask(arr)
    arr = arr*255
    return array(arr, dtype=uint8)
