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
3. Run `uv run invoke check-all` — must pass before opening PR
4. Rebase on `origin/develop` to resolve conflicts
5. Push branch and open PR targeting `develop`
6. Fill out PR template (Why, What changed, How to review, How to test)
7. CI must pass (lint, tests, security scan)
8. **CodeRabbit will automatically post an AI review** — address actionable comments before requesting human review
9. Request review — at least 1 approval required
10. Address all review comments
11. Merge via **squash merge** (keeps history clean)
12. Delete the feature branch after merge

### Key Rules

- **Keep PRs small** — aim for < 400 lines changed
- **One feature/fix per PR** — don't combine unrelated changes
- **PR title uses Conventional Commits** — this becomes the merge commit message
- **Don't force-push during review** — it destroys comment context

> For comprehensive guidance, see [Pull Request Best Practices](../guides/pull-request-best-practices.md).

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

## Issue Lifecycle

Every issue follows this progression:

| Stage           | Action                                                                          |
| --------------- | ------------------------------------------------------------------------------- |
| **Created**     | Assignee set, label set, `## Sub-tasks` and `## Acceptance Criteria` filled out |
| **In Progress** | Branch created matching the `## Branch` field in the issue body                 |
| **In Review**   | PR opened with `Closes #N` in the body — links the PR to the issue              |
| **Done**        | PR merged → issue auto-closed by GitHub                                         |

As each sub-task is completed, **edit the issue body and tick the checkbox** so progress is visible without reading the commit history.

> For full details, see [Issue Management](./issue-management.md).

## Git Hooks

Local hooks enforce GitFlow rules before code leaves your machine.

### Pre-commit hooks (via `pre-commit`)

Installed with `uv run pre-commit install`. Runs on every commit:

- Linting and formatting (ruff)
- Secret detection (detect-secrets, gitleaks)
- **Branch protection** — blocks commits directly to `main` or `develop`

### Pre-push hook

Blocks `git push` directly to `main` or `develop`. Install with:

```bash
ln -sf ../../.githooks/pre-push .git/hooks/pre-push
```

The hook is stored in `.githooks/pre-push` (version-controlled). It ensures all changes go through Pull Requests, even if GitHub branch protection is misconfigured.

## Agent-Specific Rules

> **AI agents MUST always use this workflow. No exceptions.**

1. Create a feature branch: `git checkout -b feat/<description> develop`
2. Make changes and run `uv run invoke check-all`
3. Commit with Conventional Commits format
4. Push and open a PR: `gh pr create --base develop`
5. **Wait for CodeRabbit AI review** — address any flagged issues before requesting human review
6. Wait for CI to pass and PR to be merged
7. **Do NOT SSH to the VM to deploy changes.** The CD pipeline handles deployment.
8. **Do NOT push directly to `main` or `develop`.** Branch protection will reject it.
