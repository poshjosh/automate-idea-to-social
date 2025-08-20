FROM python:3.9-slim-bookworm AS builder

# We only need this during build time, so we use ARG instead of ENV
ARG DEBIAN_FRONTEND=noninteractive

# Check available versions here: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
ARG CHROME_VERSION='131.0.6778.139-1'

RUN apt-get update && apt -f install -y docker.io git wget \
    && docker --version && git --version && wget --version \
    && wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb" \
    && apt remove wget -y \
    && apt install "./google-chrome-stable_${CHROME_VERSION}_amd64.deb" -y --fix-missing \
    && rm -f "./google-chrome-stable_${CHROME_VERSION}_amd64.deb" \
    && apt install xvfb -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to override any set by base image
# This will create the directory if it doesn't exist
# The app expect to work from within the aideas directory.
WORKDIR /aideas

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN python3 -m pip install --no-cache-dir -r "requirements.txt" \
    && rm -rf ~/.cache/pip

FROM python:3.12-slim-bookworm

WORKDIR /

COPY --from=builder . .

#RUN echo $(whoami) && echo $(pwd) && ls -aol && cd aideas && echo $(pwd) && ls -aol && cd ..

ENTRYPOINT ["sh", "-c", "./aideas/docker-entrypoint.sh"]
