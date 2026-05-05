# Codex Agent Instructions

## Goal

When the user provides a task prompt, Codex should manage the full GitHub workflow:

1. Understand the requested change.
2. Create or update a GitHub issue.
3. Add suitable labels/tags to the issue.
4. Implement the fix or feature.
5. Create a pull request.
6. Fill the PR title, description, labels, assignees, and related issue links.

---

## Issue Creation Rules

When a user asks for a new feature, bug fix, refactor, documentation update, test improvement, or maintenance task, create a GitHub issue first unless an existing issue is clearly referenced.

If the user already provides an issue number, use that issue instead of creating a duplicate.

---

## Issue Title Format

Use one of these prefixes:

- `bug:` for defects
- `feature:` for new functionality
- `refactor:` for code restructuring
- `docs:` for documentation changes
- `test:` for test-related work
- `chore:` for maintenance tasks

Examples:

```text
bug: fix URL redirect failure for invalid short code
feature: add API endpoint for creating short URLs
docs: add EchoAPI testing guide
```

---

## Issue Description Template

Use this format when creating an issue:

```md
## Summary

Briefly describe the requested change.

## Problem

Explain the current issue, missing functionality, or improvement needed.

## Expected Behavior

Describe what should happen after the change.

## Scope of Work

- [ ] Code changes
- [ ] Tests added or updated
- [ ] Documentation updated if required

## Acceptance Criteria

- [ ] The issue is resolved
- [ ] Existing functionality is not broken
- [ ] Tests pass successfully
- [ ] Code is clean and readable
- [ ] Documentation is updated if required

## Notes

Add any assumptions, constraints, or implementation details.
```

---

## Label Rules

Apply labels based on the task type.

### Type Labels

Use one primary type label:

- `bug`
- `feature`
- `refactor`
- `documentation`
- `test`
- `chore`

### Priority Labels

Use one priority label when possible:

- `priority: low`
- `priority: medium`
- `priority: high`

Default to:

```text
priority: medium
```

### Area Labels

Apply relevant area labels when applicable:

- `area: backend`
- `area: frontend`
- `area: database`
- `area: api`
- `area: ci-cd`
- `area: docs`
- `area: tests`
- `area: config`

### Status Labels

Use the following workflow labels:

When the issue is created:

```text
status: ready
```

When implementation starts:

```text
status: in-progress
```

When the PR is created:

```text
status: in-review
```

---

## Assignee Rules

Assign the issue and PR to the repository owner or current authenticated user when possible.

If the user explicitly mentions an assignee, use that assignee.

If assignee assignment fails due to permission issues, continue the workflow and mention the failure in the final response.

---

## Branch Naming Rules

Create a branch using this format:

```text
feature/<issue-number>-short-description
```

Examples:

```text
feature/12-fix-url-redirect
feature/18-add-api-docs
feature/25-refactor-database-layer
```

Use lowercase words separated by hyphens.

---

## Environment Promotion Rules

Use this promotion flow for application changes:

1. Create feature branches from `dev`.
2. Open feature PRs against the `dev` branch.
3. After testing passes in `dev`, open a promotion PR from `dev` to `stage`.
4. After testing passes in `stage`, open a promotion PR from `stage` to
   `master`.
5. Deploy production only after the `stage` changes have reached `master` and
   explicit manual approval is given.

In this repository, the production branch target is `master`. If a user says
`prod branch`, `production branch`, or asks to promote production changes, treat
that as `master` unless they explicitly ask for the legacy `prod` branch by
name. Do not create `stage` to `prod` or `prod` to `master` promotion PRs for
the normal flow; create `stage` to `master` instead.

GitHub only auto-closes issues when a closing keyword reaches the repository
default branch, currently `master`. Feature PRs into `dev` may still include
`Closes #<issue-number>` for traceability, but every promotion PR into `master`
must also include the closing keywords for all issues carried by the promotion:

```text
Closes #<issue-number>
Closes #<another-issue-number>
```

Before opening a `stage` to `master` promotion PR, review the merged feature PRs
being promoted and copy their related issue references into the promotion PR
body. Do not rely on `dev` or `stage` PR closing keywords to close issues.

For Docker Desktop Kubernetes:

- Merge `dev` changes and let `.github/workflows/publish-dev-image.yml`
  publish `sunlnx/url-shortener:dev_<short-sha>`.
- Let Argo CD deploy `dev` branch changes to the `url-shortener-dev`
  namespace.
- Merge `dev` into `stage` and let
  `.github/workflows/publish-stage-image.yml` publish
  `sunlnx/url-shortener:stage_<short-sha>`.
- Let Argo CD deploy `stage` branch changes to the `url-shortener-stage`
  namespace.
- Treat `master` as the production branch and deploy the `master` commit to the
  `url-shortener-prod` namespace only after manual approval.

Use `scripts/deploy-dev.sh`, `scripts/deploy-stage.sh`, and
`scripts/deploy-prod.sh` only for manual local Docker Desktop testing. These
scripts build and deploy the local `url-shortener:dev` image.

Do not automatically deploy production from a branch push or merge.

---

## Git Push Approval Rules

Never run `git push` without explicit user approval.

Before pushing, summarize:

- Branch name
- Commits to be pushed
- Target remote
- Related PR or issue

Wait for the user to approve before running `git push`.

---

## Pull Request Rules

After implementing the fix, create a pull request.

The PR must include:

- Clear title
- Detailed description
- Related issue link
- Summary of changes
- Testing details
- Risk or migration notes
- Checklist
- Labels copied from the issue
- Assignee when possible

For promotion PRs into `master`, the related issue section must include all
issues included in the promotion with GitHub closing keywords, one per line.

---

## PR Title Format

Use this format:

```text
<type>: <short summary>
```

Examples:

```text
bug: fix URL redirect for invalid short codes
feature: add URL creation form
docs: add API testing guide
```

---

## PR Description Template

Use this format:

```md
## Summary

Describe what this PR changes.

## Related Issue

Closes #<issue-number>

## Changes Made

- Added/updated relevant implementation
- Added/updated tests
- Updated documentation if required

## Testing

Describe how the change was tested.

- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] API tested successfully
- [ ] UI flow verified

## Screenshots / Evidence

Add screenshots, logs, API responses, or sample output if applicable.

## Risk

Mention any risk, migration concern, database change, or backward compatibility issue.

## Checklist

- [ ] Code follows the project structure
- [ ] No secrets or sensitive data committed
- [ ] Tests added or updated where required
- [ ] Documentation updated where required
- [ ] PR is linked to the issue
- [ ] Labels are applied
- [ ] Assignee is added if possible
```

---

## PR Labels

Copy relevant labels from the issue to the PR.

Always include:

```text
status: in-review
```

Remove or replace `status: in-progress` if the repository uses only one status label at a time.

---

## Commit Message Rules

Use clear conventional commit messages.

Examples:

```text
fix: handle invalid short URL redirects
feat: add URL creation form
docs: add API testing guide
refactor: simplify database session handling
test: add redirect endpoint tests
chore: update project instructions
```

---

## Testing Rules

Before creating the PR:

1. Run existing tests if available.
2. Add new tests for new behavior.
3. Do not remove existing tests unless clearly required.
4. Mention test results in the PR description.

If tests cannot be run, mention why clearly in the PR.

Example:

```text
Tests not run because the project does not currently include a test suite.
```

---

## Documentation Rules

Update documentation when:

- New API endpoints are added
- Existing behavior changes
- Setup steps change
- Environment variables are added or modified
- Database schema changes
- New commands or workflows are introduced

---

## Safety Rules

Never commit:

- `.env`
- Secrets
- Tokens
- API keys
- Passwords
- Local database files
- Generated cache files
- Virtual environments

Make sure these are ignored when applicable:

```gitignore
.env
.env.*
*.db
*.sqlite
*.sqlite3
__pycache__/
.venv/
venv/
.pytest_cache/
```

---

## Error Handling Rules

If GitHub issue creation fails, explain the exact error and continue with code changes if possible.

If PR creation fails with:

```text
403 Resource not accessible by integration
```

Then explain that the GitHub connector or integration does not have enough permission to create the PR.

In that case, provide manual PR steps:

```bash
git checkout -b feature/<issue-number>-short-description
git add .
git commit -m "<type>: <short summary>"
git push origin feature/<issue-number>-short-description
```

Then ask the user to open the PR manually from GitHub.

---

## Final Response Rules

After completing the work, summarize:

1. Issue created or updated
2. Labels applied
3. Branch created
4. Files changed
5. Tests run
6. PR created
7. PR link

If any step fails due to permissions, clearly mention the failed step and the exact error.
