import os
from dotenv import load_dotenv

load_dotenv()

MSKEY_VALUE = os.getenv("AZURE_MASTER_KEY")

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://internal-database-test.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', MSKEY_VALUE),
    'database_id': os.environ.get('COSMOS_DATABASE', 'InternalDB'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Applications'),
    'case_number_container_id': os.environ.get('COSMOS_CONTAINER', 'CaseNumbers'),
    'connection_string': os.environ.get('CONNECTION_STRING', 'DefaultEndpointsProtocol=https;AccountName=redforvedlegg;AccountKey=CshrKxCNdLm7LXZ2f3lDpFP92gthtb+7r1C/NjtJySp7JCvQclWNH4sztD1TMPsQX6G4/jC4hcwuZcs/3sOvzQ==;EndpointSuffix=core.windows.net'),
    'vedlegg_container_name': os.environ.get('VEDLEGG_CONTAINER_NAME', 'vedlegg-container')
}
