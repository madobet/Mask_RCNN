#!/bin/sh
VERSION=${1:-0.1}
sudo docker build -f tfhub_v1.Dockerfile --tag tfhub_v1:$VERSION .
sudo docker run -it --rm --gpus all -v $HOME:/home/tfhub -p 8000:8000 tfhub_v1:$VERSION
