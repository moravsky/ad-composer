#!/bin/bash
set -e

# Start the PostgreSQL server in the background
docker-entrypoint.sh "$@" &
PG_PID=$!

# Wait for PostgreSQL to become ready
until pg_isready -U tofu_user -d tofudb; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
done

echo "PostgreSQL started, running import script..."
# Run the import script
if [ -f /docker-entrypoint-initdb.d/data/import_data.sh ]; then
  bash /docker-entrypoint-initdb.d/data/import_data.sh
else
  echo "Import script not found!"
fi

# Wait for the PostgreSQL process to finish
wait $PG_PID