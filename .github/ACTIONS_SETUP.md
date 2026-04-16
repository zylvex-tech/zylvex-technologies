# GitHub Actions Setup Guide

Use this guide to configure repository and organization settings for reliable CI/CD execution.

## 1) Recommended Actions permissions

In **Repository Settings → Actions → General**:

- **Actions permissions**: Allow required actions/workflows for this repo/org.
- **Workflow permissions**:
  - Prefer **Read and write permissions** when workflows need to comment, update statuses, or push generated changes.
  - If using restricted defaults, grant required per-job permissions in workflow YAML.
- Enable **Allow GitHub Actions to create and approve pull requests** only if your process requires it.

## 2) Token management best practices

- Use the default `GITHUB_TOKEN` for repository-scoped automation whenever possible.
- Explicitly pass tokens to actions that call GitHub APIs.
- Use least-privilege permissions in each job (`permissions:` block).
- Store external credentials in repository/organization secrets; never hardcode tokens.
- Rotate external tokens on a regular schedule.

## 3) Copilot cloud agent setup

- Confirm Copilot/GitHub App is approved for the target repositories.
- Keep branch protections and workflow approvals enabled unless full automation is required.
- If agent-created PRs run workflows from forks or external contributors, require manual approval where appropriate.
- Ensure workflows that post comments or write artifacts have the required token scopes.

## 4) Rate limiting mitigation strategies

- Avoid large AI prompts in CI; only include necessary context.
- Prefer deterministic shell/script checks over model calls for gating logic.
- Use retries with backoff for API calls that can return transient throttling.
- Reduce unnecessary workflow triggers with path filters.
- Split heavy workflows into smaller jobs to reduce repeated failures and reruns.

## 5) Git/authentication reliability checklist

- Always fetch required refs before `git diff` against base branches.
- Configure git identity in automation before any commit/push operations.
- Validate branch/ref availability and provide fallback logic.
- Suppress stderr only for optional operations and log clear warnings.
