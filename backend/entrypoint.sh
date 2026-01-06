#!/bin/sh
set -e

echo "Waiting for database to be ready..."
until pg_isready -h db -U dixi -d dixi > /dev/null 2>&1; do
  echo "Database not ready, waiting..."
  sleep 2
done
echo "Database is ready!"

# Check if data needs to be imported
ENTRY_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM entries;" 2>/dev/null || echo "0")
ENTRY_COUNT=$(echo "$ENTRY_COUNT" | tr -d '[:space:]')

if [ "$ENTRY_COUNT" = "0" ] || [ -z "$ENTRY_COUNT" ]; then
  echo "Database is empty, checking for data file..."

  if [ -f "/data/dictionary.jsonl" ]; then
    echo "Found dictionary.jsonl, importing data..."
    /app/import /data/dictionary.jsonl
    echo "Import complete!"
  else
    echo "No data file found at /data/dictionary.jsonl, skipping import."
  fi
else
  echo "Database already has $ENTRY_COUNT entries, skipping import."
fi

echo "Starting server..."
exec /app/dixi-backend
