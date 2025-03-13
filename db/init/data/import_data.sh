#!/bin/bash
# Script to import data into the Stampli database
set -e

echo "Starting data import process..."

echo "Using Python script at: /docker-entrypoint-initdb.d/data/import_data.py"

# Run the Python script with absolute paths inlined
python3 /docker-entrypoint-initdb.d/data/import_data.py \
  --host localhost \
  --port 5432 \
  --dbname addb \
  --user ad_user \
  --password your_secure_password \
  --company_file /docker-entrypoint-initdb.d/data/company_info.json \
  --target_file /docker-entrypoint-initdb.d/data/target_info.json \
  --clean \
  --summary

# Get exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Data import completed successfully"
else
  echo "Data import failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE