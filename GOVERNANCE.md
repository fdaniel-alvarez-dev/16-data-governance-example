# Governance and repository protections

This repository is designed to be safe-by-default and audit-friendly.

## Forking
GitHub supports disabling forks only for certain repository ownership/plan combinations (typically organization-owned repositories).

Status (reviewed 2026-03-06):
- Current API state: `allow_forking=true` (public repository).
- Attempted to disable forking via the GitHub REST API setting `allow_forking=false`.
- GitHub returned HTTP 422 with the message: “Allow forks can only be changed on org-owned repositories”.
- Result: forking cannot be disabled here; the closest enforceable alternative is to move the repository under an organization that supports fork restrictions, or make it private.

## Branch protection (recommended)
If you adopt this repository for a real system, enable:
- required PR reviews
- status checks required before merge
- signed commits (if your workflow supports it)
- restricted push access to `main`

## Secret hygiene
- Do not store credentials in git.
- Use GitHub Actions OIDC or a secrets manager for deployments.
