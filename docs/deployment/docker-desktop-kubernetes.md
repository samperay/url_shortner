# Deploy URL Shortener on Docker Desktop Kubernetes

This guide deploys the FastAPI URL Shortener to the single-node Kubernetes cluster that ships with Docker Desktop.

## What You Will Run

- FastAPI app served by Uvicorn on port `8000`
- Docker image named `url-shortener:dev`
- Kubernetes `Deployment` with one replica per environment
- Kubernetes `Service` exposed inside the cluster, with local access through
  `kubectl port-forward`
- SQLite database stored in an `emptyDir` volume at `/data/url_shortener.db`

`emptyDir` is good for learning because it is simple, but the data disappears when the Pod is deleted. Later, replace it with a `PersistentVolumeClaim`.

## Prerequisites

1. Install Docker Desktop.
2. Enable Kubernetes:
   - Docker Desktop -> Settings -> Kubernetes -> Enable Kubernetes
3. Confirm your context points to Docker Desktop:

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

## 1. Build the Docker Image

Run this from the project root:

```bash
docker build -t url-shortener:dev .
```

Smoke test the image locally:

```bash
docker run --rm -p 8000:8000 url-shortener:dev
```

Open:

```text
http://localhost:8000
```

Stop the container with `Ctrl+C`.

For normal non-container local development, use:

```bash
./scripts/start.sh
```

## 2. Deploy to Kubernetes

Apply one environment overlay. For day-to-day development, start with `dev`:

```bash
./scripts/deploy-dev.sh
```

The script builds the local Docker image, applies the dev overlay, and waits for
the rollout. You can also run the commands manually:

```bash
docker build -t url-shortener:dev .
kubectl apply -k k8s/environments/dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
```

Check the resources:

```bash
kubectl get all -n url-shortener-dev
```

## 3. Open the App

Use `kubectl port-forward` for the most reliable local access path on Docker
Desktop Kubernetes:

```bash
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
```

Keep that terminal open. In another terminal, verify the app:

```bash
curl http://localhost:30080/health
```

Expected response:

```json
{"status":"ok"}
```

Open the UI:

```text
http://localhost:30080
```

Try shortening a URL, then click the generated short URL.

### Optional: NodePort Access

The Service is configured as `NodePort` on port `30080`, but Docker Desktop does
not always expose NodePort traffic on macOS localhost. If this fails:

```bash
curl http://localhost:30080/health
```

but the Pod is `Running` and `Ready`, test the Service from inside the cluster:

```bash
kubectl run curl-test -n url-shortener-dev --rm -i --restart=Never \
  --image=curlimages/curl -- curl -sS http://url-shortener/health
```

If the in-cluster test returns `{"status":"ok"}`, the app and Service are
working. Use `kubectl port-forward` for local browser access.

## 4. Useful Debug Commands

List Pods:

```bash
kubectl get pods -n url-shortener-dev
```

Describe the Deployment:

```bash
kubectl describe deployment url-shortener -n url-shortener-dev
```

Describe a Pod:

```bash
kubectl describe pod <pod-name> -n url-shortener-dev
```

View logs:

```bash
kubectl logs deployment/url-shortener -n url-shortener-dev
```

Open a shell inside the Pod:

```bash
kubectl exec -it deployment/url-shortener -n url-shortener-dev -- sh
```

Check the health endpoint from your machine:

```bash
curl http://localhost:30080/health
```

If this only works while `kubectl port-forward` is running, the issue is local
NodePort exposure, not the application.

## 5. Update the App

After changing Python or template files:

```bash
docker build -t url-shortener:dev .
kubectl rollout restart deployment/url-shortener -n url-shortener-dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
```

The local deployment scripts build `url-shortener:dev`, apply the selected
overlay, and then override the Deployment to use that Docker Desktop image.
Argo CD deployments use the image tag recorded in the environment overlay.

## 6. Clean Up

Delete the app:

```bash
kubectl delete namespace url-shortener-dev
```

This also deletes the `emptyDir` SQLite data.

For stage and production environment commands, see
[Environment promotion flow](environment-promotion.md).

For GitOps deployment through Argo CD, see
[Install Argo CD on Docker Desktop Kubernetes](argocd-install.md).

## 7. Next Production Improvements

- Replace `emptyDir` with a `PersistentVolumeClaim`.
- Use a real database such as PostgreSQL.
- Add resource requests and limits.
- Add Ingress instead of `NodePort`.
- Add CI to build and push images.
- Add tests before every image build.
