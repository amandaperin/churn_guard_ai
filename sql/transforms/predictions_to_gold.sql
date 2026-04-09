-- Clear the gold table before inserting the latest segmentation results
TRUNCATE TABLE gold.customer_risk_segments;

-- Insert customer risk segments derived from churn predictions
INSERT INTO gold.customer_risk_segments (
    customer_id,
    churn_probability,
    churn_prediction,
    risk_category
)
SELECT
    customer_id,
    churn_probability,
    churn_prediction,
    CASE
        WHEN churn_probability >= 0.70 THEN 'High'
        WHEN churn_probability >= 0.30 THEN 'Medium'
        ELSE 'Low'
    END AS risk_category
    
FROM gold.churn_predictions;