FROM python:3.12-slim

# Install system dependencies and CLI tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    ca-certificates \
    gh \
    && rm -rf /var/lib/apt/lists/*

# Install uv via pip to avoid external apt repos
RUN python -m pip install --no-cache-dir uv

# Set working directory
WORKDIR /workspace

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/
COPY tests/ tests/

# Install Python dependencies
RUN uv pip install --system -e ".[dev]"

# Set default command
CMD ["/bin/bash"]
