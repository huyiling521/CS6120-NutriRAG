# =============================
# Dockerfile: backend/Dockerfile
# =============================
FROM python:3.11-slim

WORKDIR /code

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ /code/

# Default environment and run
ENV IS_CLOUD_ENV=false
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]