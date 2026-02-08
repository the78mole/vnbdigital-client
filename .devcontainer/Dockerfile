FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN uv pip install --system -e ".[dev]"

# Set default command
CMD ["/bin/bash"]
