FROM python:3.9.5

RUN apt-get update && apt -f install -y && apt-get install -y \
    git \
    wget \
    && git --version && wget --version \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install ./google-chrome-stable_current_amd64.deb -y --fix-missing \
    # removes the package deb file
    && apt-get clean \
    # removes package lists, loaded by apt update
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to override any set by base image
# This will create the directory if it doesn't exist
WORKDIR /

COPY ./ ./

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]
