import os
from azure.storage.blob import BlobServiceClient



def upload_to_azure(df,name):
    try:
                # Azure Storage connection string
                AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=krunchtest;AccountKey=M8DSdcSRERbD/yucKJGeP41cafaiyuadsZ5yEl6rT/lkn419BAlaWBmAOZ1/X6yLs4ofKU0hrycT+AStB3bIJw==;EndpointSuffix=core.windows.net"  # Replace with your connection string
                container_name = "rpa-test"  # Replace with your container name

                # Initialize the BlobServiceClient
                blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
                container_client = blob_service_client.get_container_client(container_name)

                container_client.upload_blob(name=name, data=df, overwrite=True)


                print(f"File uploaded to Azure Storage successfully: {name}")
    except Exception as e:
        print(f"An error occurred while uploading to Azure: {e}")    