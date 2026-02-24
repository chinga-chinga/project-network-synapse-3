# Git Workflow

## Branch Strategy

| Branch    | Purpose                                                 | Merges From          |
| --------- | ------------------------------------------------------- | -------------------- |
| `main`    | Production-ready code. Protected — no direct commits.   | `develop` via PR     |
| `develop` | Integration branch. All feature work merges here first. | Feature/fix branches |

## Branch Naming

| Pattern                  | Use Case                 | Example                        |
| ------------------------ | ------------------------ | ------------------------------ |
| `feature/<description>`  | New features             | `feature/bgp-validation`       |
| `fix/<description>`      | Bug fixes                | `fix/schema-loader-timeout`    |
| `dev/<description>`      | Infrastructure / tooling | `dev/ci-pipeline-update`       |
| `docs/<description>`     | Documentation only       | `docs/add-runbook`             |
| `refactor/<description>` | Code refactoring         | `refactor/temporal-activities` |

## Commit Conventions

Use **Conventional Commits** format:

```
<type>: <short description>

[optional body]

[optional footer]
```

### Types

| Type       | When to Use                             |
| ---------- | --------------------------------------- |
| `feat`     | New feature or capability               |
| `fix`      | Bug fix                                 |
| `docs`     | Documentation only                      |
| `style`    | Formatting, whitespace (no code change) |
| `refactor` | Code restructuring (no behavior change) |
| `test`     | Adding or updating tests                |
| `chore`    | Build, CI, tooling changes              |
| `perf`     | Performance improvement                 |

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

## Deployment (GitOps)

Deployment is **fully automated** via GitHub Actions.

| Trigger                    | Target               | Workflow                       |
| -------------------------- | -------------------- | ------------------------------ |
| PR merge to `main`         | GCP VM (staging)     | `.github/workflows/deploy.yml` |
| Manual `workflow_dispatch` | dev / staging / prod | `.github/workflows/deploy.yml` |

### Pipeline stages

1. **Validate** — `uv run invoke check-all` + unit tests
2. **Deploy** — SSH to VM → `git pull` → `uv sync` → `systemctl restart synapse-worker`
3. **Health check** — verify worker process, Temporal, Infrahub

### Required GitHub Secrets

| Secret       | Purpose                               |
| ------------ | ------------------------------------- |
| `VM_SSH_KEY` | SSH private key for the deployment VM |
| `VM_HOST`    | IP address of the GCP VM              |

## Agent-Specific Rules

> **AI agents MUST always use this workflow. No exceptions.**

1. Create a feature branch: `git checkout -b feat/<description> develop`
2. Make changes and run `uv run invoke check-all`
3. Commit with Conventional Commits format
4. Push and open a PR: `gh pr create --base develop`
5. Wait for CI to pass and PR to be merged
6. **Do NOT SSH to the VM to deploy changes.** The CD pipeline handles deployment.
7. **Do NOT push directly to `main` or `develop`.** Branch protection will reject it.
