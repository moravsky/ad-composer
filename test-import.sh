#!/bin/bash
# Save this as test-import.sh

# Connect to the database and verify connectivity
echo "Testing database connection..."
psql -U tofu_user -d tofudb -c "SELECT 'Connection successful';"

# Manually insert a test record to verify permissions
echo "Inserting test record..."
psql -U tofu_user -d tofudb -c "INSERT INTO company_info (company_name) VALUES ('Test Company') RETURNING id;"

# Check if the import_data.py script can be executed
echo "Testing Python script..."
python3 /docker-entrypoint-initdb.d/import_data.py --help

# Check if the JSON files are readable
echo "Testing JSON file reading..."
head -n 5 /docker-entrypoint-initdb.d/company_info.json