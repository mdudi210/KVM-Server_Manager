# KVM Server Manager - Kubernetes Deployment Guide

This guide covers deploying the KVM Server Manager application on a Kubernetes cluster for production use with scaling capabilities.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Building Docker Images](#building-docker-images)
3. [Preparing Kubernetes Cluster](#preparing-kubernetes-cluster)
4. [Deploying to Kubernetes](#deploying-to-kubernetes)
5. [Scaling the Application](#scaling-the-application)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- `kubectl` - Kubernetes command-line tool
- `docker` - For building images
- Access to a Kubernetes cluster (minikube, k3s, or cloud provider)
- `kustomize` (optional, included with kubectl 1.14+)

### Install kubectl

```bash
# For Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

### Kubernetes Cluster Options

**Option 1: Minikube (Local Development)**
```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start cluster
minikube start --cpus=4 --memory=4096
```

**Option 2: k3s (Lightweight Production)**
```bash
# Install k3s
curl -sfL https://get.k3s.io | sh -

# Verify installation
sudo k3s kubectl get nodes
```

**Option 3: Cloud Provider (Production)**
- AWS EKS
- Google GKE
- Azure AKS
- DigitalOcean Kubernetes

## Building Docker Images

### 1. Build Images Locally

```bash
# Navigate to project root
cd /path/to/KVM-Server-Manager

# Build backend image
docker build -f backend/Dockerfile -t kvm-backend:latest .

# Build frontend image
docker build -f frontend/Dockerfile -t kvm-frontend:latest .

# Build nginx image
docker build -f nginx/Dockerfile -t kvm-nginx:latest .
```

### 2. Tag and Push to Registry (Optional)

If using a container registry:

```bash
# Tag images
docker tag kvm-backend:latest your-registry.com/kvm-backend:latest
docker tag kvm-frontend:latest your-registry.com/kvm-frontend:latest
docker tag kvm-nginx:latest your-registry.com/kvm-nginx:latest

# Push to registry
docker push your-registry.com/kvm-backend:latest
docker push your-registry.com/kvm-frontend:latest
docker push your-registry.com/kvm-nginx:latest
```

### 3. For Minikube (Load Images Directly)

```bash
# Load images into minikube
minikube image load kvm-backend:latest
minikube image load kvm-frontend:latest
minikube image load kvm-nginx:latest
```

## Preparing Kubernetes Cluster

### 1. Verify Cluster Access

```bash
# Check cluster connection
kubectl cluster-info

# List nodes
kubectl get nodes

# Check if you have admin access
kubectl auth can-i '*' '*' --all-namespaces
```

### 2. Set Up Storage Class (if needed)

For MySQL persistent volume, ensure a storage class exists:

```bash
# Check existing storage classes
kubectl get storageclass

# If none exist, create one (example for local storage)
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
EOF
```

### 3. Generate SSL Certificates

```bash
# Generate SSL certificates
./scripts/generate-ssl.sh kvm-server.local ./ssl

# Create Kubernetes secret for SSL
kubectl create secret generic nginx-ssl-secret \
  --from-file=cert.pem=./ssl/cert.pem \
  --from-file=key.pem=./ssl/key.pem \
  --namespace=kvm-server \
  --dry-run=client -o yaml > k8s/nginx-ssl-secret.yaml

# Or create directly
kubectl create secret generic nginx-ssl-secret \
  --from-file=cert.pem=./ssl/cert.pem \
  --from-file=key.pem=./ssl/key.pem \
  -n kvm-server
```

## Deploying to Kubernetes

### Method 1: Using kubectl (Recommended)

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mysql-secret.yaml
kubectl apply -f k8s/mysql-configmap.yaml
kubectl apply -f k8s/mysql-pvc.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### Method 2: Using kustomize

```bash
# Apply using kustomize
kubectl apply -k k8s/
```

### Method 3: One-by-One Deployment (for debugging)

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Deploy MySQL
kubectl apply -f k8s/mysql-secret.yaml
kubectl apply -f k8s/mysql-configmap.yaml
kubectl apply -f k8s/mysql-pvc.yaml
kubectl apply -f k8s/mysql-deployment.yaml

# 3. Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql -n kvm-server --timeout=300s

# 4. Deploy Backend
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml

# 5. Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml

# 6. Deploy Nginx
kubectl apply -f k8s/nginx-deployment.yaml

# 7. Deploy Ingress (if using)
kubectl apply -f k8s/ingress.yaml
```

### Verify Deployment

```bash
# Check all pods
kubectl get pods -n kvm-server

# Check services
kubectl get svc -n kvm-server

# Check deployments
kubectl get deployments -n kvm-server

# View detailed pod status
kubectl describe pod <pod-name> -n kvm-server

# View logs
kubectl logs -f deployment/backend -n kvm-server
kubectl logs -f deployment/frontend -n kvm-server
kubectl logs -f deployment/mysql -n kvm-server
kubectl logs -f deployment/nginx -n kvm-server
```

## Accessing the Application

### Get Service Information

```bash
# Get nginx service (LoadBalancer or NodePort)
kubectl get svc nginx -n kvm-server

# For LoadBalancer, get external IP
kubectl get svc nginx -n kvm-server -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# For NodePort, get node port
kubectl get svc nginx -n kvm-server -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}'
```

### Access Methods

**1. Using LoadBalancer (Cloud Providers)**
- Access via external IP provided by cloud provider
- Example: `https://EXTERNAL_IP`

**2. Using NodePort (Bare Metal)**
```bash
# Get node IP
kubectl get nodes -o wide

# Access via: https://NODE_IP:NODE_PORT
```

**3. Using Port Forwarding (Testing)**
```bash
# Forward nginx service
kubectl port-forward svc/nginx 443:443 -n kvm-server

# Access via: https://localhost
```

**4. Using Ingress**
- Configure DNS to point to ingress controller IP
- Access via: `https://your-domain.com`

## Scaling the Application

### Manual Scaling

```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n kvm-server

# Scale frontend to 3 replicas
kubectl scale deployment frontend --replicas=3 -n kvm-server

# Scale nginx to 2 replicas
kubectl scale deployment nginx --replicas=2 -n kvm-server

# Check scaling status
kubectl get deployments -n kvm-server
```

### Horizontal Pod Autoscaling (HPA)

Create HPA configuration:

```bash
# Install metrics-server (if not installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create HPA for backend
kubectl autoscale deployment backend \
  --min=2 \
  --max=10 \
  --cpu-percent=70 \
  -n kvm-server

# Create HPA for frontend
kubectl autoscale deployment frontend \
  --min=2 \
  --max=10 \
  --cpu-percent=70 \
  -n kvm-server

# Check HPA status
kubectl get hpa -n kvm-server
```

### Update Deployment Replicas

Edit deployment files:

```yaml
# In backend-deployment.yaml
spec:
  replicas: 5  # Change this number
```

Then apply:
```bash
kubectl apply -f k8s/backend-deployment.yaml
```

## SSL/TLS Configuration

### Option 1: Using cert-manager (Recommended)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Option 2: Manual SSL Secret

```bash
# Create secret from existing certificates
kubectl create secret tls kvm-server-tls \
  --cert=./ssl/cert.pem \
  --key=./ssl/key.pem \
  -n kvm-server
```

### Option 3: Self-Signed Certificate

```bash
# Generate self-signed certificate
./scripts/generate-ssl.sh kvm-server.local ./ssl

# Create secret
kubectl create secret tls kvm-server-tls \
  --cert=./ssl/cert.pem \
  --key=./ssl/key.pem \
  -n kvm-server
```

## Monitoring and Maintenance

### View Resource Usage

```bash
# Pod resource usage
kubectl top pods -n kvm-server

# Node resource usage
kubectl top nodes

# Detailed resource usage
kubectl describe nodes
```

### Database Backup

```bash
# Create backup job
kubectl run mysql-backup --image=mysql:8.0 --restart=Never \
  -n kvm-server --rm -it -- \
  mysqldump -h mysql -u kvm_user -pkvm_password kvm_db > backup.sql

# Or use a CronJob for automated backups
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mysql-backup
  namespace: kvm-server
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: mysql:8.0
            command:
            - /bin/sh
            - -c
            - mysqldump -h mysql -u kvm_user -pkvm_password kvm_db > /backup/backup-$(date +%Y%m%d).sql
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

### Update Application

```bash
# Update image
docker build -t kvm-backend:v2.0 -f backend/Dockerfile .
kubectl set image deployment/backend backend=kvm-backend:v2.0 -n kvm-server

# Rollout status
kubectl rollout status deployment/backend -n kvm-server

# Rollback if needed
kubectl rollout undo deployment/backend -n kvm-server
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n kvm-server

# Describe pod for details
kubectl describe pod <pod-name> -n kvm-server

# Check logs
kubectl logs <pod-name> -n kvm-server

# Check events
kubectl get events -n kvm-server --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check MySQL pod
kubectl get pods -l app=mysql -n kvm-server

# Check MySQL logs
kubectl logs -l app=mysql -n kvm-server

# Test MySQL connection
kubectl run mysql-client --image=mysql:8.0 --restart=Never \
  -n kvm-server --rm -it -- \
  mysql -h mysql -u kvm_user -pkvm_password kvm_db
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n kvm-server

# Check service details
kubectl describe svc nginx -n kvm-server

# Test service from within cluster
kubectl run curl-test --image=curlimages/curl --restart=Never \
  -n kvm-server --rm -it -- \
  curl http://nginx:80/health
```

### Persistent Volume Issues

```bash
# Check PVC status
kubectl get pvc -n kvm-server

# Describe PVC
kubectl describe pvc mysql-pvc -n kvm-server

# Check PV
kubectl get pv
```

### Image Pull Errors

```bash
# Check image pull secrets
kubectl get secrets -n kvm-server

# For private registry, create secret
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  -n kvm-server

# Add to deployment
# Add imagePullSecrets section to deployment YAML
```

## Production Recommendations

1. **Resource Limits:** Set appropriate CPU and memory limits
2. **Health Checks:** Ensure liveness and readiness probes are configured
3. **Backup Strategy:** Implement automated database backups
4. **Monitoring:** Set up Prometheus and Grafana
5. **Logging:** Configure centralized logging (ELK stack or similar)
6. **Security:** Use RBAC, network policies, and secrets management
7. **High Availability:** Deploy across multiple nodes/zones
8. **Disaster Recovery:** Plan for cluster failures and data recovery

## Cleanup

```bash
# Delete all resources
kubectl delete namespace kvm-server

# Or delete individually
kubectl delete -f k8s/
```

## Next Steps

- Set up monitoring with Prometheus and Grafana
- Configure centralized logging
- Implement CI/CD pipeline
- Set up automated backups
- Configure network policies for security
