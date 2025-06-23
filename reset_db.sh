#!/bin/bash

echo "🔄 AGGRESSIVE DATABASE RESET - Removing everything and starting fresh..."

# Remove ALL Alembic migrations
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
alembic revision --autogenerate -m "Fresh auto-generated migration"

# Apply migration
echo "🔄 Applying migration..."
alembic upgrade head

echo "✅ Complete database reset completed!"
echo "🚀 You can now run: python main.py" 