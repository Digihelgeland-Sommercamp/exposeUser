from flask import Flask, request, Response
import json
from run import *

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
    except:
        return "<p>404</p>"

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
                print(type(request_data))
                application.updateStatus(IDkey, request_data)
                status_code = 200

                return application.getApplication(IDkey)

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
    try:
        request_data = request.get_json()

        if request_data != None:
            try:
                print("inne i try")
                application = applicationDB()
                sub_application = application.submitApplication(request_data)
                print("ferdig med sub")
                status_code = 200
                return request_data

            except KeyError:
                response = "Faulty JSON. Please provide JSON in request body"
                status_code = 400

    except:
        return "<p>404</p>"

if __name__=="__main__":
    app.run(debug=True)
