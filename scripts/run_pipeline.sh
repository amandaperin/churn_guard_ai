#!/bin/bash
set -e

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

: "${DB_PORT:=5432}"

PSQL_CMD=(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME")

echo "Running DDL..."

PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/01_create_schemas.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/02_create_bronze_table.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/03_create_silver_table.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/04_create_feature_table.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/05_create_predictions_table.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/06_create_gold_tables.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/ddl/07_create_feature_importance_table.sql

echo "Loading bronze data..."
python src/ingestion/load_bronze_csv.py

echo "Running transforms..."
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/transforms/bronze_to_silver.sql
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/transforms/silver_to_features.sql

echo "Generating predictions and feature importance..."
python src/model/predict.py
python src/model/save_feature_importance.py

echo "Updating gold layer..."
PGPASSWORD=$DB_PASSWORD "${PSQL_CMD[@]}" -f sql/transforms/predictions_to_gold.sql

echo "Pipeline completed successfully."
