FROM python:3.10-bullseye

WORKDIR /app

# Only ffmpeg is truly needed at runtime
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
