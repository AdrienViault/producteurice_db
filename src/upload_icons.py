import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

# Load Azure credentials from .env
account_name = os.getenv("STORAGE_ACCOUNT_NAME")
account_key = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = os.getenv("STORAGE_CONTAINER_NAME")

# Blob path prefix
local_icon_folder = "data/icons/"
blob_folder_prefix = "icons/"

# Build connection string
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

# Create blob service client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

def upload_icons():
    for filename in os.listdir(local_icon_folder):
        if filename.startswith("."):
            continue  # Skip hidden files like .DS_Store

        file_path = os.path.join(local_icon_folder, filename)
        blob_path = blob_folder_prefix + filename

        print(f"Uploading {file_path} to {blob_path}...")

        with open(file_path, "rb") as data:
            container_client.upload_blob(
                name=blob_path,
                data=data,
                overwrite=True,
                content_settings=ContentSettings(content_type="image/svg+xml")
            )

    print("✅ Upload complete.")

if __name__ == "__main__":
    upload_icons()
