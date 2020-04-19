#!/bin/sh
VERSION=${1:-0.1}
sudo docker build -f tfhub.Dockerfile --tag tfhub:$VERSION .
sudo docker run -it --rm --gpus all -v $HOME:/home/tfhub -p 8000:8000 tfhub:$VERSION
