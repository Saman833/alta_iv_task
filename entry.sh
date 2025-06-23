#!/bin/bash

echo "🚀 Starting application setup..."

# Function to handle errors
handle_error() {
    echo "❌ Error occurred: $1"
    exit 1
}

# Check if we're in a Docker environment
if [ -n "$DOCKER_ENV" ]; then
    echo "🐳 Running in Docker environment"
fi

# Wait for database to be ready (if using PostgreSQL)
if [[ "$SQL_URI" == *"postgresql"* ]]; then
    echo "⏳ Waiting for PostgreSQL to be ready..."
    # Extract host and port from SQL_URI
    DB_HOST=$(echo $SQL_URI | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $SQL_URI | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        until nc -z $DB_HOST $DB_PORT; do
            echo "Waiting for database connection..."
            sleep 2
        done
        echo "✅ Database is ready"
    fi
fi

# Remove existing Alembic migrations
echo "🗑️  Removing existing Alembic migrations..."
rm -rf alembic/versions/*.py || handle_error "Failed to remove existing migrations"

# Remove existing database file (for SQLite)
if [[ "$SQL_URI" == *"sqlite"* ]]; then
    echo "🗑️  Removing existing SQLite database..."
    rm -f *.db || true
fi

# Create new migration
echo "📝 Creating new Alembic migration..."
alembic revision --autogenerate -m "Auto-generated migration" || handle_error "Failed to create migration"

# Apply migration
echo "🔄 Applying migration..."
alembic upgrade head || handle_error "Failed to apply migration"

echo "✅ Database setup completed"

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 