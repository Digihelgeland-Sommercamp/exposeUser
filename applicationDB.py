import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from datetime import datetime
from werkzeug.exceptions import BadRequest
import json
import random

import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']
CASE_NUMBER_CONTAINER_ID = config.settings['case_number_container_id']

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

        try:
            self.case_number_container = self.db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
            print('Container with id \'{0}\' created'.format(CASE_NUMBER_CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            self.case_number_container = self.db.get_container_client(CONTAINER_ID)
            print('Container with id \'{0}\' was found'.format(CASE_NUMBER_CONTAINER_ID))

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
        if application is None:
            raise BadRequest
        if(len(application)>0):
            return format(application[0])
        else:
            raise BadRequest

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


    def updateStatus(self, saksnummer, status):
        #TODO: Insert check for status

        applicationId = self.getId(saksnummer)
        
        saksnummer = int(saksnummer)

        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        read_item['status'] = status


        #Update status_historikk
        if len(read_item['status_historikk']) > 0:
            newStatusHistorikk = {
                "seq" : read_item['status_historikk'][-1].get("seq") + 1,
                "date" : str(datetime.now()),
                "status" : status
            }
            read_item['status_historikk'].append(newStatusHistorikk)

        response = self.container.upsert_item(body=read_item)

        return read_item['status']
    
    def addChild(self, saksnummer, newChild):
        applicationId = self.getId(saksnummer)
        
        saksnummer = int(saksnummer)

        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        read_item["opplysninger_om_barn_barnehage"].append(newChild)

        response = self.container.upsert_item(body=read_item)

        return self.getApplication(saksnummer)

    def updateApplication(self, saksnummer, newApplication):
        applicationId = self.getId(saksnummer)
        
        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        response = self.container.replace_item(item=read_item, body=newApplication)

        return self.getApplication(saksnummer)

    def submitApplication(self, newApplication):
        saksnummer = self.createRandomCaseNumber()
        for i in range(3):
            application = list(self.container.query_items(
                query="SELECT * FROM r WHERE r.saksnummer=@saksnummer",
                parameters=[
                    { "name":"@saksnummer", "value": saksnummer }
                ]
            ))
            if len(application)==0:
                break
            saksnummer = self.createRandomCaseNumber()
        newApplication["saksnummer"] = int(saksnummer)
        self.container.create_item(body=newApplication)
        return str(saksnummer)

    def removeApplication(self, saksnummer):
        applicationId = self.getId(saksnummer)
        print("appId:",applicationId)
        print("saksnr:", saksnummer)

        del_item = self.getApplication(saksnummer)
        response = self.container.delete_item(item=applicationId, partition_key=saksnummer)

        return del_item

    def createRandomCaseNumber(self):
        number = ""
        for i in range(9):
            number += str(random.randint(0, 9))
        return number


def run_sample():
    try:
        test = applicationDB()
        test.readApplication(23482973)
        test.updateStatus(23482973, 'ikke_godkjent')
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

        newChild = {
            "barnets_navn": "Jon",
            "fodselsnummer": 28049712305,
            "navn_pa_barnehage": "Barnehage City",
            "prosent_plass": 100
        }

        test.updateApplication(23482974, ny_soeknad)
        test.submitApplication(newApplication)
        #test.removeApplication(23482976)
        test.addChild(23482973, newChild)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    
    #run_sample()
    app = applicationDB()
    
