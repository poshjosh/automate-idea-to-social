# we use bullseye to fix this https://github.com/docker-library/python/issues/837
#FROM python:3.9.23-bullseye
FROM python:3.9-slim-bookworm AS builder

# Set the working directory to override any set by base image
# This will create the directory if it doesn't exist
WORKDIR /aideas

COPY . .

# We only need this during build time, so we use ARG instead of ENV
ARG DEBIAN_FRONTEND=noninteractive

# We need git to install our reqirements.txt, one package is from a git repo
RUN apt-get update && apt -f install -y git  \
    && git --version \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

# Check available versions here: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
ARG CHROME_VERSION='131.0.6778.139-1'

RUN apt-get update && apt -f install -y docker.io git wget \
    && docker --version && git --version && wget --version \
    && wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt remove wget -y \
    && apt install ./google-chrome-stable_${CHROME_VERSION}_amd64.deb -y --fix-missing \
    && apt install xvfb -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim-bookworm

COPY --from=builder . .

RUN chmod +x aideas/docker-entrypoint.sh
ENTRYPOINT ["./aideas/docker-entrypoint.sh"]
