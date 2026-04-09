-- Drop the feature table if it already exists so the structure can be recreated
DROP TABLE IF EXISTS features.customer_churn_features;

-- Create the feature table that will be used as input for the churn model
CREATE TABLE features.customer_churn_features (
    customer_id TEXT,
    gender_encoded INT,
    senior_citizen INT,
    has_partner INT,
    has_dependents INT,
    tenure INT,
    monthly_charges NUMERIC(10,2),
    total_charges NUMERIC(10,2),
    contract_type INT,
    paperless_billing_encoded INT,
    churn INT
);