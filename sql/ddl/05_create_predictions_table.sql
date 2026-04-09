-- Drop the predictions table if it already exists
DROP TABLE IF EXISTS gold.churn_predictions;

-- Create a table to store churn predictions for each customer
CREATE TABLE gold.churn_predictions (
    customer_id TEXT,
    churn_probability NUMERIC(10,6),
    churn_prediction INT
);