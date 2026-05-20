# vnbdigital-client

[![PyPI](https://img.shields.io/pypi/v/vnbdigital-client)](https://pypi.org/project/vnbdigital-client/) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/vnbdigital-client/) [![Publish](https://github.com/the78mole/vnbdigital-client/actions/workflows/publish.yml/badge.svg)](https://github.com/the78mole/vnbdigital-client/actions/workflows/publish.yml)
[![GitHub issues](https://img.shields.io/github/issues/the78mole/vnbdigital-client)](https://github.com/the78mole/vnbdigital-client/issues) [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python client library and CLI tool for accessing vnbdigital.de grid operator (Verteilnetzbetreiber) data. This package abstracts the GraphQL API and provides a simple, intuitive interface for looking up operators by their BDEW code.

## Features

- Simple Python API for vnbdigital.de grid operator data
- Command-line interface (CLI) for quick lookups
- Unified search API matching the vnbdigital.de website (search for postcodes, operators, regions)
- Direct postcode-based and coordinate-based network operator search
- Typed dataclasses (`Operator`, `Region`, `Postcode`, `SearchResult`) for structured results
- Batch lookups for multiple operators
- BDEW company and market function lookup via [bdew-codes.de](https://bdew-codes.de) (address, contact details)
- Built with modern Python tooling (uv, pyproject.toml)
- Dev container support for easy development
- Comprehensive test coverage

## Installation

### From PyPI (when published)

```bash
pip install vnbdigital-client
```

Oder mit `uv`:

```bash
uv add vnbdigital-client
```

### From source with uv

```bash
# Clone the repository
git clone https://github.com/the78mole/vnbdigital-client.git
cd vnbdigital-client

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly (uv creates the venv and installs dependencies automatically)
uv run vnbdigital --help
```

## Usage

### Python API

```python
from vnbdigital_client import VNBDigitalClient

client = VNBDigitalClient()

# Look up a grid operator by BDEW code / ID
operator = client.get_operator("179")
if operator:
    print(f"{operator.name} - {operator.postcode} {operator.city}")
    print(f"Website: {operator.website}")
    for region in operator.regions:
        print(f"  Region: {region.name}")

# Get detailed information (types, description, services, documents, ...)
details = client.get_operator_details("179")
if details:
    print(f"Typ: {', '.join(details.types)}")
    print(f"Beschreibung: {details.description}")
    print(f"Aufrufe: {details.clicks}")

# Batch lookup for multiple operators
results = client.get_operators(["179", "180", "181"])
for oid, op in results.items():
    if op:
        print(f"[{oid}] {op.name}")
    else:
        print(f"[{oid}] not found")

# Unified search (same API as vnbdigital.de website)
# Search for postal codes, operators, regions, locations, etc.
search_results = client.search("91058")
for result in search_results:
    print(f"{result.type}: {result.title} - {result.subtitle}")

# Get network operators for a POSTCODE result
postcode_hit = next(r for r in search_results if r.type == "POSTCODE")
detail = client.search_by_postcode(postcode_hit.id)
for vnb in detail.get("vnbs", []):
    print(f"  - {vnb['name']}")

# Get network operators for a LOCATION result (coordinates lookup)
location_hit = next(r for r in search_results if r.type == "LOCATION")
# Extract coordinates from URL: /overview?coordinates=lat,lon&searchType=LOCATION
coords = location_hit.url.split("coordinates=")[1].split("&")[0]
detail = client.search_by_coordinates(coords)
for vnb in detail.get("vnbs", []):
    print(f"  - {vnb['name']}")

# BDEW lookup by company code (6–7 digits) — returns all market functions
from vnbdigital_client import lookup_bdew_by_company_code, lookup_bdew_by_market_code, lookup_bdew_market_function_detail

result = lookup_bdew_by_company_code(660188)
if result:
    print(f"{result['name']} ({result['code']})")
    for mf in result["market_functions"]:
        print(f"  {mf['bdew_code']}  {mf['function']}  – {mf['contact']}")
        # Optionally fetch full address and contact details:
        detail = lookup_bdew_market_function_detail(mf["id"])
        print(f"    {detail['zip']} {detail['city']}, Tel: {detail['phone']}")

# BDEW lookup by 13-digit market function code — returns only the matching entry
result = lookup_bdew_by_market_code("9903445000000")
if result:
    print(result)
```

### Command-Line Interface

The package includes a CLI tool for easy command-line access:

```bash
# Basic operator lookup
vnbdigital operator 179

# Detailed information
vnbdigital details 179

# JSON output
vnbdigital operator 179 --format json

# Batch lookup
vnbdigital batch 179 180 181

# Unified search (same as vnbdigital.de website)
# Search for postal codes, operators, regions, etc.
vnbdigital search 90158
vnbdigital search "Stadtwerke"

# Search with details for postcode and location results
vnbdigital search 90158 --details

# Search with JSON output
vnbdigital search 90158 --format json

# Look up network operators by geographic coordinates (lat,lon)
vnbdigital coordinates "49.5510,11.1101"

# Coordinates with JSON output
vnbdigital coordinates "49.5510,11.1101" --format json

# Coordinates with custom voltage filter
vnbdigital coordinates "49.5510,11.1101" --voltage Niederspannung

# BDEW company lookup by 6–7-digit company code
vnbdigital bdew 660188

# BDEW lookup by 13-digit market function code
vnbdigital bdew 9903445000000

# With full address and contact details per market function
vnbdigital bdew 660188 --details
vnbdigital bdew 9903445000000 --details

# BDEW output as JSON (combinable with --details)
vnbdigital bdew 660188 --json
vnbdigital bdew 660188 --details --json

# Override bdew-codes.de base URL via environment variable
export BDEW_LOOKUP_URL="https://bdew-codes.de"
vnbdigital bdew 660188

# Override API URL via environment variable
export VNBDIGITAL_API_URL="https://www.vnbdigital.de/gateway/graphql"
vnbdigital operator 179
```

## Development

### Using Dev Container

This project includes a dev container configuration for easy development:

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted
4. The workspace is mounted into the container automatically
5. When you run the first `uv` command, it will create a `.venv` and install dependencies

### Manual Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run tests (uv automatically creates a .venv and installs all dependencies)
uv run --extra dev pytest

# Run linting
uv run --extra dev ruff check src/

# Format code
uv run --extra dev black src/

# Type checking
uv run --extra dev mypy src/vnbdigital_client/
```

### Running Tests

```bash
# Run all tests
uv run --extra dev pytest

# Run with coverage
uv run --extra dev pytest --cov=vnbdigital_client --cov-report=html

# Run specific test file
uv run --extra dev pytest tests/test_client.py
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

- `VNBDIGITAL_API_URL`: GraphQL endpoint URL (default: https://www.vnbdigital.de/gateway/graphql)
- `BDEW_LOOKUP_URL`: Base URL for bdew-codes.de lookups (default: https://bdew-codes.de)

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
- CLI built with [Click](https://click.palletsprojects.com/)
- Data provided by [vnbdigital.de](https://www.vnbdigital.de)
