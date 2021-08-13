from flask import Flask, request, Response, jsonify
import json

from flask.wrappers import Request
from applicationDB import *
import waitress

app = Flask(__name__)

@app.route("/")
def root():
    return "Root Route!"

@app.route("/applications/<saksnummer>")
def getApplication(saksnummer):
    try:
        IDkey = int(saksnummer) 
        application = applicationDB()
        return application.getApplication(IDkey)
    except Exception as e:
        return e

# Get all application on a single person
@app.route("/all_applications/<personidentifikator>")
def getAllApplications(personidentifikator):
    try:
        application = applicationDB()
        return application.getAllApplications(personidentifikator)
        
    except Exception as e:
        return e

@app.route("/applications/<saksnummer>/status")
def getStatus(saksnummer):
    try:
        IDkey = int(saksnummer)
        application = applicationDB()
        return {"status" : application.getStatus(IDkey)}
    except:
        return "<p>404</p>"

@app.route("/applications/<saksnummer>/update_status", methods=['POST'])
def updateStatus(saksnummer):
    try:
        request_data = request.data.decode()
        if request_data != None:
            try:
                IDkey = int(saksnummer)
                application = applicationDB()
                status = application.updateStatus(IDkey, request_data)
                status_code = 200
                return status
            except KeyError:
                response = "Faulty input. Please provide String in request body"
                status_code = 400 
    except:
        return "<p>404</p>"

@app.route("/applications/<saksnummer>/add_child", methods=['POST'])
def addChild(saksnummer):
    try:
        request_data = request.get_json()
        if request_data != None:
            try:
                IDkey = int(saksnummer)
                application = applicationDB()
                application.addChild(IDkey, request_data)
                status_code = 200

                return application.getApplication(IDkey)

            except KeyError:
                response = "Faulty JSON. Please provide JSON in request body"
                status_code = 400
    except:
        return "<p>404</p>"


@app.route("/applications/<saksnummer>/update_application", methods=['POST'])
def updateApplication(saksnummer):
    try:
        request_data = request.get_json()

        if request_data != None:
            try:
                IDkey = int(saksnummer)
                application = applicationDB()
                upd_application = application.updateApplication(IDkey, request_data)

                status_code = 200
                return application.getApplication(IDkey)

            except KeyError:
                response = "Faulty JSON. Please provide JSON in request body"
                status_code = 400

    except:
        return "<p>404</p>"

@app.route("/applications/submit_application", methods=['POST'])
def submitApplication():
    request_data = json.loads(request.data)
    if(type(request_data) == str):
        request_data = json.loads(request_data)

    if request_data != None:
        try:
            application = applicationDB()
            res = application.submitApplication(request_data)
            status_code = 200
            return res
        except KeyError:
            response = "Faulty JSON. Please provide JSON in request body"
            status_code = 400

@app.route("/applications/upload_attachment", methods=['POST'])
def uploadAttachment():
    data = request.files
    application = applicationDB()
    res = application.uploadAttachment(data)
    return jsonify(res)

if __name__=="__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
