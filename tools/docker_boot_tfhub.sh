#!/bin/sh
! command -v neofetch 2>&1 >/dev/null && printf "You must have neofetch installed.\n" && exit 1
VERSION=${1:-0.1}
GPU_BRAND=$(neofetch --gpu_type dedicated --option 'gpu')
printf "$GPU_BRAND -> detected\n"

if [ "${GPU_BRAND#*[Nn][Vv][Ii][Dd][Ii][Aa]}" != "$GPU_BRAND" ]; then
    printf "[Warn] nvidia-container-toolkit(AUR) required to enable Nvidia support\n"
    sudo docker build -f tfhub_nvidia.Dockerfile --tag tfhub:nvidia-$VERSION .
    sudo docker run -it --rm --gpus all -v $HOME:/home/tfhub -p 8000:8000 tfhub:nvidia-$VERSION
elif [ "${GPU_BRAND#*[Aa][Mm][Dd]}" != "$GPU_BRAND" ]; then
    # ref: https://github.com/RadeonOpenCompute/ROCm-docker/blob/master/quick-start.md
    # ref: https://github.com/rocm-arch/rocm-arch/issues/55
    printf "[Warn] rock-dkms(AUR) MAY required and current user in \'video\' group to enable AMD GPU support\n"
    sudo docker build -f tfhub_amd.Dockerfile --tag tfhub:amd-$VERSION .
    sudo docker run -it --rm --gpus all -v $HOME:/home/tfhub -p 8000:8000 tfhub:amd-$VERSION
fi
