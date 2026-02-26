---
description: Setup the network-synapse project environment
---

# Setup Project Environment

This workflow initializes the project, downloads all dependencies, and sets up Git hooks.

// turbo-all

1. Initialize git submodules for the schema library.

```bash
git submodule update --init --recursive
```

2. Sync all python dependencies using uv.

```bash
uv sync --all-groups
```

3. Install pre-commit hooks for code quality.

```bash
uv run pre-commit install
```
