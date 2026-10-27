# Docker Setup Instructions

This project uses Docker Compose to run three containers:
1. **MySQL** - Database server
2. **Backend** - FastAPI application
3. **Frontend** - Vue.js application

## Prerequisites

- Docker and Docker Compose installed on your system

## Quick Start

1. **Start all containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - MySQL: localhost:3306

3. **Stop all containers:**
   ```bash
   docker-compose down
   ```

4. **Stop and remove volumes (clean slate):**
   ```bash
   docker-compose down -v
   ```

## Default Credentials

The database setup script creates default users:
- **Admin user:** `admin` / `password123`
- **Test user:** `testuser` / `password123`

## Database Configuration

The MySQL container is configured with:
- Database: `kvm_db`
- User: `kvm_user`
- Password: `kvm_password`
- Root Password: `rootpassword`

These are set in the `docker-compose.yml` file and can be changed if needed.

## Development Notes

- The backend automatically runs `db_setup.py` on startup to initialize the database
- Frontend and backend are connected via Docker network
- Frontend makes API calls to `http://127.0.0.1:8000` (accessible from browser)
- Backend connects to MySQL using the service name `mysql` (internal Docker network)

## Troubleshooting

- If containers fail to start, check logs: `docker-compose logs`
- To rebuild without cache: `docker-compose build --no-cache`
- To access MySQL directly: `docker exec -it kvm-mysql mysql -u kvm_user -p kvm_db`
