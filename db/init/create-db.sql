-- Connect to postgres database first
\c postgres;

-- Now we can safely drop and create the database
DROP DATABASE IF EXISTS tofudb;
CREATE DATABASE tofudb;

-- Create the user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'tofu_user') THEN
      CREATE USER tofu_user WITH PASSWORD 'your_secure_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tofudb TO tofu_user;