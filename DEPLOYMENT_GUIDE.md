# KVM Server Manager - Nginx-First Deployment Guide

This guide deploys the app behind nginx as the single public entrypoint.
Backend and MySQL stay private inside the Docker network.

## Architecture

- Public: `nginx` on ports `80` (redirect/health) and `443` (HTTPS)
- Private internal services: `frontend` (`8080` internal), `backend` (`8000` internal), `mysql` (`3306` internal)
- Browser auth: HTTP-only cookie set by backend, sent via same-origin requests through nginx

## Prerequisites

- Ubuntu 20.04+
- Docker + Docker Compose
- At least 4GB RAM and 20GB free disk

## 1) Firewall

Open nginx ports:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 2) Configure Environment

Create/update your `.env` file before startup:

```env
# Database
DB_USER=kvm_user
DB_PASSWORD=change-me
DB_DATABASE=kvm_db
MYSQL_ROOT_PASSWORD=change-me-root

# JWT / auth
AUTHJWT_SECRET_KEY=change-this-to-a-long-random-secret
RETURN_TOKEN_IN_BODY=false

# Cookie settings
# For HTTPS-only production traffic
AUTHJWT_COOKIE_SECURE=true
AUTHJWT_COOKIE_SAMESITE=lax
AUTHJWT_COOKIE_CSRF_PROTECT=false

# CORS - explicit origins only (no *)
ALLOWED_ORIGINS=https://localhost,https://127.0.0.1,http://localhost,http://127.0.0.1
```

Keep `ALLOWED_ORIGINS` explicit and minimal.

## 3) Provision TLS Certificates for nginx

Place cert files at:

- `nginx/ssl/cert.pem`
- `nginx/ssl/key.pem`

Quick local certificate:

```bash
./scripts/generate-ssl.sh localhost ./nginx/ssl
```

## 4) Start the Stack

```bash
docker compose up -d --build
docker compose ps
```

## 5) Validate Deployment

```bash
# nginx health
curl -i http://localhost/health

# HTTPS app endpoint (use -k for self-signed local cert)
curl -k -i https://localhost/

# backend root through nginx proxy path
curl -k -i https://localhost/api/
```

Expected:
- `/health` returns `200 healthy`
- HTTP requests redirect to HTTPS
- UI is reachable via HTTPS nginx endpoint
- Backend APIs reachable via nginx routes (`/login`, `/vm`, `/api/*`, `/ws/*`)

## 6) Access

- Local: `https://localhost`
- Network: `https://YOUR_SERVER_IP`

Do not expose backend/mysql ports publicly. Use nginx as the only entrypoint.

## 7) Operations

```bash
# logs
docker compose logs -f
docker compose logs -f nginx
docker compose logs -f backend

# restart
docker compose restart

# stop
docker compose down
```

## 8) Security Defaults Already Applied

Current nginx config includes:
- Security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, CSP)
- Hidden file blocking
- Rate limiting on auth endpoints (`/login`, `/adlogin`, `/logout`)
- WebSocket proxy support (`/ws/*`)
- Static asset caching
- `server_tokens off`

## 9) HTTPS Recommendation

This compose stack terminates TLS directly in nginx on port `443`.
Use CA-issued certificates in `nginx/ssl` for production.

## 10) Quick Troubleshooting

```bash
# render final compose config
docker compose config

# check running containers
docker ps

# inspect nginx logs
docker compose logs nginx
```

If UI loads but API fails, verify:
- backend container is healthy
- nginx routes include `/vm`, `/login`, `/adlogin`, `/logout`, `/ws/*`
- browser requests are same-origin and include cookies
