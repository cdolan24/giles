# Docker Deployment Plan for UC Library Web-Scraper Backend

## Overview
This document outlines the steps to containerize and deploy the FastAPI backend using Docker on a cloud VM or server.

## Steps

1. **Create a Dockerfile**
   - Define the base image (e.g., python:3.10-slim)
   - Install dependencies from requirements.txt
   - Copy backend code into the container
   - Set environment variables for production
   - Expose the backend port (default: 8000)
   - Set the entrypoint to run the FastAPI server (e.g., Uvicorn)

2. **Build the Docker Image**
   - Run: `docker build -t uc-library-backend .`

3. **Run the Container Locally for Testing**
   - Run: `docker run -p 8000:8000 uc-library-backend`
   - Test API endpoints to ensure functionality

4. **Push Image to Container Registry (Optional)**
   - Use Docker Hub, AWS ECR, or other registry
   - Run: `docker tag uc-library-backend <your-repo>/uc-library-backend`
   - Run: `docker push <your-repo>/uc-library-backend`

5. **Deploy on Cloud VM or Server**
   - Install Docker on the VM
   - Pull the image from the registry (if using remote)
   - Run the container with environment variables for secrets/API keys
   - Configure firewall to allow traffic on the backend port
   - Set up HTTPS (e.g., with Nginx reverse proxy or Caddy)

6. **Monitor and Maintain**
   - Use Docker logs and monitoring tools
   - Update the image and redeploy as needed

## Example Dockerfile
```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend/ /app/backend/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Notes
- Store secrets and API keys as environment variables, not in code.
- For production, use a process manager (e.g., Gunicorn) or multi-worker setup if needed.
- Document all environment variables and deployment steps for future maintainers.
