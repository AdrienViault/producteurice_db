import os
import mimetypes
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Azure credentials and container name from environment variables
account_name = os.getenv("STORAGE_ACCOUNT_NAME")
account_key = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = os.getenv("STORAGE_CONTAINER_NAME")

if not account_name or not account_key or not container_name:
    print("Missing Azure storage credentials in environment variables.")
    exit(1)

# Build connection string and create a BlobServiceClient
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Local media root and remote base folder (here we want to mirror the structure under 'media/')
LOCAL_MEDIA_ROOT = "media"
REMOTE_MEDIA_ROOT = "media"  # Upload preserving the local folder structure

# Optional: A mapping of file extensions to content types (if not set by mimetypes)
CONTENT_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".mp4": "video/mp4"
}

def get_content_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    # Use our mapping first, then fallback to mimetypes
    return CONTENT_TYPE_MAP.get(ext, mimetypes.guess_type(file_path)[0] or "application/octet-stream")

def upload_media_files():
    for root, dirs, files in os.walk(LOCAL_MEDIA_ROOT):
        for file in files:
            local_file_path = os.path.join(root, file)
            # Compute the relative path from the media root and use it for the blob path
            rel_path = os.path.relpath(local_file_path, LOCAL_MEDIA_ROOT)
            # Normalize path separator to forward slashes for blob storage
            blob_path = os.path.join(REMOTE_MEDIA_ROOT, rel_path).replace(os.sep, "/")

            content_type = get_content_type(local_file_path)
            print(f"Uploading {local_file_path} to {blob_path} with content type '{content_type}'...")

            with open(local_file_path, "rb") as data:
                container_client.upload_blob(
                    name=blob_path,
                    data=data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=content_type)
                )

    print("✅ Upload complete.")

if __name__ == "__main__":
    upload_media_files()
