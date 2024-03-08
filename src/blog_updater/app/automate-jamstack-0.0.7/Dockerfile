#FROM pandoc/core:latest-alpine
FROM node:18-alpine3.18

LABEL maintainer="https://github.com/poshjosh <posh.bc@gmail.com>"

ARG APP_PORT=8000
ENV APP_PORT=${APP_PORT}

EXPOSE ${APP_PORT}

ARG TERRAFORM_VERSION="1.6.6"

RUN apk update && apk upgrade \
    && apk add util-linux \
    && apk add bash git openssh npm \
    && bash --version && git --version && ssh -V && npm -v && node -v \
    && apk add \
     	  ca-certificates \
    	  groff \
    	  less \
        curl \
    	  python3 \
    	  py-pip \
        unzip \
        pandoc \
    && rm -rf /var/cache/apk/* \
    && pip install awscli \
    && aws --version \
    && curl -LO https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip '*.zip' -d /usr/local/bin \
    && rm *.zip

VOLUME /app

# Set the working directory to override any set by base image
# This will create the directory if it doesn't exist
WORKDIR /

COPY ./app/ ./app/

RUN (cd ./app/sites && npm install -g gatsby-cli)

RUN chmod +x ./app/config/setup-scripts/docker-entrypoint.sh

ENTRYPOINT ["./app/config/setup-scripts/docker-entrypoint.sh"]
