DROP TABLE IF EXISTS bronze.telco_customers_raw;

CREATE TABLE bronze.telco_customers_raw (
    customer_id TEXT,
    gender TEXT,
    senior_citizen INT,
    partner TEXT,
    dependents TEXT,
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
    total_charges TEXT,
    churn TEXT
);