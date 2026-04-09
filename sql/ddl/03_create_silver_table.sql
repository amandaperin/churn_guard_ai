-- Drop the table if it already exists so the structure can be recreated
DROP TABLE IF EXISTS silver.telco_customers_clean;

-- Create the cleaned silver table with standardized data types
CREATE TABLE silver.telco_customers_clean (
    customer_id TEXT,
    gender TEXT,
    senior_citizen INT,
    has_partner INT,
    has_dependents INT,
    tenure INT,
    phone_service TEXT,
    multiple_lines TEXT,
    internet_service TEXT,
    online_security TEXT,
    online_backup TEXT,
    device_protection TEXT,
    tech_support TEXT,
    streaming_tv TEXT,
    streaming_movies TEXT,
    contract TEXT,
    paperless_billing TEXT,
    payment_method TEXT,
    monthly_charges NUMERIC(10,2),
    total_charges NUMERIC(10,2),
    churn INT
);