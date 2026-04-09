-- Clear the feature table before loading the transformed records
TRUNCATE TABLE features.customer_churn_features;

-- Insert model-ready features derived from the silver layer
INSERT INTO features.customer_churn_features (
    customer_id,
    gender_encoded,
    senior_citizen,
    has_partner,
    has_dependents,
    tenure,
    monthly_charges,
    total_charges,
    contract_type,
    paperless_billing_encoded,
    churn
)
SELECT
    customer_id,

    -- Encode gender as a binary variable
    CASE 
        WHEN gender = 'Female' THEN 1
        ELSE 0
    END AS gender_encoded,

    senior_citizen,
    has_partner,
    has_dependents,
    tenure,
    monthly_charges,

    -- Replace missing total_charges values with 0 for model input
    COALESCE(total_charges, 0) AS total_charges,

    -- Encode contract type as an ordinal feature
    CASE
        WHEN contract = 'Month-to-month' THEN 0
        WHEN contract = 'One year' THEN 1
        WHEN contract = 'Two year' THEN 2
        ELSE NULL
    END AS contract_type,

    -- Encode paperless billing as a binary variable
    CASE
        WHEN paperless_billing = 'Yes' THEN 1
        ELSE 0
    END AS paperless_billing_encoded,

    churn
FROM silver.telco_customers_clean;