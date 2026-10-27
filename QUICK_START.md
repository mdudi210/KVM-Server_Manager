# Quick Start Guide - KVM Server Manager

This is a quick reference guide for getting the application running on your Ubuntu server.

## Prerequisites Checklist

- [ ] Ubuntu 20.04+ installed
- [ ] Docker and Docker Compose installed
- [ ] Server IP address noted
- [ ] Firewall configured (ports 80, 443)

## 5-Minute Setup

### Step 1: Install Docker (if not installed)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Logout and login again
```

### Step 2: Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Get Your Server IP

```bash
hostname -I
# Note the IP address (e.g., 192.168.1.100)
```

### Step 4: Configure Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 5: Generate SSL Certificate

```bash
cd /path/to/KVM-Server-Manager
./scripts/generate-ssl.sh kvm-server.local ./nginx/ssl
```

### Step 6: Start the Application

```bash
docker-compose up -d --build
```

### Step 7: Verify It's Running

```bash
docker-compose ps
# All containers should show "Up"
```

### Step 8: Access the Application

Open your browser and go to:
- **HTTPS:** `https://YOUR_SERVER_IP`
- Example: `https://192.168.1.100`

**First time:** Browser will warn about self-signed certificate. Click "Advanced" → "Proceed anyway"

### Step 9: Login

- Username: `admin`
- Password: `password123`

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Restart application
docker-compose restart

# Update application
docker-compose up -d --build
```

## Troubleshooting

**Can't access from network?**
1. Check firewall: `sudo ufw status`
2. Verify IP: `hostname -I`
3. Check containers: `docker-compose ps`

**SSL certificate error?**
- This is normal for self-signed certificates
- Click "Advanced" → "Proceed anyway" in browser

**Containers not starting?**
```bash
docker-compose logs
docker-compose down -v
docker-compose up -d --build
```

## Next Steps

- Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions
- Read [KUBERNETES_DEPLOYMENT.md](./KUBERNETES_DEPLOYMENT.md) for Kubernetes setup
- Change default passwords
- Set up backups
