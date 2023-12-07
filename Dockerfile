# Python images
FROM python:3.8-slim as python38
FROM python:3.9-slim as python39
FROM python:3.10-slim as python310
FROM python:3.11-slim as python311
FROM python:3.12-slim as python312

# Base image
FROM debian:bookworm-slim

# Copy Python from images to base image
COPY --from=python38 /usr/local /usr/local
COPY --from=python39 /usr/local /usr/local
COPY --from=python310 /usr/local /usr/local
COPY --from=python311 /usr/local /usr/local
COPY --from=python312 /usr/local /usr/local

# Install core libs
RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        apt-utils \
        netcat-traditional \
        binutils \
        libproj-dev \
        libpq-dev \
        gdal-bin \
        ca-certificates \
        gcc \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Setup environment
WORKDIR /home/app/libs
COPY pyproject.toml poetry.lock* ./
RUN pip3.8 install -U pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy source code
COPY . /home/app/libs
