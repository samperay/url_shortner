# Environment Promotion Flow

This repository supports three Kubernetes environments:

| Environment | Branch | Namespace | Local NodePort |
| --- | --- | --- | --- |
| Development | `dev` | `url-shortener-dev` | `30080` |
| Stage | `stage` | `url-shortener-stage` | `30081` |
| Production | `prod` | `url-shortener-prod` | `30082` |

For now these environments target Docker Desktop Kubernetes. Later, the same
layout can be pointed at a cloud Kubernetes cluster by changing image publishing
and cluster credentials, while keeping the promotion model.

## One-Time Branch Setup

If the `dev`, `stage`, and `prod` branches do not exist yet, create them from
the current stable `master` branch:

```bash
git switch master
git pull origin master
git branch dev
git branch stage
git branch prod
```

Push the branches only after approval:

```bash
git push origin dev stage prod
```

## Branch Promotion Rules

Use this branch flow:

1. Create feature work from `dev`.
2. Open feature PRs into `dev`.
3. After `dev` testing passes, open a PR from `dev` into `stage`.
4. After `stage` testing passes, open a PR from `stage` into `prod`.
5. Deploy to the `prod` namespace only after manual approval.

Recommended branch names:

```text
feature/<short-description>
```

Promotion PRs should be small and explicit:

```text
feature/my-change -> dev
dev -> stage
stage -> prod
```

## Docker Desktop Deployment

Build the local image before deploying any environment:

```bash
docker build -t url-shortener:dev .
```

Deploy development:

```bash
kubectl apply -k k8s/environments/dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
```

Deploy stage:

```bash
kubectl apply -k k8s/environments/stage
kubectl rollout status deployment/url-shortener -n url-shortener-stage
kubectl port-forward svc/url-shortener 30081:80 -n url-shortener-stage
```

Deploy production after manual approval:

```bash
kubectl apply -k k8s/environments/prod
kubectl rollout status deployment/url-shortener -n url-shortener-prod
kubectl port-forward svc/url-shortener 30082:80 -n url-shortener-prod
```

Keep the `kubectl port-forward` command running while you test the app.

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

- Confirm the `stage -> prod` PR is approved and merged.
- Confirm CI passed on `prod`.
- Confirm the exact image tag or commit being deployed.
- Get explicit manual approval from the environment owner.
- Run the production `kubectl apply -k k8s/environments/prod` command only
  after that approval.

## Future Cloud Migration Notes

When moving away from Docker Desktop:

- Push images to a registry instead of using `imagePullPolicy: Never`.
- Use unique image tags per commit or release.
- Replace `emptyDir` with persistent storage or a managed database.
- Store cluster credentials in GitHub Actions environments or a deployment
  platform.
- Configure the GitHub `production` environment with required reviewers before
  allowing production deployments.
