-- Drop tables if they exist (order matters for foreign key constraints)
-- Drop child tables first, then parent tables
DROP TABLE IF EXISTS personalized_content CASCADE;
DROP TABLE IF EXISTS account_industries CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS company_info CASCADE;
DROP TABLE IF EXISTS industries CASCADE;
DROP TABLE IF EXISTS personas CASCADE;
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
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    industry_id INTEGER REFERENCES industries(id) ON DELETE CASCADE,
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

-- Create personalized_content table for storing workflow results
CREATE TABLE IF NOT EXISTS personalized_content (
    id SERIAL PRIMARY KEY,
    company_info_id INTEGER NOT NULL REFERENCES company_info(id) ON DELETE CASCADE,
    target_account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    personalized_text TEXT NOT NULL,
    text_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_personalized_content_company_target
ON personalized_content(company_info_id, target_account_id);

-- Add comment
COMMENT ON TABLE personalized_content IS 'Stores personalized content generated by the ad content workflow';

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