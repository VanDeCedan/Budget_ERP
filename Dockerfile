# Stage 1: Build env
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
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

# Initialize Reflex (this installs frontend packages into .web)
RUN reflex init

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Install Node.js in the final image as well if needed for runtime (though Reflex production build might only need it for build)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder
COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy project files and build artifacts
COPY . .
COPY --from=builder /app/.web /app/.web

# Port used by Reflex (Backend usually 8000, Frontend 3000)
# In production mode, Reflex serves both.
EXPOSE 8000
EXPOSE 3000

# Set production environment
ENV RA_ENV=production

# Run the app
# Use --env prod to run in production mode
CMD ["reflex", "run", "--env", "prod", "--backend-only"]
