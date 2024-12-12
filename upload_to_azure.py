import os
from azure.storage.blob import BlobServiceClient



def upload_to_azure(file):
    try:
                # Azure Storage connection string
                AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=krunchtest;AccountKey=M8DSdcSRERbD/yucKJGeP41cafaiyuadsZ5yEl6rT/lkn419BAlaWBmAOZ1/X6yLs4ofKU0hrycT+AStB3bIJw==;EndpointSuffix=core.windows.net"  # Replace with your connection string
                container_name = "rpa-test"  # Replace with your container name

                # Initialize the BlobServiceClient
                blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

                # Get the blob client
                blob_name = os.path.basename(file)  # Use the file name as the blob name
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

                # Upload the file
                with open(file, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)

                print(f"File uploaded to Azure Storage successfully: {blob_name}")
    except Exception as e:
        print(f"An error occurred while uploading to Azure: {e}")    