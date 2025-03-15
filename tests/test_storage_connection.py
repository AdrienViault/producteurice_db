from db import get_blob_container_client
import os
import pytest

@pytest.mark.skipif(
    not (os.getenv("STORAGE_ACCOUNT_NAME") and os.getenv("STORAGE_ACCOUNT_KEY") and os.getenv("STORAGE_CONTAINER_NAME")),
    reason="Azure storage environment variables not set."
)
def test_azure_blob_connection_integration():
    # Attempt to connect to the blob container
    container_client = get_blob_container_client()

    # Verify that the container client has the expected container name
    expected_container_name = os.getenv("STORAGE_CONTAINER_NAME")
    assert container_client.container_name == expected_container_name

    # List blobs from the container (actual API call)
    blobs = list(container_client.list_blobs())
    
    # For an integration test, you might not know the exact number of blobs,
    # but you can check that the call returns a list.
    assert isinstance(blobs, list)
    
    # Optionally print the number of blobs found (for debugging)
    print(f"Found {len(blobs)} blob(s) in container '{expected_container_name}'.")
