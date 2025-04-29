# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install fastapi "uvicorn[standard]"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the final image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq5

# Copy dependencies from the builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your FastAPI application code
COPY . .

# Expose the port your FastAPI app listens on
EXPOSE 8000

# Run your FastAPI application with Uvicorn
CMD ["uvicorn", "signup:app", "--host", "0.0.0.0", "--port", "8001"]