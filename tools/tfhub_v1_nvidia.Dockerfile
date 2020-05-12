FROM tensorflow/tensorflow:1.15.2-gpu-py3-jupyter

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python-pip python-setuptools python-wheel apt-transport-https
RUN pip install --upgrade pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install apt-smart
RUN apt-smart --auto-change-mirror --update
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo vim neovim htop git build-essential npm

RUN npm config set loglevel http -g
RUN npm config set registry https://r.npm.taobao.org -g
RUN npm install -g configurable-http-proxy

RUN pip uninstall -y enum34
COPY tfhub_v1_requirements.txt /tmp/requirements.txt
RUN pip install --timeout 600 -r /tmp/requirements.txt
RUN pip install pycocotools

RUN apt-get install -y libsm6 libxext6 libxrender-dev fontconfig fonts-powerline
RUN fc-cache -f

RUN useradd -ms /bin/bash -G sudo tfhub
RUN echo 'tfhub:hub?112358!' | chpasswd

WORKDIR /tmp
RUN echo "c.Spawner.default_url = '/lab'" > jupyterhub_config.py
# ENTRYPOINT [ "jupyterhub", "--no-db", "--url=http://:8000/jupyter", "--y=True" ]
CMD [ "jupyterhub", "--no-db", "--url=http://:8000/jupyter", "--y=True" ]
