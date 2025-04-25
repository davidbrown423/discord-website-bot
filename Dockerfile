# Use an official Python runtime as the base image
FROM python:3.11-slim

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxss1 \
    libgtk-3-0 \
    libx11-xcb1 \
    # Additional dependencies for Playwright
    libgstreamer1.0-0 \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libatomic1 \
    libxslt1.1 \
    libwoff2-1.0.2 \
    libvpx7 \
    libevent-2.1-7 \
    libopus0 \
    libgstreamer-plugins-base1.0-0 \
    gstreamer1.0-plugins-good \
    libgstreamer-plugins-bad1.0-0 \
    libflite1 \
    libwebpdemux2 \
    libavif15 \
    libharfbuzz-icu0 \
    libwebpmux3 \
    libenchant-2-2 \
    libsecret-1-0 \
    libhyphen0 \
    libmanette-0.2-0 \
    libpsl5 \
    libnghttp2-14 \
    libgles2 \
    libx264-164 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Copy the rest of the application
COPY . .

# Command to run the bot
CMD ["python", "main.py"]
