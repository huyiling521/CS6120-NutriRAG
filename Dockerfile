FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Optional: add full dev dependencies if env variable is set
ARG INSTALL_MODE=prod
ENV INSTALL_MODE=${INSTALL_MODE}

# Install dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$INSTALL_MODE" = "dev" ]; then \
    pip install --no-cache-dir -r requirements-dev.txt ; \
    fi

# Copy code
COPY app/ /code/app
# COPY data/ /code/data     # 包含空结构，防止路径不存在

# Default env: assume local
ENV IS_CLOUD_ENV=false

# Command to run the API
ENV PORT=8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]

