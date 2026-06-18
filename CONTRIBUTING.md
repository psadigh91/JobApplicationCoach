# Contributing to Resume Optimizer

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/psadigh91/JobApplicationCoach/issues)
2. If not, create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, Node version)

### Suggesting Features

1. Open an issue with the tag `enhancement`
2. Describe the feature and its use case
3. Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly:
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests  
   cd frontend && npm test
   ```
5. Commit with clear messages
6. Push and create a PR

## Development Setup

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/JobApplicationCoach.git
cd JobApplicationCoach

# 2. Navigate to project directory (if nested)
cd resume-optimizer  # Only if files are in subdirectory

# 3. Run setup
./scripts/setup.sh

# 4. Create .env file
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# 5. Start development
./scripts/start.sh
```

## Code Style

- **Python:** Follow PEP 8, use `black` for formatting
- **JavaScript:** Use ESLint with Airbnb style guide
- **Commits:** Use conventional commits format
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `docs:` - Documentation changes
  - `style:` - Formatting changes
  - `refactor:` - Code restructuring
  - `test:` - Adding tests
  - `chore:` - Maintenance tasks

## Project Structure Guidelines

- Keep components small and focused
- Write tests for new features
- Document complex logic
- Update README if adding new features
- Keep dependencies minimal

## Testing Guidelines

### Backend Tests
```bash
cd backend
pytest tests/
pytest tests/ --cov  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Documentation

When adding features:
- Update README.md with new capabilities
- Add JSDoc/docstrings to functions
- Update API documentation if changing endpoints
- Add examples for complex features

## Questions?

Open an issue or reach out via GitHub discussions.

Thank you for contributing! 🙏
