FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install uv and gh via wakemeops
RUN curl -fsSL https://raw.githubusercontent.com/upciti/wakemeops/main/assets/wakemeops.gpg \
        | gpg --dearmor -o /usr/share/keyrings/wakemeops-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/wakemeops-archive-keyring.gpg] https://deb.wakemeops.com/ stable main" \
        > /etc/apt/sources.list.d/wakemeops.list \
    && apt-get update \
    && apt-get install -y \
        uv \
        gh \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN uv pip install --system -e ".[dev]"

# Set default command
CMD ["/bin/bash"]
