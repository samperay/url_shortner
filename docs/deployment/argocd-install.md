# Install Argo CD On Docker Desktop Kubernetes

Use this guide to install Argo CD into Docker Desktop Kubernetes and connect it
to this repository's `dev` and `stage` GitOps overlays.

## Prerequisites

1. Install Docker Desktop.
2. Enable Kubernetes in Docker Desktop.
3. Install `kubectl`.
4. Confirm your Kubernetes context points to Docker Desktop:

```bash
kubectl config current-context
```

Expected context:

```text
docker-desktop
```

If needed:

```bash
kubectl config use-context docker-desktop
```

## 1. Install Argo CD

Create the Argo CD namespace and apply the official stable install manifest:

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for Argo CD to become ready:

```bash
kubectl rollout status deployment/argocd-server -n argocd
kubectl rollout status deployment/argocd-repo-server -n argocd
kubectl rollout status deployment/argocd-applicationset-controller -n argocd
kubectl rollout status statefulset/argocd-application-controller -n argocd
```

Check the installed resources:

```bash
kubectl get pods -n argocd
kubectl get svc -n argocd
```

## 2. Install The Argo CD CLI

On macOS with Homebrew:

```bash
brew install argocd
```

Confirm the CLI works:

```bash
argocd version --client
```

## 3. Open The Argo CD UI

Argo CD is not exposed outside the cluster by default. Use port forwarding for
local Docker Desktop access:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Keep that terminal open, then open:

```text
https://localhost:8080
```

The browser may warn about a self-signed certificate. That is expected for this
local install.

## 4. Log In

Get the initial admin password:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d
```

Log in with the CLI:

```bash
argocd login localhost:8080 --username admin --password <password> --insecure
```

After logging in, change the admin password:

```bash
argocd account update-password
```

## 5. Create The Dev Application

Create an Argo CD Application that watches the `dev` branch and applies the dev
Kustomize overlay:

```bash
argocd app create url-shortener-dev \
  --repo https://github.com/samperay/url_shortner.git \
  --revision dev \
  --path k8s/environments/dev \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace url-shortener-dev \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

Sync it:

```bash
argocd app sync url-shortener-dev
argocd app wait url-shortener-dev --health --sync
```

Verify the app:

```bash
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
curl http://localhost:30080/health
```

Expected response:

```json
{"status":"ok"}
```

## 6. Create The Stage Application

Create an Argo CD Application that watches the `stage` branch and applies the
stage Kustomize overlay:

```bash
argocd app create url-shortener-stage \
  --repo https://github.com/samperay/url_shortner.git \
  --revision stage \
  --path k8s/environments/stage \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace url-shortener-stage \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

Sync it:

```bash
argocd app sync url-shortener-stage
argocd app wait url-shortener-stage --health --sync
```

Verify the app:

```bash
kubectl port-forward svc/url-shortener 30081:80 -n url-shortener-stage
curl http://localhost:30081/health
```

Expected response:

```json
{"status":"ok"}
```

## 7. How The GitOps Flow Works

After Argo CD is installed and both Applications exist:

- A merge to `dev` triggers `.github/workflows/publish-dev-image.yml`.
- The workflow pushes `sunlnx/url-shortener:dev_<short-sha>` to Docker Hub.
- The workflow updates `k8s/environments/dev/kustomization.yaml` on `dev`.
- Argo CD sees the `dev` branch change and syncs `url-shortener-dev`.
- A merge to `stage` triggers `.github/workflows/publish-stage-image.yml`.
- The workflow pushes `sunlnx/url-shortener:stage_<short-sha>` to Docker Hub.
- The workflow updates `k8s/environments/stage/kustomization.yaml` on `stage`.
- Argo CD sees the `stage` branch change and syncs `url-shortener-stage`.

Production remains manual for this Docker Desktop setup. See
[Environment promotion flow](environment-promotion.md) for the promotion model.

## Troubleshooting

If the Argo CD UI does not open, confirm the port-forward is still running:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

If an Application cannot fetch the repository, confirm the repository is public.
For a private repository, add repository credentials in Argo CD before creating
the Applications.

If an Application is out of sync, inspect it:

```bash
argocd app get url-shortener-dev
argocd app diff url-shortener-dev
```

If a synced app is not reachable locally, use `kubectl port-forward` instead of
NodePort access. Docker Desktop on macOS may not expose NodePort traffic
reliably on `localhost`.
