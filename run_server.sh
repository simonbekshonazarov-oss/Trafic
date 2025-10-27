#!/bin/bash

# Traffic Share - Server startup script

echo "🚀 Starting Traffic Share Server..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Create necessary directories
mkdir -p logs backups

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Initialize database
echo "📊 Initializing database..."
python traffic_share/scripts/init_db.py

# Run migrations (if using Alembic)
# alembic upgrade head

# Start the server
echo "✅ Starting FastAPI server..."
uvicorn traffic_share.server.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
