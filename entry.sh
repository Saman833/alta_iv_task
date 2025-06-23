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
    echo "🔧 SQL_URI: $SQL_URI"
    
    # More robust URL parsing
    if [[ "$SQL_URI" =~ postgresql://[^:]+:[^@]+@([^:]+):([0-9]+)/ ]]; then
        DB_HOST="${BASH_REMATCH[1]}"
        DB_PORT="${BASH_REMATCH[2]}"
        echo "🔧 Extracted - Host: $DB_HOST, Port: $DB_PORT"
        
        if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
            echo "⏳ Waiting for database connection to $DB_HOST:$DB_PORT..."
            until nc -z $DB_HOST $DB_PORT; do
                echo "Waiting for database connection..."
                sleep 2
            done
            echo "✅ Database is ready"
        else
            echo "⚠️  Could not extract host/port from SQL_URI, skipping wait"
        fi
    else
        echo "⚠️  Could not parse PostgreSQL URL, skipping wait"
    fi
fi

# AGGRESSIVE CLEANUP - Remove everything
echo "🗑️  AGGRESSIVE CLEANUP - Removing all existing data..."

# Remove ALL Alembic migrations (not just .py files)
echo "🗑️  Removing ALL Alembic migrations..."
rm -rf alembic/versions/* || true
rm -f alembic/versions/.gitkeep || true

# Remove ALL database files
echo "🗑️  Removing ALL database files..."
rm -f *.db || true
rm -f test.db || true
rm -f database.db || true
rm -f app.db || true

# Remove Python cache files
echo "🗑️  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + || true
find . -name "*.pyc" -delete || true

# Remove Alembic cache
echo "🗑️  Removing Alembic cache..."
rm -rf alembic/__pycache__ || true

# Create new migration from current models
echo "📝 Creating new Alembic migration from current models..."
alembic revision --autogenerate -m "Fresh auto-generated migration" || handle_error "Failed to create migration"

# Apply migration
echo "🔄 Applying migration..."
alembic upgrade head || handle_error "Failed to apply migration"

echo "✅ Complete database reset and setup completed!"

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 