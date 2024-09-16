#!/bin/sh

# Wait for the Phoenix service to be ready
echo "Waiting for Phoenix to be ready..."
while ! curl -s http://phoenix:6006/v1/traces > /dev/null; do
    echo "Phoenix is unavailable - sleeping"
    sleep 5
done

echo "Phoenix is up - starting the backend..."
# Start the FastAPI backend
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
