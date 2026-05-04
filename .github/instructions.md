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
codex/<issue-number>-short-description
```

Examples:

```text
codex/12-fix-url-redirect
codex/18-add-api-docs
codex/25-refactor-database-layer
```

Use lowercase words separated by hyphens.

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
git checkout -b codex/<issue-number>-short-description
git add .
git commit -m "<type>: <short summary>"
git push origin codex/<issue-number>-short-description
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
