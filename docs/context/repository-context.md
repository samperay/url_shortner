# Repository Context

This document summarizes the current shape of the URL Shortener repository so
future contributors and agents can get oriented quickly.

## Purpose

This repository contains a small FastAPI URL shortener backed by SQLite. It is
structured as a learning-friendly service that demonstrates clean application
layers, local Docker usage, Kubernetes deployment basics, automated tests, and
CI quality checks, and a dev GitOps deployment flow using Docker Hub and
Argo CD.

## Application Architecture

The application follows a simple layered flow:

```text
HTML form or HTTP client
        |
FastAPI router
        |
Service layer
        |
Repository layer
        |
SQLite database
```

Key files:

- `app/main.py`: creates the FastAPI app, creates database tables, exposes
  `/health`, and includes the URL router.
- `app/routers/url_router.py`: handles the home page, URL shortening form
  submission, and short-code redirects.
- `app/services.py`: owns business logic for short-code generation, duplicate
  original URL reuse, and short-code collision retries.
- `app/repositories.py`: owns SQLAlchemy persistence and lookup operations.
- `app/database.py`: configures the database engine and request-scoped sessions.
- `app/models.py`: defines the `url_mappings` SQLAlchemy model.
- `app/schemas.py`: defines Pydantic request/response models.
- `app/templates/index.html`: provides the simple HTML form UI.
- `scripts/start.sh`: starts the local FastAPI development server with reload
  enabled.
- `scripts/deploy-dev.sh`: builds the local Docker image and deploys the dev
  Kubernetes overlay to Docker Desktop.
- `scripts/deploy-stage.sh`: builds the local Docker image and deploys the
  stage Kubernetes overlay to Docker Desktop.
- `scripts/deploy-prod.sh`: builds the local Docker image and deploys the prod
  Kubernetes overlay to Docker Desktop after typed confirmation.
- `.github/workflows/publish-dev-image.yml`: builds and pushes the dev Docker
  Hub image, then commits the new image tag back to `dev` for Argo CD.

## Runtime Behavior

- `GET /health` returns `{"status": "ok"}` for health checks.
- `GET /` renders the HTML form.
- `POST /shorten` accepts `original_url` form data, creates or reuses a short
  code, and renders the short URL.
- `GET /{short_code}` redirects to the original URL when found.
- Missing short codes return `404` with `Short URL not found`.

The default database is `sqlite:///./url_shortener.db`. Kubernetes deployment
overrides this with `sqlite:////data/url_shortener.db` so the database lives in
the mounted `/data` path inside the container.

## Testing

The test suite lives in `tests/`:

- `tests/unit/`: service, repository, schema, and database-session tests.
- `tests/integration/`: FastAPI route tests using `TestClient`.
- `tests/conftest.py`: creates an isolated in-memory SQLite database and
  overrides the app database dependency for integration tests.

Run all tests locally:

```bash
.venv/bin/python -m pytest -q
```

Run tests with coverage:

```bash
.venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-report=xml
```

The suite currently covers the `app` package and reports full app coverage.

## CI And Quality

The main quality workflow is `.github/workflows/ci.yml`.

It runs on every push and pull request update:

1. Install dependencies from `requirements.txt`.
2. Run Ruff linting with `python -m ruff check .`.
3. Run Ruff formatting checks with `python -m ruff format --check .`.
4. Run pytest with coverage.
5. Upload coverage artifacts.
6. Publish coverage in the workflow summary.
7. Post or update a sticky PR comment with coverage details.

Ruff, pytest, and coverage options are configured in `pyproject.toml`.

The dev image publishing workflow is `.github/workflows/publish-dev-image.yml`.
It runs on pushes to `dev`, builds `sunlnx/url-shortener:dev_<short-sha>`,
pushes it to Docker Hub, updates the dev Kustomize image tag, and commits that
tag update back to `dev`.

## Deployment Notes

The repository includes Docker, local Kubernetes support, and dev GitOps
deployment:

- `scripts/start.sh`: runs the local Uvicorn development server.
- `scripts/deploy-dev.sh`: deploys the `url-shortener-dev` namespace locally.
- `scripts/deploy-stage.sh`: deploys the `url-shortener-stage` namespace
  locally.
- `scripts/deploy-prod.sh`: deploys the `url-shortener-prod` namespace locally
  after manual confirmation.
- `Dockerfile`: builds the FastAPI app image.
- `k8s/base/deployment.yaml`: runs the app with readiness/liveness probes and a
  learning-friendly `emptyDir` SQLite volume.
- `k8s/base/service.yaml`: exposes the app through a Docker Desktop NodePort.
- `k8s/environments/dev`: targets Docker Hub image `sunlnx/url-shortener` for
  Argo CD deployment to `url-shortener-dev`.
- `k8s/environments/stage` and
  `k8s/environments/prod`: create environment namespaces and overlay
  environment-specific settings.
- Argo CD watches the `dev` branch and deploys the rendered dev overlay.

Deployment docs are grouped under `docs/deployment/`. The Kubernetes layout uses
a reusable `k8s/base/` manifest and environment overlays under
`k8s/environments/` for `dev`, `stage`, and `prod`.
Kubernetes learning exercises are grouped under `docs/learning/`.

## Repository Workflow

The repository instructions live in `.github/instructions.md`.

Important workflow expectations:

- Create or use a GitHub issue before implementation work.
- Use branches named `codex/<issue-number>-short-description`.
- Keep PR descriptions structured with summary, testing, risk, and checklist.
- Apply labels and assignees when possible.
- Do not run `git push` without explicit user approval.

Dev deployment expectations:

- Merge feature PRs into `dev`.
- Let GitHub Actions publish `sunlnx/url-shortener:dev_<short-sha>`.
- Let the workflow commit the updated dev image tag.
- Let Argo CD sync the `dev` overlay into `url-shortener-dev`.
- Use `scripts/deploy-*.sh` only for manual Docker Desktop local testing.

## Current Documentation Layout

```text
docs/
├── context/
│   └── repository-context.md
├── deployment/
│   ├── docker-desktop-kubernetes.md
│   └── environment-promotion.md
└── learning/
    └── kubernetes-break-fix.md
```

Local scripts live under:

```text
scripts/
├── deploy-dev.sh
├── deploy-prod.sh
├── deploy-stage.sh
└── start.sh
```
