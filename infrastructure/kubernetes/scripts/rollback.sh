#!/usr/bin/env bash
# ============================================================================
# Zylvex Kubernetes Rollback Script
# ============================================================================
# Rolls back deployments to the previous revision.
# Usage:
#   ./rollback.sh              — rollback ALL services
#   ./rollback.sh auth-service — rollback a specific service
# ============================================================================
set -euo pipefail

NAMESPACE="zylvex-production"

ALL_DEPLOYMENTS=(
    "auth-service"
    "spatial-canvas-backend"
    "mind-mapper-backend"
    "social-service"
    "notifications-service"
    "realtime-gateway"
    "web-app"
)

rollback_deployment() {
    local deploy="$1"
    echo "🔄 Rolling back $deploy..."
    kubectl rollout undo deployment/"$deploy" -n "$NAMESPACE"
    kubectl rollout status deployment/"$deploy" -n "$NAMESPACE" --timeout=120s && \
        echo "  ✅ $deploy rolled back successfully." || \
        echo "  ⚠️  $deploy rollback may not have completed. Check status manually."
}

echo "============================================"
echo "  Zylvex Kubernetes Rollback"
echo "============================================"
echo ""

if [ $# -eq 0 ]; then
    echo "Rolling back ALL application services..."
    echo ""
    read -r -p "Are you sure you want to rollback all services? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "❌ Aborting rollback."
        exit 1
    fi
    echo ""
    for deploy in "${ALL_DEPLOYMENTS[@]}"; do
        rollback_deployment "$deploy"
    done
else
    rollback_deployment "$1"
fi

echo ""
echo "============================================"
echo "  Rollback complete."
echo "============================================"
echo ""
echo "Check pod status:  kubectl get pods -n $NAMESPACE"
echo "Check rollout:     kubectl rollout history deployment/<name> -n $NAMESPACE"
echo ""
