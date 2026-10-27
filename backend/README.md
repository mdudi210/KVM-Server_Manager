# KVM Server Backend

Production-focused FastAPI backend for KVM VM operations (list/start/shutdown/reboot/clone/create) with JWT authentication.

## What Changed

- Cookie-based auth is now enabled (HTTP-only JWT cookies).
- `POST /login` now supports both local and AD authentication via `auth_provider`.
- `GET /check-token` endpoint has been removed.
- `POST /adlogin` is kept as a deprecated compatibility route and internally uses unified login logic.
- Input validation has been hardened for usernames, passwords, and VM names.
- Password hashing now uses bcrypt (legacy SHA-512 hashes are still accepted for existing users).

## API Endpoints

### Auth

- `POST /login`
  - Request body:
    - `username` (string)
    - `password` (string)
    - `auth_provider` (`local` or `ad`, optional, default `local`)
  - Response:
    - `id`, `username`, `role`, `auth_provider`
    - `access_token` (included when `RETURN_TOKEN_IN_BODY=true`)
  - Also sets JWT in HTTP-only cookie (`access_token_cookie` by default).

- `POST /logout`
  - Clears auth cookies.

- `POST /adlogin` (deprecated)
  - Compatibility wrapper that routes to `/login` with `auth_provider=ad`.

### VM Operations

- `GET /vm`
  - Lists all VMs.

- `GET /vm?vm_name=<name>`
  - Fetches a specific VM state.

- `POST /vm/state`
  - Body:
    - `state`: `start|shutdown|destroy|reboot`
    - `name`: VM name
    - `expected_state` (optional, conflict protection)

- `POST /vm/new` (admin)
  - Body: `vmtoinstall` (`Linux|Windows`), `name`

- `POST /vm/clone` (admin)
  - Body: `vmtoinstall` (`Linux|Windows`), `name`

### Realtime

- `WS /ws/vm-updates`
  - Auth via query token or auth cookie.
  - Publishes VM change events to connected clients.

## Authentication Flow (Cookie-Based)

1. Client calls `POST /login`.
2. Backend validates local or AD credentials.
3. Backend sets JWT as HTTP-only cookie.
4. Protected endpoints use `jwt_required()` and accept token from header or cookie.
5. `POST /logout` clears auth cookie.

## AD Login Flow

- Use `POST /login` with `"auth_provider": "ad"`.
- Backend authenticates against AD and reads required AD attributes (`KVMrole`, `objectGUID`).
- Returned role is used for authorization checks.

## Required Environment Variables

### Core

- `AUTHJWT_SECRET_KEY` (required)
- `ALGORITHM` (default `HS256`)
- `ALLOWED_ORIGINS` (comma-separated)

### JWT Cookie

- `AUTHJWT_COOKIE_SECURE` (`true/false`)
- `AUTHJWT_COOKIE_SAMESITE` (`lax|strict|none`)
- `AUTHJWT_COOKIE_CSRF_PROTECT` (`true/false`)
- `AUTHJWT_ACCESS_COOKIE_KEY` (default `access_token_cookie`)
- `RETURN_TOKEN_IN_BODY` (`true/false`, default `true` for compatibility)

### Database

- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_DATABASE`

### SSH / KVM

- `SSH_HOSTNAME`
- `SSH_USERNAME`
- `SSH_PASSWORD`
- `SSH_CONNECT_TIMEOUT` (default `10`)
- `SSH_AUTO_ADD_HOST_KEYS` (default `true`)
- `LINUX_TEMPLATE`
- `WIN_TEMPLATE`
- `LINUX_ISO`
- `WIN_ISO`

### Active Directory

- `AD_SERVER`
- `AD_BASE_DN`
- `AD_BIND_USER`
- `AD_BIND_PASSWORD`

## Setup

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Configure environment variables.
3. Initialize DB tables/users:
   ```bash
   python backend/db_setup.py
   ```
4. Start API:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## Testing (cURL)

### 1) Local login (cookie jar)

```bash
curl -i -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"admin","password":"password123","auth_provider":"local"}'
```

### 2) AD login

```bash
curl -i -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"user@domain.local","password":"secret","auth_provider":"ad"}'
```

### 3) List VMs using cookie auth

```bash
curl -i http://127.0.0.1:8000/vm -b cookies.txt
```

### 4) Change VM state with optimistic concurrency

```bash
curl -i -X POST http://127.0.0.1:8000/vm/state \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"vm01","state":"start","expected_state":"shut off"}'
```

### 5) Logout

```bash
curl -i -X POST http://127.0.0.1:8000/logout -b cookies.txt -c cookies.txt
```

## Postman Flow

1. Call `POST /login` and allow cookie capture.
2. Reuse same Postman session for `/vm`, `/vm/state`, `/vm/new`, `/vm/clone`.
3. For admin-only endpoints, login with an admin role.
