# Contributing to Autonomous Agent Pro

Thank you for your interest in contributing to Autonomous Agent Pro! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with other contributors and maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Write or update tests as needed
6. Commit your changes: `git commit -m "Add your feature description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request with a clear description

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Irfan430/autonomous-agent-pro.git
cd autonomous-agent-pro

# Install dependencies
pip install -r requirements.txt
cd client && pnpm install && cd ..

# Start development servers
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd client && pnpm dev
```

## Code Style

- **Python**: Follow PEP 8 guidelines. Use `black` for formatting and `flake8` for linting
- **JavaScript/TypeScript**: Follow ESLint configuration. Use Prettier for formatting
- **Commit messages**: Use clear, descriptive messages (e.g., "Add voice input support")

## Testing

Before submitting a PR, ensure:

- All tests pass: `pytest backend/ -v`
- Code is properly formatted: `black backend/` and `pnpm format`
- No linting errors: `flake8 backend/`

## Pull Request Process

1. Update the README.md with any new features or changes
2. Update the todo.md with completed items
3. Ensure all tests pass
4. Request review from maintainers
5. Address any feedback or requested changes

## Reporting Issues

When reporting bugs, please include:

- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

## Feature Requests

For feature requests, please:

1. Check existing issues to avoid duplicates
2. Clearly describe the feature and its use case
3. Explain how it benefits users
4. Suggest implementation approach if possible

## Documentation

When adding new features:

1. Update the README.md with usage examples
2. Add docstrings to all functions and classes
3. Update API documentation if applicable
4. Add comments for complex logic

## Areas for Contribution

- **Bug fixes**: Help fix reported issues
- **Feature implementation**: Implement requested features
- **Documentation**: Improve docs and examples
- **Testing**: Add tests for better coverage
- **Performance**: Optimize slow operations
- **Security**: Report and help fix security issues

## Questions?

Feel free to open an issue or contact the maintainers for questions about contributing.

Thank you for contributing to Autonomous Agent Pro!
