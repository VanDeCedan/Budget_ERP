# Stage 1: Build env
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (Reflex requires it for the frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create and activate virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Initialize Reflex
RUN reflex init

# Export frontend static assets
RUN reflex export --frontend-only --no-zip

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Port used by Nginx (Frontend & Proxy)
EXPOSE 8000

# Install Nginx and cleanup
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Copy virtual env and built frontend from builder
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/.web /app/.web

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Setup env
ENV PATH="/app/venv/bin:$PATH"
ENV RA_ENV=production

# Make start script executable
RUN chmod +x start.sh

# Run the app via startup script
CMD ["./start.sh"]
