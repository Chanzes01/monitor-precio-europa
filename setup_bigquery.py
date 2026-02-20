from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import json
import os

# Configuration
PROJECT_ID = os.environ.get("GCP_PROJECT", "monitor-precio-europa") # Change this or set env var
DATASET_ID = "wine_market_data"
TABLE_ID = "prices_staging"
SCHEMA_FILE = "bigquery_schema.json"

def setup_bigquery():
    client = bigquery.Client(project=PROJECT_ID)

    # 1. Create Dataset
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_ref} already exists.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU" # Data location
        client.create_dataset(dataset)
        print(f"Dataset {dataset_ref} created.")

    # 2. Create Table
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    try:
        client.get_table(table_ref)
        print(f"Table {table_ref} already exists.")
    except NotFound:
        with open(SCHEMA_FILE, "r") as f:
            schema_json = json.load(f)
            schema = [bigquery.SchemaField.from_api_repr(field) for field in schema_json]
            
        table = bigquery.Table(table_ref, schema=schema)
        # Partition by date for performance/cost
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="fecha"
        )
        client.create_table(table)
        print(f"Table {table_ref} created.")

if __name__ == "__main__":
    print(f"Setting up BigQuery for project: {PROJECT_ID}")
    try:
        setup_bigquery()
    except Exception as e:
        print(f"Error setting up BigQuery: {e}")
        print("Ensure you have authenticated with 'gcloud auth application-default login' and set GCP_PROJECT env var.")
