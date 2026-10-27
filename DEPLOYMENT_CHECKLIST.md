# Deployment Checklist (Nginx-First)

Use this checklist before and after deployment.

## Pre-Deployment

- [ ] Ubuntu server ready (20.04+)
- [ ] Docker + Docker Compose installed
- [ ] Firewall opened for `80/tcp` and `443/tcp`
- [ ] `.env` prepared with strong secrets (`AUTHJWT_SECRET_KEY`, DB passwords)
- [ ] `RETURN_TOKEN_IN_BODY=false` set
- [ ] `ALLOWED_ORIGINS` explicitly set (not `*`)

## Docker Deployment

- [ ] Run `docker compose up -d --build`
- [ ] All containers healthy: `docker compose ps`
- [ ] Nginx health check works: `curl http://localhost/health`
- [ ] TLS cert files exist: `nginx/ssl/cert.pem` and `nginx/ssl/key.pem`
- [ ] Frontend loads through nginx HTTPS: `https://SERVER_IP`

## Network Exposure

- [ ] Only nginx is publicly exposed
- [ ] Backend port `8000` is not exposed publicly
- [ ] MySQL port `3306` is not exposed publicly

## Security

- [ ] Default app users/passwords changed
- [ ] `AUTHJWT_COOKIE_SECURE=true` for production
- [ ] Cookie settings reviewed (`AUTHJWT_COOKIE_SAMESITE`)
- [ ] HTTPS plan in place for production
- [ ] Backup strategy defined

## Functional Validation

- [ ] Login works (cookie-based session)
- [ ] VM list/state endpoints work via nginx
- [ ] WebSocket `/ws/vm-updates` works while logged in
- [ ] Logout invalidates session and redirects to login

## Post-Deployment

- [ ] Logs monitored (`docker compose logs -f`)
- [ ] Team has documented restart/recovery procedure
- [ ] Periodic update cadence scheduled
