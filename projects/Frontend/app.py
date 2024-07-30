import streamlit as st
from azure.storage.blob import BlobServiceClient
# import backen
from backen import process_pdf_and_store_data_from_blob, upload_extracted_text_to_blob

# Azure Blob Storage Configuration (Dictionary)
connection_configs = {
    "Investor": {
        "connection_string": "",
        "container_name": "customers"  
    },
    "Supplier": {
        "connection_string": "",
        "container_name": "investors"
    },
    "Customer": {
        "connection_string": "  
        "container_name": "suppliers" 
    }
}

# Azure Blob Storage Service Client
def get_blob_service_client(connection_string):
    return BlobServiceClient.from_connection_string(connection_string)

def get_blob_filenames(selected_tab):
    config = connection_configs.get(selected_tab)
    if config:
        try:
            blob_service_client = get_blob_service_client(config["connection_string"])
            container_client = blob_service_client.get_container_client(config["container_name"])

            blob_list = container_client.list_blobs()
            filenames = [blob.name for blob in blob_list]
            return filenames

        except Exception as e:
            st.error(f"Error retrieving files for {selected_tab}: {e}")
            return []  
    else:
        return []  # Return empty list if configuration is not found

def process_and_upload_file(selected_tab, file_name):
    config = connection_configs.get(selected_tab)
    if config:
        try:
            # Get Blob Service Client
            blob_service_client = get_blob_service_client(config["connection_string"])

            # Process PDF and get extracted data
            combined_filename, combined_text = process_pdf_and_store_data_from_blob(
                blob_service_client, 
                config["container_name"], 
                file_name
            )

            # Upload the extracted text to a new blob
            upload_extracted_text_to_blob(
                blob_service_client, 
                "extractedtext",  # Use the "extractedtext" container
                combined_filename, 
                combined_text
            )
            
            st.success(f"Processed and uploaded '{combined_filename}' successfully.")
        
        except Exception as e:
            st.error(f"Error processing file {file_name}: {e}")
    else:
        st.error(f"Configuration not found for {selected_tab}")

# App Title
st.title("Sustainability Matrix")

# Create Tabs
tab_names = ["Investor", "Supplier", "Customer"]
selected_tab = st.sidebar.selectbox("Select Stakeholders", tab_names)

# Content for each Tab
if selected_tab:
    st.header(f"{selected_tab} Sustainability Assessment")
    # Dynamically fetch filenames from Azure Blob Storage
    options = get_blob_filenames(selected_tab)
    selected_files = st.multiselect(f"Select {selected_tab} Assessment Files:", options)

    if selected_files:
        for file in selected_files:
            if st.button(f"Process {file}"):
                process_and_upload_file(selected_tab, file)
