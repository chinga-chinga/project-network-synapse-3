---
description: Run all code quality checks (linting, formatting, security)
---

# Run Code Quality Checks

This workflow runs the entire suite of code quality checks across the workspace.

// turbo-all

1. Run Ruff formatting check to ensure all code is properly formatted.

```bash
uv run ruff format --check .
```

2. Run Ruff linter to catch any code quality issues or anti-patterns.

```bash
uv run ruff check .
```

3. Run the security scanner (Bandit) to check for vulnerabilities.

```bash
uv run invoke scan
```

4. Run the unit tests to verify backend logic.

```bash
uv run invoke backend.test-unit
```
