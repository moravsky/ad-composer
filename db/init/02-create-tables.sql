-- Drop tables if they exist
DROP TABLE IF EXISTS company_info CASCADE;
DROP TABLE IF EXISTS target_personas CASCADE;
DROP TABLE IF EXISTS target_accounts CASCADE;
DROP TABLE IF EXISTS target_industries CASCADE;
DROP TABLE IF EXISTS healthcare_subverticals CASCADE;

-- Create company_info table
CREATE TABLE IF NOT EXISTS company_info (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_website VARCHAR(255),
    company_description TEXT,
    official_overview TEXT,
    product_overview TEXT,
    differentiators TEXT,
    ap_automation_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create personas table
CREATE TABLE IF NOT EXISTS personas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(2048),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create industries table
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(2048),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(2048),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create account_industries junction table (many-to-many)
CREATE TABLE IF NOT EXISTS account_industries (
    account_id INTEGER REFERENCES accounts(id),
    industry_id INTEGER REFERENCES industries(id),
    PRIMARY KEY (account_id, industry_id)
);

-- Create healthcare_subverticals table
CREATE TABLE IF NOT EXISTS healthcare_subverticals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(2048),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

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