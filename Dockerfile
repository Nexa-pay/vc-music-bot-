FROM python:3.10-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

# ✅ Pre-download yt-dlp EJS remote components at build time
RUN yt-dlp --allow-unplayable-formats --remote-components ejs:github || true

COPY . .

CMD ["python", "main.py"]
