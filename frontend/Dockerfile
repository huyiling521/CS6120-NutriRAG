# =============================
# Dockerfile: frontend/Dockerfile
# =============================
FROM python:3.11-slim

WORKDIR /app

# Install frontend dependencies
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend Streamlit app code
COPY frontend/ /app/

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

