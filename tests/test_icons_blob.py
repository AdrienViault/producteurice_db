import os
import pytest
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Storage credentials from .env
account_name = os.getenv("STORAGE_ACCOUNT_NAME")
account_key = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = os.getenv("STORAGE_CONTAINER_NAME")

blob_folder_prefix = "icons/"

# Build connection string
connect_str = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={account_name};"
    f"AccountKey={account_key};"
    f"EndpointSuffix=core.windows.net"
)

# Create blob service client and container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

def test_svg_exists():
    """
    Test to verify that at least one SVG file exists in the 'icons/' folder of the blob container.
    """
    blobs = container_client.list_blobs(name_starts_with=blob_folder_prefix)
    svg_found = any(blob.name.lower().endswith('.svg') for blob in blobs)
    assert svg_found, "No SVG files found in the remote repository under the 'icons/' folder."
