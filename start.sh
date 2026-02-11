#!/bin/sh

# Start the Reflex backend on port 8001
# We use --port 8001 to move it away from Nginx's port
reflex run --env prod --backend-only --loglevel info --backend-port 8001 &

# Start Nginx in the foreground on port 8000
nginx -g "daemon off;"
