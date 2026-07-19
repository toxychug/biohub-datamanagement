# Contributing to BioHub Change Management & Audit Service

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Report issues and suggestions constructively
- Collaborate in good faith

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit with clear messages: `git commit -m "Add feature description"`
6. Push to your fork
7. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/biohub-datamanagement.git
cd biohub-datamanagement

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local config

# Run tests
pytest -v
```

## Code Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Add tests for new features
- Keep functions focused and small

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_audit_service.py -v
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for your changes
3. Ensure all tests pass: `pytest`
4. Update CHANGELOG if applicable
5. Provide clear PR description

## Reporting Issues

- Check if issue already exists
- Include reproduction steps
- Provide environment details (OS, Python version)
- Share error logs or screenshots if relevant

## Questions?

Create an issue or contact the BioHub Team.

Thank you for contributing! 🎉
