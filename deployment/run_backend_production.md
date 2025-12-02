# Running Backend Server with Production Settings

## Overview
Run the FastAPI backend in production using Uvicorn or Gunicorn, with proper environment variables and security settings.

## Steps

1. **Run with Uvicorn (Single Worker)**
```
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e API_KEY_UC_LIBRARY="your-uc-api-key" \
  uc-library-backend \
  uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 1
```

2. **Run with Gunicorn (Multiple Workers, Recommended for Production)**
```
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e API_KEY_UC_LIBRARY="your-uc-api-key" \
  uc-library-backend \
  gunicorn -k uvicorn.workers.UvicornWorker backend.app:app --bind 0.0.0.0:8000 --workers 4
```

3. **Configure for HTTPS (Recommended)**
- Use a reverse proxy (Nginx, Caddy) in front of your backend container.
- Terminate SSL at the proxy and forward requests to the backend.

## Notes
- Always run with `DEBUG=false` in production.
- Monitor logs for errors and performance issues.
- Use health checks and restart policies for reliability.
