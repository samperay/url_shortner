# GitOps And Argo CD Break/Fix Learning Path

Use this guide after installing Argo CD with
[Install Argo CD on Docker Desktop Kubernetes](../deployment/argocd-install.md).
The goal is to learn GitOps by breaking the live Argo CD flow for this URL
Shortener app, reading the symptoms, and fixing the source of truth.

## Starting Point

Confirm both Argo CD Applications exist and are healthy:

```bash
argocd app get url-shortener-dev
argocd app get url-shortener-stage
```

Expected status for each app:

```text
Sync Status: Synced
Health Status: Healthy
```

Verify the Kubernetes side:

```bash
kubectl get pods -n url-shortener-dev
kubectl get pods -n url-shortener-stage
```

Verify the app endpoints with port-forwarding:

```bash
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
curl http://localhost:30080/health
```

In another terminal:

```bash
kubectl port-forward svc/url-shortener 30081:80 -n url-shortener-stage
curl http://localhost:30081/health
```

Expected response:

```json
{"status":"ok"}
```

## Learning Loop

For each exercise:

1. Break one part of the GitOps flow.
2. Observe the symptom in Argo CD and Kubernetes.
3. Explain whether the problem is Git state, cluster drift, image publishing, or
   Application configuration.
4. Fix the source of truth or the Argo CD Application.
5. Confirm Argo CD returns to `Synced` and `Healthy`.

Prefer fixing files and PRs over manually patching the cluster. Manual cluster
changes are useful for learning drift, but Git should remain the long-term
source of truth.

## Exercise 1: Manual Cluster Drift And Self-Heal

Goal: Learn how Argo CD detects and repairs drift when `self-heal` is enabled.

Break it:

```bash
kubectl scale deployment/url-shortener --replicas=2 -n url-shortener-dev
kubectl get deployment/url-shortener -n url-shortener-dev
```

Observe:

```bash
argocd app get url-shortener-dev
argocd app diff url-shortener-dev
kubectl get deployment/url-shortener -n url-shortener-dev --watch
```

Expected symptom:

```text
OutOfSync
```

Why it broke:

The live cluster was changed directly. Git still says the Deployment should use
the replica count from `k8s/environments/dev`, so Argo CD sees drift.

Fix it:

If self-heal is enabled, wait for Argo CD to restore the Git-defined state. If
you want to force the repair:

```bash
argocd app sync url-shortener-dev
argocd app wait url-shortener-dev --health --sync
```

Confirm:

```bash
argocd app get url-shortener-dev
kubectl get deployment/url-shortener -n url-shortener-dev
```

## Exercise 2: Pause Auto-Sync

Goal: Learn the difference between committed Git changes and Argo CD sync
policy.

Break it:

```bash
argocd app set url-shortener-dev --sync-policy none
```

Make a small documentation-only PR into `dev`, or wait for an existing dev image
tag update. Then inspect:

```bash
argocd app get url-shortener-dev
argocd app diff url-shortener-dev
```

Expected symptom:

```text
OutOfSync
```

Why it broke:

Argo CD can see that Git changed, but auto-sync is disabled, so it does not
apply the desired state.

Fix it:

```bash
argocd app set url-shortener-dev --sync-policy automated --auto-prune --self-heal
argocd app sync url-shortener-dev
argocd app wait url-shortener-dev --health --sync
```

## Exercise 3: Wrong Application Path

Goal: Learn how an Application points to a Git path.

Break it:

```bash
argocd app set url-shortener-stage --path k8s/environments/missing
```

Observe:

```bash
argocd app get url-shortener-stage
argocd app events url-shortener-stage
```

Expected symptom:

```text
ComparisonError
```

Why it broke:

The Argo CD Application now points at a path that does not exist in the
repository, so Argo CD cannot generate manifests.

Fix it:

```bash
argocd app set url-shortener-stage --path k8s/environments/stage
argocd app sync url-shortener-stage
argocd app wait url-shortener-stage --health --sync
```

## Exercise 4: Wrong Branch Revision

Goal: Learn how branch selection controls the desired state.

Break it:

```bash
argocd app set url-shortener-stage --revision dev
```

Observe:

```bash
argocd app get url-shortener-stage
argocd app diff url-shortener-stage
```

Expected symptom:

The stage Application starts comparing the cluster against the `dev` branch
instead of the `stage` branch.

Why it broke:

GitOps depends on the Application watching the correct revision. This repository
expects:

```text
url-shortener-dev   -> dev
url-shortener-stage -> stage
```

Fix it:

```bash
argocd app set url-shortener-stage --revision stage
argocd app sync url-shortener-stage
argocd app wait url-shortener-stage --health --sync
```

## Exercise 5: Bad Image Tag In Git

Goal: Learn the difference between a GitOps sync problem and an image pull
problem.

Break it on a short-lived feature branch by editing
`k8s/environments/dev/kustomization.yaml`:

```yaml
images:
  - name: url-shortener
    newName: sunlnx/url-shortener
    newTag: dev_missing
```

Promote that change to `dev` only if you intentionally want to see the failure
in Argo CD.

Observe:

```bash
argocd app get url-shortener-dev
kubectl get pods -n url-shortener-dev
kubectl describe pod <pod-name> -n url-shortener-dev
```

Expected symptom:

```text
ImagePullBackOff
```

Why it broke:

Argo CD successfully synced the manifests from Git, but Kubernetes cannot pull
the image tag. The sync can be `Synced` while health is degraded.

Fix it:

Revert the bad tag or let `.github/workflows/publish-dev-image.yml` write a real
`dev_<short-sha>` tag after the next merge to `dev`.

Confirm:

```bash
argocd app sync url-shortener-dev
argocd app wait url-shortener-dev --health --sync
curl http://localhost:30080/health
```

## Exercise 6: Recover From A Failed Stage Promotion

Goal: Practice reading the full GitHub Actions to Argo CD pipeline.

Break it:

1. Create a temporary branch with a harmless docs change.
2. Open and merge the PR into `dev`.
3. Confirm the dev image workflow updates the dev tag.
4. Promote `dev -> stage`.
5. Watch the stage image workflow and Argo CD stage Application.

Observe each layer:

```bash
gh run list --branch dev --limit 5
gh run list --branch stage --limit 5
argocd app get url-shortener-stage
argocd app diff url-shortener-stage
kubectl get pods -n url-shortener-stage
```

Expected healthy path:

```text
dev merge -> dev image tag commit -> dev Argo CD sync
stage promotion -> stage image tag commit -> stage Argo CD sync
```

If it fails, decide where the break happened:

- GitHub Actions failed before pushing an image.
- The workflow pushed an image but did not update Kustomize.
- Argo CD is not watching the expected branch/path.
- Kubernetes synced the manifests but the Pod is unhealthy.

Fix it by repairing the failed layer, then confirm:

```bash
argocd app wait url-shortener-stage --health --sync
curl http://localhost:30081/health
```

## Cleanup Checklist

After break/fix practice:

```bash
argocd app get url-shortener-dev
argocd app get url-shortener-stage
kubectl get pods -n url-shortener-dev
kubectl get pods -n url-shortener-stage
```

Both Applications should be `Synced` and `Healthy`, and both namespaces should
have a running `url-shortener` Pod.
