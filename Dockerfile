FROM python:3.10-bullseye

# Install ALL build deps for tgcalls + ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libopus-dev \
    libvpx-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

CMD ["python", "main.py"]