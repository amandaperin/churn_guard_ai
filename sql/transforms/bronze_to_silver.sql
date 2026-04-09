-- Clear the silver table before reloading the transformed data
TRUNCATE TABLE silver.telco_customers_clean;

-- Insert cleaned and standardized records from the bronze layer
INSERT INTO silver.telco_customers_clean (
    customer_id,
    gender,
    senior_citizen,
    has_partner,
    has_dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    total_charges,
    churn
)
SELECT
    customer_id,
    gender,
    senior_citizen,
    CASE WHEN partner = 'Yes' THEN 1 ELSE 0 END AS has_partner,
    CASE WHEN dependents = 'Yes' THEN 1 ELSE 0 END AS has_dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    NULLIF(TRIM(total_charges), '')::NUMERIC(10,2) AS total_charges,
    CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END AS churn
FROM bronze.telco_customers_raw;