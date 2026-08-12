# API and database service

This folder contains the FastAPI service used by Posture Pulse to expose health checks and store posture data in PostgreSQL.

## Start the stack

From the repository's `RPi/` directory:

```bash
cp api/.env.example api/.env
docker compose up -d --build
```

Useful endpoints:

- `http://<pi-ip>:8000/docs` - interactive API documentation
- `http://<pi-ip>:8000/health` - API health check
- `http://<pi-ip>:8000/db-health` - database connection health check

The example environment file contains local development credentials. Replace them before deploying the system outside a trusted network.
