-- Migration 004: Add detailed financial columns to financial_reports
-- Depozitar provides rich P&L (anexa2), Balance Sheet (anexa1), and Cash Flow (anexa4) data.
-- Previously we only stored 6 summary fields; now we store all detail fields.

-- P&L detail
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS cost_of_goods_sold FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS distribution_expenses FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS admin_expenses FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS other_operating_expenses FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS financial_income FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS financial_expenses FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS income_tax FLOAT;

-- Balance sheet detail
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS current_assets FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS fixed_assets FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS inventories FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS trade_receivables FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS cash_and_banks FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS short_term_debt FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS long_term_debt FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS share_capital FLOAT;

-- Cash flow (anexa4)
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS operating_cash_flow FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS investing_cash_flow FLOAT;
ALTER TABLE financial_reports ADD COLUMN IF NOT EXISTS financing_cash_flow FLOAT;
