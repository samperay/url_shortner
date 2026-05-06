# Kubernetes Break/Fix Learning Path

Use this file as a hands-on tutorial for learning Kubernetes by breaking this real URL Shortener app and fixing it again.

If you want to practice GitOps behavior after the Kubernetes basics, continue
with [GitOps and Argo CD break/fix learning path](gitops-argocd-break-fix.md).
That guide uses Argo CD sync, drift, self-heal, branch, path, and image-tag
failures to teach the dev/stage GitOps flow.

Start from a healthy deployment:

```bash
./scripts/deploy-dev.sh
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
```

Keep the port-forward running in that terminal. In another terminal:

```bash
curl http://localhost:30080/health
```

Expected response:

```json
{"status":"ok"}
```

## Learning Loop

For each exercise:

1. Break one thing.
2. Observe symptoms with `kubectl get`, `kubectl describe`, `kubectl logs`, and `curl`.
3. Explain what Kubernetes is telling you.
4. Fix the manifest or rebuild the image.
5. Confirm the app works again.

## Exercise 1: Wrong Image Name

Goal: Learn `ImagePullBackOff`.

Break it:

```bash
kubectl set image deployment/url-shortener url-shortener=url-shortener:missing -n url-shortener-dev
kubectl get pods -n url-shortener-dev
```

Observe:

```bash
kubectl describe pod <pod-name> -n url-shortener-dev
```

Expected symptom:

```text
ImagePullBackOff
```

Why it broke:

Kubernetes cannot find or pull the image named `url-shortener:missing`.

Fix it:

```bash
kubectl set image deployment/url-shortener url-shortener=url-shortener:dev -n url-shortener-dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
curl http://localhost:30080/health
```

## Exercise 2: Wrong Container Port

Goal: Learn the difference between `containerPort`, `targetPort`, and app runtime port.

Break it by editing `k8s/base/service.yaml`:

```yaml
targetPort: 9999
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
curl http://localhost:30080/health
```

Expected symptom:

```text
Connection refused
```

Observe:

```bash
kubectl get endpoints url-shortener -n url-shortener-dev
kubectl describe service url-shortener -n url-shortener-dev
```

Why it broke:

The FastAPI app listens on port `8000` inside the container. The Service sent traffic to port `9999`, where nothing is listening.

Fix it:

```yaml
targetPort: 8000
```

Apply and test:

```bash
kubectl apply -k k8s/environments/dev
curl http://localhost:30080/health
```

## Exercise 3: Selector Mismatch

Goal: Learn how Services find Pods.

Break it by editing `k8s/base/service.yaml`:

```yaml
selector:
  app: wrong-app
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl get endpoints url-shortener -n url-shortener-dev
```

Expected symptom:

```text
ENDPOINTS   <none>
```

Why it broke:

The Service only routes to Pods whose labels match its selector. The Pods are labeled `app: url-shortener`, but the Service searched for `app: wrong-app`.

Fix it:

```yaml
selector:
  app: url-shortener
```

Apply and test:

```bash
kubectl apply -k k8s/environments/dev
curl http://localhost:30080/health
```

## Exercise 4: Readiness Probe Failure

Goal: Learn why a running Pod may still receive no traffic.

Break it by editing `k8s/base/deployment.yaml`:

```yaml
readinessProbe:
  httpGet:
    path: /not-health
    port: 8000
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl get pods -n url-shortener-dev
kubectl describe pod <pod-name> -n url-shortener-dev
```

Expected symptom:

```text
READY   0/1
Readiness probe failed: HTTP probe failed with statuscode: 404
```

Why it broke:

The app has `/health`, but the readiness probe checks `/not-health`. Kubernetes keeps the Pod out of Service endpoints because it is not ready.

Fix it:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
```

Apply and test:

```bash
kubectl apply -k k8s/environments/dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
curl http://localhost:30080/health
```

## Exercise 5: Liveness Probe Restart Loop

Goal: Learn restart behavior caused by health checks.

Break it by editing `k8s/base/deployment.yaml`:

```yaml
livenessProbe:
  httpGet:
    path: /not-health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl get pods -n url-shortener-dev --watch
```

Expected symptom:

The Pod repeatedly restarts.

Observe:

```bash
kubectl describe pod <pod-name> -n url-shortener-dev
kubectl logs <pod-name> -n url-shortener-dev --previous
```

Why it broke:

The liveness probe tells Kubernetes when the container should be restarted. A bad path makes Kubernetes think the healthy app is dead.

Fix it:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20
```

Apply and test:

```bash
kubectl apply -k k8s/environments/dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
```

## Exercise 6: Bad Database Path

Goal: Learn environment variables, volume mounts, and app startup failures.

Break it by editing `k8s/base/deployment.yaml`:

```yaml
env:
  - name: DATABASE_URL
    value: sqlite:////missing-folder/url_shortener.db
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl get pods -n url-shortener-dev
kubectl logs deployment/url-shortener -n url-shortener-dev
```

Expected symptom:

The app may fail when it tries to create or write to the SQLite database.

Why it broke:

The app reads `DATABASE_URL` from the container environment. The configured path points to a folder that is not mounted and may not exist.

Fix it:

```yaml
env:
  - name: DATABASE_URL
    value: sqlite:////data/url_shortener.db
volumeMounts:
  - name: sqlite-data
    mountPath: /data
```

Apply and test:

```bash
kubectl apply -k k8s/environments/dev
curl http://localhost:30080/health
```

## Exercise 7: Delete the Pod

Goal: Learn how Deployments self-heal.

Break it:

```bash
kubectl delete pod <pod-name> -n url-shortener-dev
kubectl get pods -n url-shortener-dev --watch
```

Expected symptom:

Kubernetes creates a replacement Pod.

Why it recovered:

The Deployment owns a ReplicaSet, and the ReplicaSet keeps the desired number of Pods running.

Confirm:

```bash
curl http://localhost:30080/health
```

Learning note:

Because this project currently uses `emptyDir`, deleting the Pod also deletes the SQLite data. This is why production apps should use a PersistentVolume or external database.

## Exercise 8: Scale the App

Goal: Learn replicas and the SQLite limitation.

Scale:

```bash
kubectl scale deployment/url-shortener --replicas=3 -n url-shortener-dev
kubectl get pods -n url-shortener-dev
```

Expected result:

Three Pods run.

Important project lesson:

Each Pod gets its own `emptyDir` SQLite database. One request may create a short URL in Pod A, while a later redirect may land on Pod B and return `404`.

Fix options:

- For learning: scale back to one replica.
- For a real project: move data to PostgreSQL and let every Pod use the same database.

Scale back:

```bash
kubectl scale deployment/url-shortener --replicas=1 -n url-shortener-dev
```

## Exercise 9: Resource Pressure

Goal: Learn requests, limits, and scheduling.

Break it by adding unrealistic resource requests to the container in `k8s/base/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: "8"
    memory: "16Gi"
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl get pods -n url-shortener-dev
kubectl describe pod <pod-name> -n url-shortener-dev
```

Expected symptom:

The Pod may stay `Pending`.

Why it broke:

Docker Desktop Kubernetes has limited CPU and memory. The scheduler cannot place a Pod that asks for more resources than the node can provide.

Fix it with realistic values:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

Apply:

```bash
kubectl apply -k k8s/environments/dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
```

## Exercise 10: Roll Back a Bad Release

Goal: Learn rollout history and undo.

Create a bad release:

```bash
kubectl set image deployment/url-shortener url-shortener=url-shortener:bad -n url-shortener-dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
```

Observe:

```bash
kubectl rollout history deployment/url-shortener -n url-shortener-dev
kubectl get pods -n url-shortener-dev
```

Fix by rollback:

```bash
kubectl rollout undo deployment/url-shortener -n url-shortener-dev
kubectl rollout status deployment/url-shortener -n url-shortener-dev
curl http://localhost:30080/health
```

## Daily Debug Checklist

Use this order when the app is broken:

```bash
kubectl get pods -n url-shortener-dev
kubectl describe pod <pod-name> -n url-shortener-dev
kubectl logs <pod-name> -n url-shortener-dev
kubectl get service,endpoints -n url-shortener-dev
kubectl describe service url-shortener -n url-shortener-dev
curl -v http://localhost:30080/health
```

Read the state first:

- `Pending`: scheduler or resource issue.
- `ImagePullBackOff` / `ErrImageNeverPull`: image issue.
- `CrashLoopBackOff`: process starts and crashes.
- `Running` with `READY 0/1`: readiness probe issue.
- Service has no endpoints: selector or readiness issue.
- Health works but redirect fails: application or database issue.

## Suggested Learning Order

1. Deploy the healthy app.
2. Break image name.
3. Break Service port.
4. Break Service selector.
5. Break readiness probe.
6. Break liveness probe.
7. Break database path.
8. Delete Pods and watch self-healing.
9. Scale replicas and discover the SQLite problem.
10. Practice rollback.

After you finish these, convert the SQLite database to PostgreSQL and repeat the same break/fix loop with a database `Service`, `Secret`, and `PersistentVolumeClaim`.
