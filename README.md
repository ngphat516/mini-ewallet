# Mini E-Wallet

This is a personal project built to learn and practice **backend development**.

The application simulates a small digital wallet where users can register, sign in, manage a wallet, deposit funds, transfer money, and review transaction history. The frontend is mainly a client for consuming and testing the API; the main focus of this project is backend design, implementation, and testing.

## Backend topics covered

- Building REST APIs with FastAPI and Python.
- Authentication with access tokens and refresh tokens.
- Account status enforcement: disabled accounts cannot continue using tokens.
- Wallet management and deposit, withdrawal, and transfer transactions.
- Concurrent transfer handling with database transactions and SQL Server row locks.
- Idempotency to prevent duplicate transaction requests.
- Audit logging for failed transactions.
- Health and readiness checks for SQL Server, MongoDB, and Redis.
- Database schema management through initialization and migration scripts.
- Tests for important flows and configuration.
- Local development environment with Docker Compose.

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy
- Databases: SQL Server, MongoDB, Redis
- Frontend: Next.js, TypeScript, Tailwind CSS
- Infrastructure: Docker and Docker Compose

## Run the project

Make sure Docker Desktop is running.

```powershell
cd backend
docker compose up --build
```

Once the containers are running:

- Backend API: `http://localhost:8000`
- API health check: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
