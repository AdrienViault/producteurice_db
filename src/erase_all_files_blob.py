import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve Azure credentials and container name from environment variables
account_name = os.getenv("STORAGE_ACCOUNT_NAME")
account_key = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = os.getenv("STORAGE_CONTAINER_NAME")

if not account_name or not account_key or not container_name:
    print("Missing Azure storage credentials in environment variables.")
    exit(1)

# Build connection string and create a container client
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# List all blobs in the container
blobs = list(container_client.list_blobs())
print("The following blobs will be deleted:")
for blob in blobs:
    print(f" - {blob.name}")

# Ask for manual confirmation
confirm = input("Are you sure you want to delete all these blobs? Type 'yes' to confirm: ")
if confirm.lower() == "yes":
    for blob in blobs:
        print(f"Deleting {blob.name}...")
        container_client.delete_blob(blob.name)
    print("✅ All blobs have been deleted.")
else:
    print("Operation aborted.")
