!/bin/bash
TESTDATA="$(pwd)/serving/tensorflow_serving/servables/tensorflow/testdata"
docker run -t --rm -p 8501:8501 \
    -v "$TESTDATA/saved_model_half_plus_two_cpu:/models/half_plus_two" \
    -e MODEL_NAME=half_plus_two \
    tensorflow/serving &
