import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-cosmosdb-resources-portal#create-an-azure-cosmos-db-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Item resource for Azure Cosmos
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

class applicationDB:
    def __init__(self):
        #   Initialize the applicationDB
        self.client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
        try:
            self.db = self.client.create_database(id=DATABASE_ID)
            print('Database with id \'{0}\' created'.format(DATABASE_ID))

        except exceptions.CosmosResourceExistsError:
            self.db = self.client.get_database_client(DATABASE_ID)
            print('Database with id \'{0}\' was found'.format(DATABASE_ID))

        # setup container for this sample
        try:
            self.container = self.db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            self.container = self.db.get_container_client(CONTAINER_ID)
            print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    def getId(self, saksnummer):
        application = list(self.container.query_items(
            query="SELECT * FROM r WHERE r.saksnummer=@saksnummer",
            parameters=[
                { "name":"@saksnummer", "value": saksnummer }
            ]
        ))
        if(len(application)>0):
            ...
        else:
            return None

        applicationId = application[0]["id"]

        return applicationId

    def readApplication(self, saksnummer):
        applicationId = self.getId(saksnummer)

        response = self.container.read_item(item=applicationId, partition_key=saksnummer)

    def getApplication(self, saksnummer):
        application = list(self.container.query_items(
            query="SELECT * FROM r WHERE r.saksnummer=@saksnummer",
            parameters=[
                { "name":"@saksnummer", "value": saksnummer }
            ]
        ))
        if(len(application)>0):
            return format(application[0])
        else:
            return None

    def getStatus(self, saksnummer):
        application = list(self.container.query_items(
            query="SELECT * FROM r WHERE r.saksnummer=@saksnummer",
            parameters=[
                { "name":"@saksnummer", "value": saksnummer }
            ]
        ))
        if(len(application)>0):
            return format(application[0].get("status"))
        else:
            return None


    def putStatus(self, saksnummer, status):
        #Insert check for status format

        applicationId = self.getId(saksnummer)
        
        saksnummer = int(saksnummer)

        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        read_item['status'] = status

        response = self.container.upsert_item(body=read_item)

        return read_item['status']

    def updateApplication(self, saksnummer, newApplication):
        applicationId = self.getId(saksnummer)
        
        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        response = self.container.replace_item(item=read_item, body=newApplication)

        return self.getApplication(saksnummer)

    def submitApplication(self, newApplication):
        #Insert check for newApplication in right format
        
        #Create a new Application object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as is without converting into rows/columns.
        self.container.create_item(body=newApplication)
        saksnummer = int(newApplication.get("saksnummer"))
        
        return self.getApplication(saksnummer)

    def removeApplication(self, saksnummer):
        applicationId = 



def run_sample():
    try:
        test = applicationDB()
        test.readApplication(23482973)
        test.putStatus(23482973, 'ikke_godkjent')
        test.readApplication(23482973)
        ny_soeknad = {
            "saksnummer": 23482974,
            "status": "ikke_godkjent",
            "status_historikk": [
                {
                    "seq": 0,
                    "date": "12:36-07-07-2021",
                    "status": "til_behandling"
                },
                {
                    "seq": 1,
                    "date": "12:37-07-07-2021",
                    "status": "ikke_godkjent"
                }
            ],
            "eier": [
                {
                    "fodselsnummer": 12345678976,
                    "sivilstand_ved_innsending": "åpen_for_muligheter"
                }
            ],
            "opplysninger_om_barn_barnehage": [
                {
                    "barnets_navn": "Htide",
                    "fodselsnummer": 17382943887,
                    "navn_pa_barnehage": "Barnehage City",
                    "prosent_plass": 100
                }
            ],
            "saksbehandler": [
                {
                    "brukernavn": "ed1th"
                }
            ],
            "id": "0e5487a2-b117-40b5-a2fe-3d414c328c54",
            "_rid": "s5FjAMdG60ACAAAAAAAAAA==",
            "_self": "dbs/s5FjAA==/colls/s5FjAMdG60A=/docs/s5FjAMdG60ACAAAAAAAAAA==/",
            "_etag": "\"01008770-0000-3c00-0000-60e808d00000\"",
            "_attachments": "attachments/",
            "_ts": 1625819344
        }

        newApplication = {
            "saksnummer": 23482976,
            "status": "ikke_godkjent",
            "status_historikk": [
                {
                    "seq": 0,
                    "date": "12:36-07-07-2021",
                    "status": "til_behandling"
                },
                {
                    "seq": 1,
                    "date": "12:37-07-07-2021",
                    "status": "godkjent"
                }
            ],
            "eier": [
                {
                    "fodselsnummer": 12345678908,
                    "sivilstand_ved_innsending": "partner"
                }
            ],
            "opplysninger_om_barn_barnehage": [
                {
                    "barnets_navn": "A was here",
                    "fodselsnummer": 17382943827,
                    "navn_pa_barnehage": "Barnehage City",
                    "prosent_plass": 50
                }
            ],
            "saksbehandler": [
                {
                    "brukernavn": "ed1th"
                }
            ],
            "id": "c4be20f1-e127-4b8d-903e-c9f1cff1b73a",
            "_rid": "s5FjAMdG60ABAAAAAAAAAA==",
            "_self": "dbs/s5FjAA==/colls/s5FjAMdG60A=/docs/s5FjAMdG60ABAAAAAAAAAA==/",
            "_etag": "\"0100c005-0000-3c00-0000-60f54dc70000\"",
            "_attachments": "attachments/",
            "_ts": 1626688967
        }

        test.updateApplication(23482974, ny_soeknad)
        test.submitApplication(newApplication)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()
