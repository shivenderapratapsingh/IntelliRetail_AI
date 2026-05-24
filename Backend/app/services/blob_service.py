from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
load_dotenv()

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)


def download_blob():

    container_name = os.getenv("CONTAINER_NAME")
    blob_name = os.getenv("BLOB_NAME")

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    with open("cleaned_data.csv", "wb") as file:
        download_stream = blob_client.download_blob()
        file.write(download_stream.readall())

    print("CSV downloaded successfully")