# Contributing to vnbdigital-client

Thank you for your interest in contributing to vnbdigital-client! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/the78mole/vnbdigital-client.git
   cd vnbdigital-client
   ```

2. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

### Using Dev Container (Optional)

If you use VS Code, you can use the provided dev container:

1. Install the "Dev Containers" extension
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted
4. The workspace is mounted into the container automatically
5. When you run the first `uv` command, it will create a `.venv` and install dependencies

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vnbdigital_client --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

### Code Formatting

We use [Black](https://github.com/psf/black) for code formatting:

```bash
# Format code
black src/ tests/ examples/

# Check formatting without making changes
black --check src/
```

### Linting

We use [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
# Run linter
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

### Type Checking

We use [mypy](https://mypy-lang.org/) for type checking:

```bash
mypy src/vnbdigital_client/
```

### Building the Package

```bash
# Install build tool
uv pip install build

# Build the package
python -m build
```

## Making Changes

### Branch Naming

- Feature branches: `feature/description-of-feature`
- Bug fix branches: `fix/description-of-bug`
- Documentation: `docs/description-of-change`

### Commit Messages

Follow these guidelines for commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Example:
```
Add support for advanced search filters

- Add filter parameters to search method
- Update CLI to accept filter options
- Add tests for new functionality

Fixes #123
```

### Pull Request Process

1. **Create a new branch** from `main`
2. **Make your changes** following the coding standards
3. **Add or update tests** for your changes
4. **Update documentation** if needed
5. **Ensure all tests pass** and code is formatted
6. **Submit a pull request** with a clear description

### Pull Request Checklist

Before submitting your PR, make sure:

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] Linting passes (`ruff check src/`)
- [ ] Type checking passes (`mypy src/vnbdigital_client/`)
- [ ] Documentation is updated (if applicable)
- [ ] CHANGELOG is updated (if applicable)
- [ ] Commit messages follow guidelines

## Code Style

### Python Code

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings for public functions and classes

### Example:

```python
from typing import List, Dict, Any

def search_items(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for items matching the query.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of matching items
        
    Raises:
        ValueError: If query is empty
    """
    if not query:
        raise ValueError("Query cannot be empty")
    
    # Implementation here
    return []
```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Test files should start with `test_`
- Test functions should start with `test_`
- Use descriptive test names that explain what is being tested
- Mock external API calls
- Aim for high code coverage

### Example Test:

```python
from unittest.mock import Mock, patch
from vnbdigital_client import VNBDigitalClient

@patch('vnbdigital_client.client.Client')
def test_search_returns_results(mock_client_class):
    """Test that search returns expected results."""
    mock_client = Mock()
    mock_client.execute.return_value = {
        "search": [{"id": "1", "title": "Test"}]
    }
    mock_client_class.return_value = mock_client
    
    client = VNBDigitalClient()
    results = client.search("test")
    
    assert len(results) == 1
    assert results[0]["id"] == "1"
```

## Documentation

### Updating README

When adding new features:
- Update the usage examples
- Add new CLI commands to the command reference
- Update the feature list if applicable

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings for complex functions

## Getting Help

If you have questions or need help:

1. Check existing issues and discussions
2. Read the README and documentation
3. Open a new issue with the "question" label

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## License

By contributing to vnbdigital-client, you agree that your contributions will be licensed under the MIT License.
