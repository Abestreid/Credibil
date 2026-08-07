-- Migration 005: Add business_category to companies table
-- Classification: micro, small, medium, large based on EU/Moldovan SME criteria
-- Calculated from employee count and revenue/total_assets

ALTER TABLE companies ADD COLUMN IF NOT EXISTS business_category VARCHAR(20);

-- Index for filtering by category
CREATE INDEX IF NOT EXISTS ix_companies_business_category ON companies(business_category) WHERE business_category IS NOT NULL;
