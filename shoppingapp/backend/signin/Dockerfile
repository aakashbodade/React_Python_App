# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY shoppingapp/backend/signin/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


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
CMD ["uvicorn", "signin:app", "--host", "0.0.0.0", "--port", "8000"]
