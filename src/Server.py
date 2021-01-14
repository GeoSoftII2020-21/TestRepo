import os
import uuid
import datetime
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import xarray
import Eval

app = Flask(__name__)
CORS(app)

docker = False


Datastore = {}




@app.route("/api/v1/", methods=['GET'])
def default():
    """
    Soll ein JSON mit der Kurzübersicht unserer API Returnen
    :return: JSON
    """
    # Todo: Anpassen
    data = {"api_version": "1.0.0", "backend_version": "1.1.2", "stac_version": "string", "id": "cool-eo-cloud",
            "title": "WWU Geosoft2 Projekt", "description": "WWU Projekt", "production": False,
            "endpoints": [{"path": "/collections", "methods": ["GET"]}, {"path": "/processes", "methods": ["GET"]},
                          {"path": "/jobs", "methods": ["GET", "POST"]},
                          {"path": "/jobs/{job_id}", "methods": ["DELETE", "PATCH"]},
                          {"path": "/jobs/{job_id}/result", "methods": ["GET", "POST"]}], "links": [
            {"href": "https://www.uni-muenster.de/de/", "rel": "about", "type": "text/html",
             "title": "Homepage of the service provider"}]}
    return jsonify(data)


@app.route("/.well-known/openeo", methods=["GET"])
@app.route("/api/v1/.well-known/openeo", methods=["GET"])
def wellKnownEO():
    """
    Implementiert abfrage für Supported openEO Versions auf wunsch von Judith.
    Evtl. Antwort noch anpassen. Ich bin mir noch nicht ganz sicher ob das so richtig ist. Insbesondere weiß ich nicht welche version wir implementieren.
    :returns:
        jsonify(data): JSON mit der Unterstützen API Version und ein verweis auf diese.
    """
    data = {
        "versions": [
            {
                "url": "http://localhost/api/v1",
                "api_version": "1.0.0",
                "production": False
            },
        ]
    }
    return jsonify(data)


@app.route("/api/<string:version>/collections", methods=['GET'])
def collections(version):
    """
    Returnt alle vorhandenen Collections bei einer GET Request
    Collections sollten evtl im dezidierten server gelistet sein, entsprechend sollte dort die Antwort generiert werden
    :returns:
        jsonify(data): Alle Collections in einer JSON
    """
    # Todo: Abfrage an Daten Managment System über welche Collections wir überhaupt verfügen
    if (version == "v1"):
        with open("json/collection_description.json") as json_file:
            data = json.load(json_file)
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/processes", methods=['GET'])
def processes(version):
    """
    Returnt alle vorhandenen processes bei einer GET Request
    Quelle für NDVI: https://github.com/Open-EO/openeo-processes/blob/master/ndvi.json
    :returns:
        jsonify(data): Alle processes in einer JSON
    """
    if (version == "v1"):
        with open("json/process_description.json") as json_file:
            data = json.load(json_file)
        # Todo: Anpassen, Dev Team beauftragen das gleiche für SST zu schreiben, von Dev Team Verifizieren Lassen
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs", methods=['GET'])
def jobsGET(version):
    """
    Returnt alle vorhandenen jobs bei einer GET Request
    :returns:
        jsonify(data): Alle jobs in einer JSON
    """
    if (version == "v1"):
        data = {
            "jobs": [
            ],
            "links": [
                {
                    "rel": "related",
                    "href": "https://example.openeo.org",
                    "type": "text/html",
                    "title": "openEO"
                }
            ]
        }  # Todo: Anpassen
        for i in Datastore:
            data["jobs"].append(Datastore[i])
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs", methods=['POST'])
def jobsPOST(version):
    """
    Nimmt den Body eines /jobs post request entgegen. Wichtig: Startet ihn NICHT!
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """

    # Todo: Funktion schreiben die auswertet was im JSON steht...
    if (version == "v1"):
        dataFromPost = request.get_json()  # Todo: JSON Evaluieren
        ev = Eval.evalTaskAndQueue(dataFromPost, Datastore)
        if (ev[0]):
            resp = Response(status=200)
            resp.headers["Location"] = "localhost/api/v1/jobs/" + str(ev[1])
            resp.headers["OpenEO-Identifier"] = str(ev[1])
            return resp
        else:
            data = {
                "id": "",  # Todo: ID Generieren bzw. Recherchieren
                "code": "400",
                "message": "Unbekannter Job Typ.",
                "links": [
                    {
                        "href": "https://example.openeo.org/docs/errors/SampleError",
                        # Todo: Passenden Link Recherchieren & Einfügen
                        "rel": "about"
                    }
                ]
            }
            return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>", methods=['PATCH'])
def patchFromID(version, id):
    """
    Nimmt den Body einer Patch request mit einer ID entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPatch = request.get_json()
    if (version == "v1"):
        if Eval.evalTask(dataFromPatch):
            dataFromPatch["created"] = Datastore[uuid.UUID(id)]["created"]
            dataFromPatch["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z"
            Datastore[uuid.UUID(id)] = dataFromPatch
        else:
            data = {
                "id": "",  # Todo: ID Generieren bzw. Recherchieren
                "code": "404",
                "message": "Ungültiger API Aufruf.",
                "links": [
                    {
                        "href": "https://example.openeo.org/docs/errors/SampleError",
                        # Todo: Passenden Link Recherchieren & Einfügen
                        "rel": "about"
                    }
                ]
            }
            return jsonify(data)


    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>", methods=["DELETE"])
def deleteFromID(version, id):
    """
    Nimmt eine Delete request für eine ID Entgegen
    Todo: Herausfinden wie man das Umsetzt. Irgendwie müssen wir laufende Dask Prozesse Terminieren.
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    if (version == "v1"):
        Datastore[uuid.UUID(id)]["status"] = "created"
        return Response(status=204)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=['POST'])
def startFromID(version, id):
    """
    Startet einen Job aufgrundlage einer ID aus der URL. Nimmt ebenso den Body der Post request entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    #Todo: Datastore sollte immer alle elemente beinhalten
    if (version == "v1"):
        Datastore[uuid.UUID(str(id))]["status"] = "queued"
        job = Datastore[uuid.UUID(str(id))]
        temp = dict(job)
        temp["id"] = str(job["id"])
        if docker:
            requests.post("http://processManager:80/takeJob", json=temp)
        else:
            requests.post("http://localhost:440/takeJob", json=temp)
        return Response(status=204)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=["GET"])
def getJobFromID(version, id):
    """
    Nimmt den Body einer GET request mit einer ID entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): Ergebnis des Jobs welcher mit der ID assoziiert ist.
    """
    bbox = []
    for i in Datastore[uuid.UUID(id)]:
        for j in Datastore[uuid.UUID(id)]["process"]["process_graph"]:
            if Datastore[uuid.UUID(id)]["process"]["process_graph"][j]["id"] == "load_collection":
                bbox.append(Datastore[uuid.UUID(id)]["process"]["process_graph"][j]["arguments"]["spatial_extent"])
    if (version == "v1"):
        returnVal = {
            "stac_version":  "string",
            "stac_extensions": [],
            "id": id,
            "type": "Feature",
            "bbox": bbox,
            "geometry": None, #Rücksprache was das ist?
            "properties": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z",
                "start_datetime": Datastore[uuid.UUID(id)]["start_datetime"],
                "end_datetime": Datastore[uuid.UUID(id)]["end_datetime"],
                "title": Datastore[uuid.UUID(id)]["title"],
                "description": Datastore[uuid.UUID(id)]["description"],
                "license":  "", #Todo: Lizenz Einfpgen
                "providers": [{
                    "name": "WWU Studienprojekt",
                    "description": "Studienprojekt der WWU",
                    "roles": [
                        "host"
                    ]
                }
                ],
                "created": Datastore[uuid.UUID(id)]["created"],
                "updated": Datastore[uuid.UUID(id)]["updated"],
                "expires": None,
            },
            "assets":  { #Todo: Aus prozessbeschreibung generieren
            }, #Todo: Ergänzen wenn wir netcdfs haben
            "links": []
        }
        return jsonify(returnVal)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/data", methods=["POST"])
def postData():
    """
    Custom Route, welche nicht in der OpenEO API Vorgesehen ist. Nimmt die daten der Post request entgegen.
    Todo: Evtl. Verschieben das der Upload nur noch von der Lokalen Maschine aus möglich ist?
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPost = request.get_data()
    f = open('data/sst.day.mean.1984.v2.nc', 'w+b')
    binary_format = bytearray(dataFromPost)
    f.write(binary_format)
    f.close()
    #if docker:
    #    r = requests.post("http://database:80/data", json=None)
    #else:
    #    r = requests.post("http://localhost:443/data", json=None)
    #data = r.json()
    return jsonify(None)


@app.route("/jobRunning/<uuid:id>", methods=["GET"])
def jobUpdate(id):
    """
    Aktualisiert den Job status sofern er nicht abgebrochen wurde
    :param id: ID
    :return: Json mit Job
    """
    print(type(id))
    if Datastore[id]["status"] == "queued":
        Datastore[id]["status"] = "running"
        return jsonify(Datastore[id])
    elif Datastore[id]["status"] != "queued":
        return Datastore[id]


@app.route("/takeData/<uuid:id>", methods=["POST"])
def takeData(id):
    """
    Nimmt das ergebnis eines jobs entgegen und fügt ihm den Datastore hinzu
    :rtype: Response Object
    """
    Datastore[uuid.UUID(id)]["result"] = request.get_json()
    return Response(status=200)


def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    app.run(debug=True, host="0.0.0.0", port=80)  # Todo: Debug  Ausschalten, Beißt sich  mit Threading


if __name__ == "__main__":
    serverBoot()
