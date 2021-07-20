import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://internal-database-test.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'hu81UE1RC9YNzHOrL0zC0tuxVwmyzhYcGiFnzAw6EnGZhstqhetzOa2xUylw3coa5ylE4YYAhDDVW3R4KbqOvw=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'InternalDB'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Applications'),
    'case_number_container_id': os.environ.get('COSMOS_CONTAINER', 'CaseNumbers')
}