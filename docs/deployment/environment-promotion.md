# Environment Promotion Flow

This repository supports three Kubernetes environments:

| Environment | Branch | Namespace | Local NodePort |
| --- | --- | --- | --- |
| Development | `dev` | `url-shortener-dev` | `30080` |
| Stage | `stage` | `url-shortener-stage` | `30081` |
| Production | `master` | `url-shortener-prod` | `30082` |

For now these environments target Docker Desktop Kubernetes. Later, the same
layout can be pointed at a cloud Kubernetes cluster by changing image publishing
and cluster credentials, while keeping the promotion model.

For one-time Argo CD setup, see [Install Argo CD on Docker Desktop Kubernetes](argocd-install.md).

## One-Time Branch Setup

If the `dev` and `stage` branches do not exist yet, create them from
the current stable `master` branch:

```bash
git switch master
git pull origin master
git branch dev
git branch stage
```

Push the branches only after approval:

```bash
git push origin dev stage
```

## Branch Promotion Rules

Use this branch flow:

1. Create feature work from `dev`.
2. Open feature PRs into `dev`.
3. After `dev` testing passes, open a PR from `dev` into `stage`.
4. After `stage` testing passes, open a PR from `stage` into `master`.
5. Deploy to the production namespace only after `master` is updated and manual
   approval is given.

Recommended branch names:

```text
feature/<short-description>
```

Promotion PRs should be small and explicit:

```text
feature/my-change -> dev
dev -> stage
stage -> master
```

## Issue Closing During Promotion

GitHub auto-closes issues only when a closing keyword is merged into the
repository default branch, currently `master`.

Feature PRs into `dev` can include `Closes #<issue-number>` for traceability,
but the final `stage -> master` promotion PR must also include every issue that
the promotion completes:

```text
Closes #11
Closes #13
```

Before opening the `stage -> master` PR, review the merged feature PRs included
in the promotion and copy their related issue references into the promotion PR
body. That ensures GitHub closes the issues automatically when the promotion PR
is merged.

## Docker Desktop Deployment

Build the local image before deploying any environment:

```bash
docker build -t url-shortener:dev .
```

For non-Kubernetes local development, start the app with:

```bash
./scripts/start.sh
```

Deploy development:

```bash
./scripts/deploy-dev.sh
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
```

The script builds the local Docker image, applies `k8s/environments/dev`, and
waits for the dev rollout.

Deploy stage:

```bash
./scripts/deploy-stage.sh
kubectl port-forward svc/url-shortener 30081:80 -n url-shortener-stage
```

Deploy production after manual approval:

```bash
./scripts/deploy-prod.sh
kubectl port-forward svc/url-shortener 30082:80 -n url-shortener-prod
```

The production script asks you to type `prod` before it applies the production
overlay.

Keep the `kubectl port-forward` command running while you test the app.

## Automatic Dev And Stage Image Publishing

The workflow `.github/workflows/publish-dev-image.yml` builds and pushes a Docker
Hub image when changes are pushed to `dev`.

The image tag format is:

```text
sunlnx/url-shortener:dev_<short-commit-id>
```

After pushing the image, the workflow updates
`k8s/environments/dev/kustomization.yaml` with the new tag and commits that
change back to `dev`. Argo CD watches the `dev` branch and deploys the updated
image to the `url-shortener-dev` namespace.

The workflow `.github/workflows/publish-stage-image.yml` runs when changes are
pushed to `stage`, including when a `dev -> stage` promotion PR is merged. It
builds and pushes:

```text
sunlnx/url-shortener:stage_<short-commit-id>
```

After pushing the image, the workflow updates
`k8s/environments/stage/kustomization.yaml` with the new tag and commits that
change back to `stage`. Argo CD should watch the `stage` branch and deploy the
updated stage overlay to the `url-shortener-stage` namespace.

These workflows require these GitHub repository secrets:

- `DOCKER_HUB_LOGIN`: Docker Hub username
- `DOCKER_HUB_TOKEN`: Docker Hub access token or password

The local deployment scripts are still for Docker Desktop-only manual testing.
They build `url-shortener:dev`, apply the selected overlay, and override the
Deployment to use the local Docker Desktop image.

Argo CD itself must be installed once in the cluster, and the dev/stage
Applications must be created before the branch watcher flow can sync changes.
See [Install Argo CD on Docker Desktop Kubernetes](argocd-install.md).

## Health Checks

Verify each environment:

```bash
curl http://localhost:30080/health  # dev
curl http://localhost:30081/health  # stage
curl http://localhost:30082/health  # prod
```

Expected response:

```json
{"status":"ok"}
```

## Production Approval

Do not deploy production as part of an automatic branch push.

GitHub-hosted Actions cannot deploy into Docker Desktop Kubernetes on your
machine. While this project targets Docker Desktop, production deployment is a
manual local command after approval. When the project moves to a cloud
Kubernetes cluster, use GitHub Environments with required reviewers for the
production deployment job.

Before production deployment:

- Confirm the `stage -> master` PR is approved and merged.
- Confirm CI passed on `master`.
- Confirm the exact image tag or commit being deployed.
- Get explicit manual approval from the environment owner.
- Run `./scripts/deploy-prod.sh` only after that approval.

## Future Cloud Migration Notes

When moving away from Docker Desktop:

- Continue using unique image tags per commit or release.
- Replace `emptyDir` with persistent storage or a managed database.
- Store cluster credentials in GitHub Actions environments or a deployment
  platform.
- Configure the GitHub `production` environment with required reviewers before
  allowing production deployments.
