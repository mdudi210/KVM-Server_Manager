Place TLS certificate files here for nginx HTTPS termination:

- cert.pem
- key.pem

For local/self-signed cert generation:

```bash
./scripts/generate-ssl.sh localhost ./nginx/ssl
```

For production, replace with CA-issued certificates.
