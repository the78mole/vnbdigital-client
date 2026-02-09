# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-08

### Added
- Initial release of vnbdigital-client
- Python client library for accessing vnbdigital.de database
- GraphQL abstraction layer with simple API methods:
  - `search()` - Search for items
  - `get_item()` - Get specific item by ID
  - `list_collections()` - List all collections
  - `get_collection()` - Get items from a collection
- Command-line interface (CLI) with Click:
  - `vnbdigital search` - Search for items
  - `vnbdigital get` - Get specific item
  - `vnbdigital collections` - List collections
  - `vnbdigital collection` - Get collection items
  - Support for JSON and table output formats
- Project setup with uv package manager
- pyproject.toml configuration
- Renovate configuration for automated dependency updates
- GitHub Actions workflows:
  - CI workflow for testing and linting
  - PyPI publish workflow for releases
- Dev container support with:
  - Dockerfile with Python 3.12 and uv
  - VS Code devcontainer.json configuration
- Comprehensive test suite with pytest (67% coverage)
- Documentation:
  - Detailed README with usage examples
  - Contributing guidelines
  - Example scripts
- Code quality tools:
  - Black for code formatting
  - Ruff for linting
  - mypy for type checking

### Security
- Added explicit permissions to GitHub Actions workflows
- Passed CodeQL security scanning with no alerts

[0.1.0]: https://github.com/the78mole/vnbdigital-client/releases/tag/v0.1.0
