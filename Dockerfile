# Stage 1: Base
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 as base

ARG KOHYA_VERSION=v21.7.16

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Africa/Johannesburg \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    SHELL=/bin/bash

# Install Ubuntu packages
RUN apt update && \
    apt -y upgrade && \
    apt install -y --no-install-recommends \
        software-properties-common \
        python3.10-venv \
        python3-tk \
        bash \
        git \
        ncdu \
        net-tools \
        openssh-server \
        libglib2.0-0 \
        libsm6 \
        libgl1 \
        libxrender1 \
        libxext6 \
        ffmpeg \
        wget \
        curl \
        psmisc \
        rsync \
        vim \
        unzip \
        p7zip-full \
        htop \
        pkg-config \
        libcairo2-dev \
        libgoogle-perftools4 libtcmalloc-minimal4 \
        apt-transport-https ca-certificates && \
    update-ca-certificates && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

# Set Python and pip
RUN ln -s /usr/bin/python3.10 /usr/bin/python && \
    curl https://bootstrap.pypa.io/get-pip.py | python && \
    rm -f get-pip.py

# Stage 2: Install kohya_ss and python modules
FROM base as kohya_ss_setup

# Create workspace working directory
WORKDIR /

# Install Kohya_ss
RUN git clone https://github.com/bmaltais/kohya_ss.git
WORKDIR /kohya_ss
RUN git checkout ${KOHYA_VERSION} && \
    python3 -m venv --system-site-packages venv && \
    source venv/bin/activate && \
    pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install --no-cache-dir xformers==0.0.20 bitsandbytes==0.35.0 accelerate==0.19.0 tensorboard==2.12.1 tensorflow==2.12.0 && \
    pip3 install -r requirements.txt && \
    pip3 install . && \
    # Fix Tensorboard
    pip3 uninstall -y tensorboard tb-nightly && \
    pip3 install tensorboard tensorflow && \
    deactivate

# Install Jupyter
RUN source venv/bin/activate && \
    pip3 install jupyterlab \
        ipywidgets \
        jupyter-archive \
        jupyter_contrib_nbextensions \
        gdown && \
    jupyter contrib nbextension install --user && \
    jupyter nbextension enable --py widgetsnbextension && \
    deactivate

# Install runpodctl
RUN wget https://github.com/runpod/runpodctl/releases/download/v1.10.0/runpodctl-linux-amd -O runpodctl && \
    chmod a+x runpodctl && \
    mv runpodctl /usr/local/bin

# Set up the container startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh
COPY accelerate.yaml /accelerate.yaml
COPY fix_venv.sh /fix_venv.sh
RUN chmod +x /fix_venv.sh

# Fix the venv to make it work from /workspace
RUN /fix_venv.sh /kohya_ss/venv /workspace/kohya_ss/venv

# Start the container
SHELL ["/bin/bash", "--login", "-c"]
CMD [ "/start.sh" ]