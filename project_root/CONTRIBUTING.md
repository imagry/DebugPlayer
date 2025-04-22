# Contributing to Debug Player

Thank you for considering contributing to Debug Player! This document outlines the guidelines for contributing to the project and explains our development workflow.

## Code of Conduct

We expect all contributors to adhere to professional behavior and show respect for all community members. Our goal is to maintain a welcoming environment for everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment following the instructions in the README.md file
4. Create a new branch for your changes

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Key points:

- Use 4 spaces for indentation (not tabs)
- Maximum line length of 88 characters (compatible with black formatter)
- Use docstrings for all modules, classes, and functions
- Use type hints for function parameters and return values

### Commit Guidelines

Write clear, concise commit messages that explain the changes made. Use the imperative mood ("Add feature" not "Added feature").

Structure your commits logically, with each commit representing a coherent change to the codebase.

### Testing

All new features and bug fixes should include appropriate tests. We aim to maintain test coverage above 80%.

```bash
# Run the full test suite
python -m pytest tests/

# Run tests with coverage report
python -m pytest --cov=core --cov=interfaces --cov=plugins tests/
```

### Pull Request Process

1. Update the README.md or documentation with details of any interface changes
2. Add or update tests for your changes
3. Ensure all tests pass locally
4. Push your changes to your fork
5. Create a Pull Request against the main repository

## Project Structure

Please maintain the existing project structure:

```
├── core/               # Core system components
├── interfaces/         # Abstract interfaces for plugins and components
├── plugins/            # Plugin implementations
├── ui/                 # User interface components
├── tests/              # Test suite
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Error Handling Guidelines

- Use custom exception classes for domain-specific errors
- Provide clear, informative error messages
- Validate inputs early to prevent cascading errors
- Use type hints to catch type errors at development time

### Example Exception

```python
class SignalValidationError(Exception):
    """Exception raised for errors in the signal validation process."""
    pass

# Usage
if not isinstance(signal_info, dict):
    raise SignalValidationError(
        f"Signal '{signal_name}' has an invalid definition (not a dictionary): {signal_info}"
    )
```

## Documentation

We use docstrings and inline comments to document the codebase:

- Module docstrings should explain the purpose and usage of the module
- Class docstrings should explain the class's purpose, behavior, and usage
- Method docstrings should explain parameters, return values, and behavior

We follow the Google Python Style Guide for docstrings:

```python
def function_with_types_in_docstring(param1: int, param2: str) -> bool:
    """
    Example function with parameters and return type annotations.
    
    Args:
        param1: The first parameter. An integer.
        param2: The second parameter. A string.
        
    Returns:
        A boolean value indicating success or failure.
        
    Raises:
        ValueError: If param1 is negative.
    """
    if param1 < 0:
        raise ValueError("param1 must be non-negative")
    return param1 > len(param2)
```

## Review Process

All pull requests will be reviewed by at least one core team member. Reviewers will check for:

- Code quality and adherence to style guidelines
- Test coverage and passing tests
- Documentation completeness and clarity
- Overall fit with the project goals and architecture

## Development Roadmap

Please see the README.md file for the current development roadmap. If you're interested in tackling a specific roadmap item, please open an issue to discuss it first.

## Thank You

Your contributions are greatly appreciated. By following these guidelines, we can maintain a high quality, well-documented, and well-tested codebase that serves its users well.
