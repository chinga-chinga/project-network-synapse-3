# Git Workflow

## Branch Strategy

| Branch | Purpose | Merges From |
|--------|---------|-------------|
| `main` | Production-ready code. Protected — no direct commits. | `develop` via PR |
| `develop` | Integration branch. All feature work merges here first. | Feature/fix branches |

## Branch Naming

| Pattern | Use Case | Example |
|---------|----------|---------|
| `feature/<description>` | New features | `feature/bgp-validation` |
| `fix/<description>` | Bug fixes | `fix/schema-loader-timeout` |
| `dev/<description>` | Infrastructure / tooling | `dev/ci-pipeline-update` |
| `docs/<description>` | Documentation only | `docs/add-runbook` |
| `refactor/<description>` | Code refactoring | `refactor/temporal-activities` |

## Commit Conventions

Use **Conventional Commits** format:

```
<type>: <short description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no code change) |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding or updating tests |
| `chore` | Build, CI, tooling changes |
| `perf` | Performance improvement |

### Examples

```bash
feat: add BGP session validation activity
fix: handle timeout in schema loader (#42)
docs: add infrastructure connection guide
chore: migrate from black to ruff
test: add unit tests for config generator
```

## Pull Request Process

1. Create branch from `develop`
2. Make changes, commit with conventional commit messages
3. Push branch and open PR targeting `develop`
4. Fill out PR template (Why, What changed, How to test)
5. CI must pass (lint, tests, security scan)
6. Request review
7. Merge via squash merge (keeps history clean)

## Submodule Handling

The `library/schema-library/` directory is a Git submodule pointing to `opsmill/schema-library`.

```bash
# Initialize submodule after cloning
git submodule update --init --recursive

# Update submodule to latest
git submodule update --remote library/schema-library
```
