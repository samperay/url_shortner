# Deploy URL Shortener on Docker Desktop Kubernetes

This guide deploys the FastAPI URL Shortener to the single-node Kubernetes cluster that ships with Docker Desktop.

## What You Will Run

- FastAPI app served by Uvicorn on port `8000`
- Docker image named `url-shortener:dev`
- Kubernetes `Deployment` with one replica
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

## 2. Deploy to Kubernetes

Apply the manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check the rollout:

```bash
kubectl rollout status deployment/url-shortener -n url-shortener
```

Check the resources:

```bash
kubectl get all -n url-shortener
```

## 3. Open the App

Use `kubectl port-forward` for the most reliable local access path on Docker
Desktop Kubernetes:

```bash
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener
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
kubectl run curl-test -n url-shortener --rm -i --restart=Never \
  --image=curlimages/curl -- curl -sS http://url-shortener/health
```

If the in-cluster test returns `{"status":"ok"}`, the app and Service are
working. Use `kubectl port-forward` for local browser access.

## 4. Useful Debug Commands

List Pods:

```bash
kubectl get pods -n url-shortener
```

Describe the Deployment:

```bash
kubectl describe deployment url-shortener -n url-shortener
```

Describe a Pod:

```bash
kubectl describe pod <pod-name> -n url-shortener
```

View logs:

```bash
kubectl logs deployment/url-shortener -n url-shortener
```

Open a shell inside the Pod:

```bash
kubectl exec -it deployment/url-shortener -n url-shortener -- sh
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
kubectl rollout restart deployment/url-shortener -n url-shortener
kubectl rollout status deployment/url-shortener -n url-shortener
```

If the manifest uses `imagePullPolicy: Never`, Kubernetes uses the local Docker
Desktop image. If you remove that setting, make sure the image is available from
a registry your cluster can pull from.

## 6. Clean Up

Delete the app:

```bash
kubectl delete namespace url-shortener
```

This also deletes the `emptyDir` SQLite data.

## 7. Next Production Improvements

- Replace `emptyDir` with a `PersistentVolumeClaim`.
- Use a real database such as PostgreSQL.
- Add resource requests and limits.
- Add Ingress instead of `NodePort`.
- Add CI to build and push images.
- Add tests before every image build.
