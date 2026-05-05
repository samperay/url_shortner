#!/usr/bin/env sh

set -eu

IMAGE_NAME="${IMAGE_NAME:-url-shortener:dev}"
NAMESPACE="${NAMESPACE:-url-shortener-stage}"
DEPLOYMENT="${DEPLOYMENT:-url-shortener}"
KUSTOMIZE_PATH="${KUSTOMIZE_PATH:-k8s/environments/stage}"
LOCAL_PORT="${LOCAL_PORT:-30081}"
SERVICE_PORT="${SERVICE_PORT:-80}"

echo "Building Docker image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .

echo "Applying Kubernetes overlay: ${KUSTOMIZE_PATH}"
kubectl apply -k "${KUSTOMIZE_PATH}"

echo "Waiting for rollout: deployment/${DEPLOYMENT} in ${NAMESPACE}"
kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"

echo "Stage deployment is ready."
echo "Run this to open local access:"
echo "kubectl port-forward svc/${DEPLOYMENT} ${LOCAL_PORT}:${SERVICE_PORT} -n ${NAMESPACE}"
echo "Then verify:"
echo "curl http://localhost:${LOCAL_PORT}/health"
