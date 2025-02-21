-- Drop tables if they exist
DROP TABLE IF EXISTS company_info CASCADE;
DROP TABLE IF EXISTS target_personas CASCADE;
DROP TABLE IF EXISTS target_accounts CASCADE;
DROP TABLE IF EXISTS target_industries CASCADE;
DROP TABLE IF EXISTS healthcare_subverticals CASCADE;

-- Create tables with JSONB columns
CREATE TABLE IF NOT EXISTS company_info (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS target_personas (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS target_accounts (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS target_industries (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS healthcare_subverticals (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

-- Create GIN indexes for full JSON search
CREATE INDEX idx_company_info_gin ON company_info USING GIN (data);
CREATE INDEX idx_personas_gin ON target_personas USING GIN (data);
CREATE INDEX idx_accounts_gin ON target_accounts USING GIN (data);
CREATE INDEX idx_industries_gin ON target_industries USING GIN (data);
CREATE INDEX idx_healthcare_gin ON healthcare_subverticals USING GIN (data);

-- Create indexes for specific JSON paths

-- Company Info indexes
CREATE INDEX idx_company_name ON company_info ((data->'Company Name'->'data'->0->>'value'));
CREATE INDEX idx_company_website ON company_info ((data->'Company Website'->'data'->0->>'value'));

-- Target Personas indexes - creates index for each persona's description and URL
CREATE INDEX idx_personas_text ON target_personas ((data->>'Accounts Payable'));
CREATE INDEX idx_personas_meta_position ON target_personas ((data->'meta'->>'position'));

-- Target Accounts indexes
CREATE INDEX idx_accounts_meta_position ON target_accounts ((data->'meta'->>'position'));

-- Target Industries indexes
CREATE INDEX idx_industries_meta_position ON target_industries ((data->'meta'->>'position'));

-- Healthcare Subverticals indexes
CREATE INDEX idx_healthcare_meta_position ON healthcare_subverticals ((data->'meta'->>'position'));

-- Example queries:
/*
-- Get company name
SELECT data->'Company Name'->'data'->0->>'value' AS company_name 
FROM company_info;

-- Get all URLs from company info
SELECT 
    key,
    value->'data'->0->>'value' AS url
FROM company_info,
jsonb_each(data) 
WHERE value->'data'->0->>'type' = 'url';

-- Get all text content from company info
SELECT 
    key,
    value->'data'->0->>'value' AS content
FROM company_info,
jsonb_each(data) 
WHERE value->'data'->0->>'type' = 'text';

-- Get all personas with position order
SELECT 
    key AS persona_name,
    value->'data'->0->>'value' AS description,
    value->'meta'->>'position' AS position
FROM target_personas,
jsonb_each(data)
WHERE key != 'meta'
ORDER BY (value->'meta'->>'position')::int;
*/