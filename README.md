# vnbdigital-client

A Python client library and CLI tool for accessing the vnbdigital.de database. This package abstracts all complex GraphQL operations and provides a simple, intuitive API for querying vnbdigital data.

## Features

- 🚀 Simple Python API for vnbdigital.de
- 💻 Command-line interface (CLI) for quick queries
- 🔒 Support for API authentication
- 📦 Built with modern Python tooling (uv, pyproject.toml)
- 🐳 Dev container support for easy development
- ✅ Comprehensive test coverage

## Installation

### From PyPI (when published)

```bash
pip install vnbdigital-client
```

### From source with uv

```bash
# Clone the repository
git clone https://github.com/the78mole/vnbdigital-client.git
cd vnbdigital-client

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install -e .
```

## Usage

### Python API

```python
from vnbdigital_client import VNBDigitalClient

# Initialize the client
client = VNBDigitalClient()

# Search for items
results = client.search("historical documents", limit=10)
for item in results:
    print(f"{item['title']}: {item['url']}")

# Get a specific item
item = client.get_item("item-id-123")
print(f"Title: {item['title']}")
print(f"Description: {item['description']}")

# List all collections
collections = client.list_collections()
for collection in collections:
    print(f"{collection['name']}: {collection['itemCount']} items")

# Get items from a collection
collection = client.get_collection("collection-id", limit=50)
print(f"Collection: {collection['name']}")
for item in collection['items']:
    print(f"  - {item['title']}")
```

### With API Authentication

```python
client = VNBDigitalClient(
    api_url="https://vnbdigital.de/api/graphql",
    api_key="your-api-key"
)
```

### Command-Line Interface

The package includes a CLI tool for easy command-line access:

```bash
# Search for items
vnbdigital search "historical documents"

# Get a specific item
vnbdigital get item-id-123

# List all collections
vnbdigital collections

# Get items from a collection
vnbdigital collection collection-id --limit 20

# Use JSON output format
vnbdigital search "documents" --format json

# Set API credentials via environment variables
export VNBDIGITAL_API_URL="https://vnbdigital.de/api/graphql"
export VNBDIGITAL_API_KEY="your-api-key"
vnbdigital search "documents"
```

## Development

### Using Dev Container

This project includes a dev container configuration for easy development:

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted
4. The container will be built with all dependencies

### Manual Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/

# Format code
black src/

# Type checking
mypy src/vnbdigital_client/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vnbdigital_client --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

## Project Structure

```
vnbdigital-client/
├── .devcontainer/          # Dev container configuration
│   ├── Dockerfile
│   └── devcontainer.json
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── ci.yml         # Continuous integration
│       └── publish.yml    # PyPI publishing
├── src/
│   └── vnbdigital_client/  # Main package
│       ├── __init__.py
│       ├── client.py       # API client
│       └── cli.py          # CLI tool
├── tests/                  # Test suite
│   ├── test_client.py
│   └── test_cli.py
├── pyproject.toml          # Project configuration
├── renovate.json           # Renovate config
└── README.md
```

## Configuration

### Environment Variables

- `VNBDIGITAL_API_URL`: API endpoint URL (default: https://vnbdigital.de/api/graphql)
- `VNBDIGITAL_API_KEY`: API authentication key (optional)

### Renovate

This project uses Renovate for automated dependency updates. Configuration is in `renovate.json`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Daniel Glaser

## Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) - A fast Python package installer
- GraphQL client powered by [gql](https://github.com/graphql-python/gql)
- CLI built with [Click](https://click.palletsprojects.com/)
