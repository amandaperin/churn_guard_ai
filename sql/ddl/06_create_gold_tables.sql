-- Drop the table if it already exists
DROP TABLE IF EXISTS gold.customer_risk_segments;

-- Create a business-friendly gold table with churn risk categories
CREATE TABLE gold.customer_risk_segments (
    customer_id TEXT,
    churn_probability NUMERIC(10,6),
    churn_prediction INT,
    risk_category TEXT
);