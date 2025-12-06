# -------------------------
# Stage 1: Build
# -------------------------
FROM python:3.12-slim AS build

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# Stage 2: Runtime
# -------------------------
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages
COPY --from=build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=build /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Expose port for Fly.io
EXPOSE 8080

# Use gunicorn to run Flask
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main_ui_web:app"]
