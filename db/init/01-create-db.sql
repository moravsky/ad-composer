-- Connect to postgres database first
\c postgres;

-- Now we can safely drop and create the database
DROP DATABASE IF EXISTS addb;
CREATE DATABASE addb;

-- Create the user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'ad_user') THEN
      CREATE USER ad_user WITH PASSWORD 'your_secure_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE addb TO ad_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO ad_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ad_user;