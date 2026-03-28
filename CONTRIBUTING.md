# Contributing to Binance Futures Trading Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## How to Contribute

### 1. Report a Bug

If you find a bug, please open a GitHub issue with:
- **Title**: Brief description of the bug
- **Description**: Detailed explanation of what went wrong
- **Steps to Reproduce**: How to replicate the issue
- **Expected Behavior**: What should have happened
- **Environment**: Python version, OS, dependencies
- **Logs**: Any relevant error messages or logs

### 2. Request a Feature

To suggest a new feature:
- Open a GitHub issue with title starting with `[FEATURE REQUEST]`
- Describe the use case and why it would be useful
- Provide code examples if applicable
- Label it as `enhancement`

### 3. Submit a Pull Request

#### Prerequisites
- Fork the repository
- Clone your fork: `git clone https://github.com/YOUR_USERNAME/trading_bot.git`
- Create a feature branch: `git checkout -b fix/issue-name`
- Create a virtual environment: `python -m venv .venv`
- Activate it: `source .venv/bin/activate` (or `venv\Scripts\activate` on Windows)
- Install dev dependencies: `pip install -r requirements.txt`

#### Development Workflow
1. Make your changes in the feature branch
2. Test your changes thoroughly:
   ```bash
   # Test CLI
   python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
   
   # Test web server
   python server.py
   ```
3. Ensure no linting errors (if applicable)
4. Write clear, concise commit messages:
   ```
   git commit -m "Fix: correct typo in validator error message"
   git commit -m "Feature: add support for trailing stop orders"
   git commit -m "Docs: update README with deployment instructions"
   ```

#### Commit Message Format

Follow conventional commits:
- `feat:` – New feature
- `fix:` – Bug fix
- `docs:` – Documentation
- `style:` – Code formatting (no logic changes)
- `refactor:` – Code refactoring
- `perf:` – Performance improvements
- `test:` – Test additions/changes
- `chore:` – Maintenance tasks

#### Pull Request Checklist
- [ ] Branch is up-to-date with `main`
- [ ] Changes are focused and don't include unrelated work
- [ ] Commit messages are clear and follow the format above
- [ ] Code follows the project style (see below)
- [ ] Tests pass locally
- [ ] Documentation is updated if needed
- [ ] No credentials or secrets are included

### 4. Code Style

Follow these guidelines:

**Python Style:**
- Follow PEP 8
- Use 4 spaces for indentation
- Use type hints where practical
- Keep functions focused and under 50 lines when possible
- Use descriptive variable names

**Example:**
```python
def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol format.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        
    Returns:
        Uppercased symbol
        
    Raises:
        ValueError: If symbol format is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")
    
    symbol_upper = symbol.upper().strip()
    if len(symbol_upper) < 6:
        raise ValueError("Symbol too short")
    
    return symbol_upper
```

**Comments:**
- Write clear, self-explanatory code first
- Add comments for non-obvious logic
- Keep comments up-to-date with code changes

**Git Hygiene:**
- Rebase before pushing: `git rebase origin/main`
- Squash related commits if requested in review
- Avoid merge commits; use rebase

### 5. Testing

Before submitting a PR, test:

**CLI Testing:**
```bash
# Dry-run test (no actual order)
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

# View orders
python cli.py orders --symbol BTCUSDT

# View account
python cli.py account
```

**Web Server Testing:**
```bash
python server.py
# Visit http://localhost:5000 in browser
# Test balance refresh, open orders, and order placement
```

### 6. Documentation

If your changes affect user-facing functionality:
- Update the README.md
- Add code comments for complex logic
- Update docstrings for modified functions
- Include examples if applicable

---

## Project Structure

```
trading_bot/
├── bot/                  # Core trading logic
│   ├── __init__.py
│   ├── client.py        # Binance REST client
│   ├── orders.py        # Order placement + formatting
│   ├── validators.py    # Input validation
│   └── logging_config.py # Logging setup
├── web/                 # Web UI assets
│   └── index.html       # Dashboard HTML
├── cli.py               # CLI entry point
├── server.py            # Flask web server
├── requirements.txt
├── README.md
└── CONTRIBUTING.md      # This file
```

## Questions or Need Help?

- Open a GitHub Discussion
- Check existing issues/PRs for similar questions
- Review the README.md thoroughly

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for making this project better! 🙏
