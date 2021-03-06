import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime
from werkzeug.exceptions import BadRequest
import json
import random
import secrets

import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']
CASE_NUMBER_CONTAINER_ID = config.settings['case_number_container_id']
CONNECTION_STRING = config.settings['connection_string']
VEDLEGG_CONTAINER_NAME = config.settings['vedlegg_container_name']

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

        # setup container
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

        self.blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        self.container_name = VEDLEGG_CONTAINER_NAME
        self.vedlegg_container_client = self.blob_service_client.get_container_client(self.container_name)


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

    def getAllApplications(self, personidentifikator):
        try:
            applications = list(self.container.query_items(
                query="SELECT r.saksnummer, r.status, r.dato_siste_endring FROM r WHERE r.identifikasjonsnummer.foedselsEllerDNummer=@personidentifikator",
                enable_cross_partition_query=True,
                parameters=[
                    {"name": "@personidentifikator", "value": personidentifikator}
                ]
            ))
        except Exception as e:
            return format(e)
        if applications is None:
            applications=[]
        return json.dumps(applications)

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
        applicationId = self.getId(saksnummer)
        
        saksnummer = int(saksnummer)

        read_item = self.container.read_item(item=applicationId, partition_key=saksnummer)
        read_item['status'] = status

        #Update status_historikk
        if "status_historikk" not in read_item.keys():
            read_item['status_historikk'] = []
        if len(read_item['status_historikk']) > 0:
            newStatusHistorikk = {
                "seq" : read_item['status_historikk'][-1].get("seq") + 1,
                "date" : str(datetime.date.today().strftime("%d-%m-%Y")),
                "status" : status
            }
            read_item['status_historikk'].append(newStatusHistorikk)
        else:
            newStatusHistorikk = {
                "seq": 0,
                "date": str(datetime.date.today().strftime("%d-%m-%Y")),
                "status": status
            }
            read_item['status_historikk'].append(newStatusHistorikk)
        
        read_item['dato_siste_endring'] = str(datetime.date.today().strftime("%d-%m-%Y"))

        response = self.container.upsert_item(body=read_item)

        return read_item['status']
    

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

        newApplication = newApplication
        newApplication["saksnummer"] = int(saksnummer)
        newApplication["id"] = secrets.token_urlsafe()
        self.container.create_item(body=newApplication)
        return str(saksnummer)

    def removeApplication(self, saksnummer):
        applicationId = self.getId(saksnummer)
        del_item = self.getApplication(saksnummer)
        response = self.container.delete_item(item=applicationId, partition_key=saksnummer)

        return del_item

    def createRandomCaseNumber(self):
        number = ""
        for i in range(9):
            number += str(random.randint(0, 9))
        return number

    def uploadAttachment(self, data):
        blob_keys = []
        blob_formats = []
        for i in data.keys():
            name = secrets.token_urlsafe(32)
            fileformat = data[i].content_type.split("/")[1]
            blob_name = name + "." + fileformat
            blob_keys.append(name)
            blob_formats.append(fileformat)
            try:
                vedlegg_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
                vedlegg_client.upload_blob(data[i].stream.read())
            except Exception as e:
                return e
        res = {}
        for i in range(len(blob_keys)):
            res[blob_keys[i]] = blob_formats[i]
        return res


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
                    "sivilstand_ved_innsending": "??pen_for_muligheter"
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
        test.submitApplication(newApplication)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
            print("\nrun_sample done")