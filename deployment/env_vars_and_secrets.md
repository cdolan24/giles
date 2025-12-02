# Environment Variables and Secrets for Backend Deployment

## Overview
Store sensitive information (API keys, secrets, DB credentials) as environment variables. Never hard-code secrets in source files or Docker images.

## Common Environment Variables
- `SECRET_KEY`: Used for JWT authentication
- `API_KEY_UC_LIBRARY`: UC Library API key
- `DB_URL`: Database connection string (if used)
- `DEBUG`: Set to `false` for production

## How to Set Environment Variables

### 1. Docker Run Command
```
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e API_KEY_UC_LIBRARY="your-uc-api-key" \
  uc-library-backend
```

### 2. .env File (with Docker Compose)
Create a `.env` file:
```
SECRET_KEY=your-secret-key
API_KEY_UC_LIBRARY=your-uc-api-key
DB_URL=your-db-url
DEBUG=false
```
Reference in `docker-compose.yml`:
```yaml
environment:
  - SECRET_KEY
  - API_KEY_UC_LIBRARY
  - DB_URL
  - DEBUG
```

## Notes
- Document all required environment variables in your README or deployment plan.
- Use secret managers (AWS Secrets Manager, Azure Key Vault, etc.) for extra security if needed.
- Ensure your backend code reads secrets from environment variables (e.g., `os.environ.get('SECRET_KEY')`).
