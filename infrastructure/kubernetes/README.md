# Zylvex Kubernetes Manifests

Production-ready Kubernetes manifests for deploying the entire Zylvex platform. Works on any Kubernetes cluster: EKS, GKE, DigitalOcean, AKS, or self-hosted.

## Prerequisites

1. **kubectl** — Kubernetes CLI ([install guide](https://kubernetes.io/docs/tasks/tools/))
2. **Helm** — for installing cert-manager ([install guide](https://helm.sh/docs/intro/install/))
3. **NGINX Ingress Controller** — installed in your cluster
4. **cert-manager** — for automated TLS certificates via Let's Encrypt

### Install NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml
```

### Install cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true
```

### Create Let's Encrypt ClusterIssuer

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@zylvex.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

## 3-Step Deploy

### Step 1: Fill in secrets

```bash
cp secrets/secrets-template.yml secrets/secrets.yml
# Edit secrets/secrets.yml and replace all placeholder values with real base64-encoded secrets
# To encode: echo -n "your-secret-value" | base64
```

### Step 2: Deploy

```bash
cd infrastructure/kubernetes/scripts
./deploy.sh
```

### Step 3: Verify

```bash
kubectl get pods -n zylvex-production
kubectl get svc -n zylvex-production
kubectl get ingress -n zylvex-production
```

## Common Operations

### Check pod status

```bash
kubectl get pods -n zylvex-production
kubectl get pods -n zylvex-production -o wide    # includes node info
```

### View logs

```bash
# View logs for a specific service
kubectl logs -n zylvex-production -l app=auth-service -f

# View logs for all pods of a service
kubectl logs -n zylvex-production -l app=spatial-canvas-backend --all-containers

# View previous container logs (after crash)
kubectl logs -n zylvex-production -l app=auth-service --previous
```

### Rollback

```bash
# Rollback all services to previous version
cd infrastructure/kubernetes/scripts
./rollback.sh

# Rollback a specific service
./rollback.sh auth-service

# View rollout history
kubectl rollout history deployment/auth-service -n zylvex-production

# Rollback to a specific revision
kubectl rollout undo deployment/auth-service -n zylvex-production --to-revision=2
```

### Scale a service manually

```bash
kubectl scale deployment/auth-service -n zylvex-production --replicas=5
```

### Check HPA status

```bash
kubectl get hpa -n zylvex-production
```

## Architecture

```
                           ┌──────────────────┐
                           │  NGINX Ingress    │
                           │  + TLS (LE cert)  │
                           └────────┬─────────┘
                                    │
        ┌───────────┬───────────┬───┴────┬───────────┬───────────┬──────────┐
        │           │           │        │           │           │          │
   /api/auth   /api/spatial /api/mm  /api/social /api/notify    /ws        /
        │           │           │        │           │           │          │
   auth-svc    spatial-svc  mm-svc   social-svc  notif-svc  realtime   web-app
   :8001       :8000        :8002    :8003       :8005      :8004      :80
        │           │           │        │           │           │
        └───────────┴───────────┴────────┴───────────┘           │
                           │                                     │
                    ┌──────┴──────┐                      ┌───────┴──────┐
                    │  PostgreSQL │                      │    Redis     │
                    │  (5 DBs)   │                      │              │
                    └─────────────┘                      └──────────────┘
```

## Directory Structure

```
infrastructure/kubernetes/
├── namespace.yml                  # zylvex-production namespace
├── configmaps/
│   └── app-config.yml             # Shared configuration
├── secrets/
│   └── secrets-template.yml       # ⚠️ Template only — never commit real values
├── deployments/                   # Deployment for each service (2 replicas HA)
│   ├── auth-service.yml
│   ├── spatial-canvas-backend.yml
│   ├── mind-mapper-backend.yml
│   ├── social-service.yml
│   ├── notifications-service.yml
│   ├── realtime-gateway.yml
│   └── web-app.yml
├── services/                      # ClusterIP Services
│   ├── auth-service.yml
│   ├── spatial-canvas-backend.yml
│   ├── mind-mapper-backend.yml
│   ├── social-service.yml
│   ├── notifications-service.yml
│   ├── realtime-gateway.yml
│   └── web-app.yml
├── ingress/
│   └── ingress.yml                # NGINX Ingress with TLS
├── autoscaling/
│   └── hpa.yml                    # HPA: min 2 → max 10, 70% CPU target
├── postgres/
│   ├── postgres-statefulset.yml   # Single instance (use managed DB in prod)
│   ├── postgres-service.yml
│   └── postgres-pvc.yml
├── redis/
│   ├── redis-deployment.yml
│   └── redis-service.yml
├── monitoring/
│   ├── prometheus-deployment.yml
│   └── grafana-deployment.yml
├── scripts/
│   ├── deploy.sh                  # One-command deploy (correct order)
│   └── rollback.sh                # Rollback to previous version
└── README.md                      # This file
```

## Production Notes

- **Database**: The included PostgreSQL StatefulSet is for dev/staging. In production, use a managed database (AWS RDS, GCP Cloud SQL, DigitalOcean Managed Databases).
- **Secrets**: Consider using [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) or [External Secrets Operator](https://external-secrets.io/) for production secret management.
- **Container Registry**: Images are pulled from `ghcr.io/zylvex-tech/`. Ensure your cluster has access to the GitHub Container Registry.
- **Monitoring**: Prometheus and Grafana are included. For production, consider using managed monitoring (Datadog, New Relic, or cloud-native solutions).
