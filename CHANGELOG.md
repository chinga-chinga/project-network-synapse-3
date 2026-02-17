# Changelog

All notable changes to this project will be documented in this file.

This project uses [Towncrier](https://towncrier.readthedocs.io/) for changelog management. See `dev/guidelines/changelog.md` for how to add entries.

<!-- towncrier release notes start -->

## [0.1.0] - 2025-02-17

### Added

- Initial project structure with Infrahub SoT integration
- Nokia SR Linux schema extensions (DcimDevice, InterfacePhysical)
- Infrahub schema loader and seed data population scripts
- Jinja2 templates for SR Linux BGP and interface configuration
- Containerlab spine-leaf topology definition (3 nodes)
- Temporal worker scaffold with workflow and activity stubs
- CI/CD pipeline with GitHub Actions (PR validation, CI, deploy, build)
- Pre-commit hooks (ruff, detect-secrets, gitleaks)
- Monorepo workspace with uv (backend + workers packages)
- Invoke task runner for unified development CLI
- AI agent developer documentation (Context Nuggets pattern)
