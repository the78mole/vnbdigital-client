FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add wakemeops apt repo and install tools via wake
RUN curl -sSL https://raw.githubusercontent.com/upciti/wakemeops/main/assets/install_repository | bash

RUN apt-get update \
    && apt-get install -y uv pre-commit \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user 'code'
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID code \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash code

# Set working directory
WORKDIR /workspace

USER code

