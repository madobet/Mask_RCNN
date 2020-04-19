#!/bin/sh
VERSION=${1:-0.1}
sudo docker build -f tfser.Dockerfile --tag tfser:${VERSION} .
sudo docker run --gpus all -it --rm -p 8500:8500 -p 8501:8501 tfser:${VERSION} --model_config_file=/models/model_config.tf
