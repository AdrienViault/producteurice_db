import psycopg2
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient

load_dotenv()

# === PostgreSQL ===
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# === Azure Blob Storage ===
def get_blob_container_client():
    account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("STORAGE_CONTAINER_NAME")

    if not account_name or not account_key or not container_name:
        raise ValueError("Missing required environment variables for Blob Storage")

    connection_str = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account_name};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )

    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    container_client = blob_service_client.get_container_client(container_name)

    return container_client
