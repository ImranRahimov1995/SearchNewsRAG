# Git Commit Message Convention

## Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (deps, configs, etc.)
- **perf**: Performance improvements

## Examples

### Feature
```bash
git commit -m "feat(telegram): add async message collection

- Implement TelegramCollector with async support
- Add date filtering functionality
- Include JSONWriter for output"
```

### Bug Fix
```bash
git commit -m "fix(parser): handle None dates in date filter

DateFilter now properly handles None values by
returning False instead of raising AttributeError"
```

### Tests
```bash
git commit -m "test(telegram): add TelegramCollector tests

- Add fixtures for mock client and messages
- Test basic collection workflow
- Test edge cases (None date, None text)
- Achieve 94% coverage on base.py"
```

### Refactor
```bash
git commit -m "refactor(tests): apply DRY principles

- Extract common fixtures to conftest.py
- Create factory fixtures for messages
- Reduce test code from 150 to 90 lines"
```

### Documentation
```bash
git commit -m "docs: add pre-commit setup guide

- Create comprehensive pre-commit documentation
- Add Makefile for common commands
- Include troubleshooting section"
```

### Chore
```bash
git commit -m "chore: add pre-commit hooks configuration

- Configure black, ruff, mypy, bandit
- Set up pytest in pre-commit
- Add coverage checks for git push"
```
