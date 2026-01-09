#!/bin/sh
set -e

echo "Waiting for database to be ready..."
until pg_isready -h db -U dixi -d dixi > /dev/null 2>&1; do
  echo "Database not ready, waiting..."
  sleep 2
done
echo "Database is ready!"

# Import data on every startup
if [ -f "/data/aromanian_dictionary.jsonl" ]; then
  echo "Found aromanian_dictionary.jsonl, importing data..."
  /app/import /data/aromanian_dictionary.jsonl --clear
  echo "Import complete!"
else
  echo "No data file found at /data/aromanian_dictionary.jsonl, skipping import."
fi

echo "Starting server..."
exec /app/dixi-backend
