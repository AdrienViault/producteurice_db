import os
import pytest
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Expected media subfolders (relative to your remote storage root)
EXPECTED_SUBFOLDERS = [
    "media/animals",
    "media/crops",
    "media/farms",
    "media/farmers",
    "media/icons",
    "media/products"
]

@pytest.fixture(scope="module")
def container_client():
    # Load credentials from environment variables (set in GitHub Secrets in CI)
    if os.path.exists('.env'):
        load_dotenv()
    account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("STORAGE_CONTAINER_NAME")
    
    # Build the connection string
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client.get_container_client(container_name)

def list_blobs_in_prefix(container_client, prefix):
    """
    Helper function to list blobs under a given prefix.
    """
    return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]

@pytest.mark.parametrize("subfolder", EXPECTED_SUBFOLDERS)
def test_media_subfolder_contains_files(container_client, subfolder):
    """
    Verify that each expected media subfolder in the remote blob storage contains at least one file.
    """
    blobs = list_blobs_in_prefix(container_client, subfolder)
    assert blobs, f"No files found in remote subfolder: {subfolder}"
    print(f"Found {len(blobs)} files in {subfolder}: {blobs}")

