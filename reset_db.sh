#!/bin/bash

echo "🔄 Resetting database and migrations..."

# Remove existing Alembic migrations
echo "🗑️  Removing existing Alembic migrations..."
rm -rf alembic/versions/*.py

# Remove existing database files
echo "🗑️  Removing existing database files..."
rm -f *.db
rm -f test.db

# Create new migration
echo "📝 Creating new Alembic migration..."
alembic revision --autogenerate -m "Fresh migration"

# Apply migration
echo "🔄 Applying migration..."
alembic upgrade head

echo "✅ Database reset completed!"
echo "🚀 You can now run: python main.py" 