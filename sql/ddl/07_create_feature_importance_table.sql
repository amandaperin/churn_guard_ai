-- Drop the table if it already exists
DROP TABLE IF EXISTS gold.model_feature_importance;

-- Create a table to store model feature importance values
CREATE TABLE gold.model_feature_importance (
    feature TEXT,
    importance NUMERIC(12,6)
);