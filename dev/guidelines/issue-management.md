# Issue Management

This document defines how GitHub issues are created, managed, and closed throughout the development lifecycle.

## Issue Anatomy

Every issue must have the following fields populated before work begins:

| Field                   | Required       | Notes                                                                        |
| ----------------------- | -------------- | ---------------------------------------------------------------------------- |
| **Assignee**            | ✅             | The person / agent responsible for delivering this issue                     |
| **Label**               | ✅             | At minimum one of: `enhancement`, `bug`, `task`, `security`, `observability` |
| **Milestone**           | ⭐ Recommended | Group issues into delivery milestones (e.g. Week 5, v0.3.0)                  |
| **Branch**              | ✅             | The branch name to be created for this work (in issue body)                  |
| **Sub-tasks**           | ✅             | Checkbox list of concrete steps in the `## Sub-tasks` section                |
| **Acceptance Criteria** | ✅             | Definition of done in `## Acceptance Criteria` section                       |

## Issue Body Template

All issues should follow this structure:

```markdown
## Description

<1–3 sentences describing the problem or feature>

## Sub-tasks

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Acceptance Criteria

- [ ] Criterion 1 (testable, observable)
- [ ] Criterion 2

## Branch

`feature/<short-description>`
```

> Use `feature/` for product features, `fix/` for bugs, `dev/` for infrastructure/tooling, `docs/` for documentation.

## Issue Lifecycle

```
Created → Assigned → In Progress → In Review → Done
```

| Stage           | What happens                                                                         |
| --------------- | ------------------------------------------------------------------------------------ |
| **Created**     | Issue body filled out, assignee set, label set, milestone set                        |
| **In Progress** | Branch created (`git checkout -b <branch> develop`), sub-tasks checked as work lands |
| **In Review**   | PR opened with `Closes #N` in the body — links PR to issue on GitHub                 |
| **Done**        | PR merged → issue **auto-closed** by GitHub via `Closes #N`                          |

## Linking a PR to an Issue

In the PR body, always include:

```
Closes #<issue-number>
```

This causes GitHub to:

- Show the linked PR on the issue sidebar
- Auto-close the issue when the PR merges to the target branch

## Tracking Sub-task Progress

As you commit work that completes a sub-task, edit the issue body and tick the checkbox:

```markdown
- [x] Step 1 ← done
- [ ] Step 2 ← still pending
```

This gives anyone viewing the issue a real-time progress picture without needing to read commit history.

## Agent Rules

> **AI agents MUST follow these rules when working on issues.**

1. **Never start work without an assignee** — add yourself or `chinga-chinga` if no human is assigned.
2. **Always create a branch** matching the `## Branch` field in the issue body.
3. **Check off sub-tasks** in the issue body as each one is completed.
4. **Always open a PR with `Closes #N`** to link work back to the issue.
5. **Never close an issue manually** — let the PR merge trigger auto-close.
6. **Update `## Acceptance Criteria`** if scope changes during implementation; don't silently deviate.
