FROM python:3.9.5

# Set the working directory to override any set by base image
# This will create the directory if it doesn't exist
WORKDIR /aideas

# We only need this during build time, so we use ARG instead of ENV
ARG DEBIAN_FRONTEND=noninteractive
# Check available versions here: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
ARG CHROME_VERSION='131.0.6778.139-1'

RUN apt-get update && apt -f install -y \
    git \
    wget \
    docker.io \
    && git --version && wget --version && docker --version \
    && wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt install ./google-chrome-stable_${CHROME_VERSION}_amd64.deb -y --fix-missing \
    && apt install xvfb -y \
    # removes the package deb file
    && apt-get clean \
    # removes package lists, loaded by apt update
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

#CMD [ "python", "main.py" ]
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
