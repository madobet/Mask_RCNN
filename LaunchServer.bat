:: TODO 根据 Windows 平台选择合适的 venv
rem [Warn] Windows containers required
sudo docker build -f tools\tfser.Dockerfile --tag tfser:windows .
sudo docker run --gpus all -it --rm -p 8500:8500 -p 8501:8501 tfser:windows --model_config_file=/models/model_config.tf