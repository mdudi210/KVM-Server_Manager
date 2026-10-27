# KVM Server Manager - Complete Deployment Summary

## Overview

This application can be deployed in two ways:
1. **Docker Compose** - For single server deployment with SSL
2. **Kubernetes** - For scalable, production deployment

## Quick Links

- **[QUICK_START.md](./QUICK_START.md)** - Get running in 5 minutes
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Detailed Docker deployment guide
- **[KUBERNETES_DEPLOYMENT.md](./KUBERNETES_DEPLOYMENT.md)** - Kubernetes deployment guide

## Architecture

### Docker Compose Setup
```
Internet/Network
    ↓
Nginx (Port 80/443) - SSL Termination
    ↓
Frontend (Vue.js) + Backend (FastAPI)
    ↓
MySQL Database
```

### Kubernetes Setup
```
Ingress Controller
    ↓
Nginx Service (LoadBalancer/NodePort)
    ↓
Frontend Pods (Scalable) + Backend Pods (Scalable)
    ↓
MySQL Pod (Stateful)
```

## Key Features

✅ **SSL/HTTPS Support** - Self-signed or Let's Encrypt certificates  
✅ **Network Accessible** - Access from any machine in your network  
✅ **Scalable** - Kubernetes supports horizontal scaling  
✅ **Production Ready** - Health checks, persistent storage, backups  
✅ **Easy Deployment** - Docker Compose for quick setup  

## Default Credentials

⚠️ **Change these in production!**

- **Admin:** `admin` / `password123`
- **Test User:** `testuser` / `password123`

## Network Access

After deployment, access the application using your server's IP address:

- **HTTPS:** `https://YOUR_SERVER_IP`
- **HTTP:** `http://YOUR_SERVER_IP` (redirects to HTTPS)

## Important Notes

### Frontend API Configuration

The frontend currently uses hardcoded API URLs (`http://127.0.0.1:8000`). When accessing through nginx:

1. **For development:** The frontend code needs to be updated to use relative URLs or environment variables
2. **For production:** Consider building the frontend with the correct API URL:
   ```bash
   # Set API URL before building
   export VUE_APP_API_URL=https://YOUR_SERVER_IP/api
   npm run build
   ```

### SSL Certificates

- **Self-signed:** Quick setup, browser warnings expected
- **Let's Encrypt:** Best for production with domain name
- **Internal CA:** Best for company networks

### Database

- MySQL data is persisted in Docker volumes
- Backups should be configured for production
- Default database: `kvm_db`

## File Structure

```
KVM-Server-Manager/
├── backend/              # FastAPI backend
├── frontend/             # Vue.js frontend
├── nginx/                # Nginx reverse proxy config
├── k8s/                  # Kubernetes manifests
├── scripts/              # Utility scripts
├── docker-compose.yml    # Docker Compose configuration
├── DEPLOYMENT_GUIDE.md   # Docker deployment guide
├── KUBERNETES_DEPLOYMENT.md  # Kubernetes guide
└── QUICK_START.md        # Quick start guide
```

## Support

For issues or questions:
1. Check the troubleshooting sections in the guides
2. Review container logs: `docker-compose logs`
3. Verify network connectivity and firewall settings
