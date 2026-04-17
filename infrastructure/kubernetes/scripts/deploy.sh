#!/usr/bin/env bash
# ============================================================================
# Zylvex Kubernetes Deployment Script
# ============================================================================
# Applies all Kubernetes manifests in the correct order.
# Usage: ./deploy.sh
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
NAMESPACE="zylvex-production"

echo "============================================"
echo "  Zylvex Kubernetes Deployment"
echo "============================================"
echo ""

# Step 1: Create namespace
echo "▶ [1/10] Creating namespace..."
kubectl apply -f "$K8S_DIR/namespace.yml"
echo ""

# Step 2: Apply ConfigMaps
echo "▶ [2/10] Applying ConfigMaps..."
kubectl apply -f "$K8S_DIR/configmaps/"
echo ""

# Step 3: Apply Secrets (WARNING)
echo "============================================"
echo "⚠️  WARNING: Ensure you have filled in real"
echo "   secret values in secrets/ before applying!"
echo "   The template contains placeholder values."
echo "============================================"
echo ""
read -r -p "Have you updated secrets with real values? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "❌ Aborting. Please fill in secrets first."
    echo "   See: infrastructure/kubernetes/secrets/secrets-template.yml"
    exit 1
fi
echo "▶ [3/10] Applying Secrets..."
kubectl apply -f "$K8S_DIR/secrets/"
echo ""

# Step 4: Deploy PostgreSQL
echo "▶ [4/10] Deploying PostgreSQL..."
kubectl apply -f "$K8S_DIR/postgres/"
echo ""

# Step 5: Deploy Redis
echo "▶ [5/10] Deploying Redis..."
kubectl apply -f "$K8S_DIR/redis/"
echo ""

# Step 6: Wait for PostgreSQL to be ready
echo "▶ [6/10] Waiting for PostgreSQL to be ready..."
kubectl rollout status statefulset/postgres -n "$NAMESPACE" --timeout=120s
echo "✅ PostgreSQL is ready."
echo ""

# Step 7: Deploy application services
echo "▶ [7/10] Deploying application services..."
kubectl apply -f "$K8S_DIR/deployments/"
echo ""

# Step 8: Apply Services
echo "▶ [8/10] Applying Services..."
kubectl apply -f "$K8S_DIR/services/"
echo ""

# Step 9: Apply Ingress
echo "▶ [9/10] Applying Ingress..."
kubectl apply -f "$K8S_DIR/ingress/"
echo ""

# Step 10: Apply Autoscaling and Monitoring
echo "▶ [10/10] Applying Autoscaling and Monitoring..."
kubectl apply -f "$K8S_DIR/autoscaling/"
kubectl apply -f "$K8S_DIR/monitoring/"
echo ""

# Wait for all deployments to be ready
echo "============================================"
echo "  Waiting for all deployments to be ready..."
echo "============================================"

DEPLOYMENTS=(
    "auth-service"
    "spatial-canvas-backend"
    "mind-mapper-backend"
    "social-service"
    "notifications-service"
    "realtime-gateway"
    "web-app"
    "redis"
    "prometheus"
    "grafana"
)

for deploy in "${DEPLOYMENTS[@]}"; do
    echo "  ⏳ Waiting for $deploy..."
    kubectl rollout status deployment/"$deploy" -n "$NAMESPACE" --timeout=120s || {
        echo "  ⚠️  $deploy did not become ready in time. Check logs:"
        echo "     kubectl logs -n $NAMESPACE -l app=$deploy --tail=50"
    }
done

echo ""
echo "============================================"
echo "  ✅ Zylvex deployment complete!"
echo "============================================"
echo ""
echo "Check pod status:  kubectl get pods -n $NAMESPACE"
echo "Check services:    kubectl get svc -n $NAMESPACE"
echo "Check ingress:     kubectl get ingress -n $NAMESPACE"
echo "View logs:         kubectl logs -n $NAMESPACE -l app=<service-name> -f"
echo ""
