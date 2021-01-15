import uuid

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import Eval

app = Flask(__name__)
CORS(app)

worker = {}
Datastore = {}
Queue = []
Running = []
Thread = None


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
        data = {
            "collections": [
                {
                    "stac_version": "0.9.0",  # Todo: Welche Stack Version verwenden wir?
                    "id": "MOD09Q1",  # Todo: Gibt es vorgeschriebene ids oder müssen wir die selbst generieren?
                    "title": "Placeholder Title",
                    "description": "Placeholder",
                    "license": "proprietary",  # Anpassen für die Lizenztypen
                    "extent": {
                        "spatial": {
                            "bbox": [
                                [
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            ]
                        },
                        "temporal": {
                            "interval": [
                                [
                                    "2000-02-01T00:00:00Z",
                                    None
                                ]
                            ]
                        }
                    },
                    "links": [
                        {
                            "rel": "license",
                            "href": "https://example.openeo.org/api/collections/MOD09Q1/license"
                        }
                    ]
                }
            ],
            "links": [
                {
                    "rel": "alternate",
                    "href": "https://example.openeo.org/csw",
                    "title": "openEO catalog (OGC Catalogue Services 3.0)"
                }
            ]
        }  # Todo: Anpassen
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
        data = {
            "processes": [
                {
                    "id": "ndvi",
                    "summary": "Normalized Difference Vegetation Index",
                    "description": "Computes the Normalized Difference Vegetation Index (NDVI). The NDVI is computed as *(nir - red) / (nir + red)*.\n\nThe `data` parameter expects a raster data cube with a dimension of type `bands` or a `DimensionAmbiguous` error is thrown otherwise. By default, the dimension must have at least two bands with the common names `red` and `nir` assigned or the user need to specify the parameters `nir` and `red`. Otherwise either the error `NirBandAmbiguous` or `RedBandAmbiguous` is thrown. The common names for each band are specified in the collection's band metadata and are *not* equal to the band names.\n\nBy default, the dimension of type `bands` is dropped by this process. To keep the dimension specify a new band name in the parameter `target_band`. This adds a new dimension label with the specified name to the dimension, which can be used to access the computed values. If a band with the specified name exists, a `BandExists` is thrown.\n\nThis process is very similar to the process ``normalized_difference()``, but determines the bands automatically based on the common names (`red`/`nir`) specified in the metadata.",
                    "categories": [
                        "math > indices",
                        "vegetation indices"
                    ],
                    "parameters": [
                        {
                            "name": "data",
                            "description": "A raster data cube with two bands that have the common names `red` and `nir` assigned.",
                            "schema": {
                                "type": "object",
                                "subtype": "raster-cube"
                            }
                        },
                        {
                            "name": "nir",
                            "description": "The name of the NIR band. Defaults to the band that has the common name `nir` assigned.\n\nEither the unique band name (metadata field `name` in bands) or one of the common band names (metadata field `common_name` in bands) can be specified. If unique band name and common name conflict, the unique band name has higher priority.",
                            "schema": {
                                "type": "string",
                                "subtype": "band-name"
                            },
                            "default": "nir",
                            "optional": True
                        },
                        {
                            "name": "red",
                            "description": "The name of the red band. Defaults to the band that has the common name `red` assigned.\n\nEither the unique band name (metadata field `name` in bands) or one of the common band names (metadata field `common_name` in bands) can be specified. If unique band name and common name conflict, the unique band name has higher priority.",
                            "schema": {
                                "type": "string",
                                "subtype": "band-name"
                            },
                            "default": "red",
                            "optional": True
                        },
                        {
                            "name": "target_band",
                            "description": "By default, the dimension of type `bands` is dropped. To keep the dimension specify a new band name in this parameter so that a new dimension label with the specified name will be added for the computed values.",
                            "schema": [
                                {
                                    "type": "string",
                                    "pattern": "^\\w+$"
                                },
                                {
                                    "type": "null"
                                }
                            ],
                            "default": None,
                            "optional": True
                        }
                    ],
                    "returns": {
                        "description": "A raster data cube containing the computed NDVI values. The structure of the data cube differs depending on the value passed to `target_band`:\n\n* `target_band` is `null`: The data cube does not contain the dimension of type `bands` any more, the number of dimensions decreases by one. The dimension properties (name, type, labels, reference system and resolution) for all other dimensions remain unchanged.\n* `target_band` is a string: The data cube keeps the same dimensions. The dimension properties remain unchanged, but the number of dimension labels for the dimension of type `bands` increases by one. The additional label is named as specified in `target_band`.",
                        "schema": {
                            "type": "object",
                            "subtype": "raster-cube"
                        }
                    },
                    "exceptions": {
                        "NirBandAmbiguous": {
                            "message": "The NIR band can't be resolved, please specify a band name."
                        },
                        "RedBandAmbiguous": {
                            "message": "The red band can't be resolved, please specify a band name."
                        },
                        "DimensionAmbiguous": {
                            "message": "dimension of type `bands` is not available or is ambiguous.."
                        },
                        "BandExists": {
                            "message": "A band with the specified target name exists."
                        }
                    },
                    "links": [
                        {
                            "rel": "about",
                            "href": "https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index",
                            "title": "NDVI explained by Wikipedia"
                        },
                        {
                            "rel": "about",
                            "href": "https://earthobservatory.nasa.gov/features/MeasuringVegetation/measuring_vegetation_2.php",
                            "title": "NDVI explained by NASA"
                        },
                        {
                            "rel": "about",
                            "href": "https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#common-band-names",
                            "title": "List of common band names as specified by the STAC specification"
                        }
                    ]
                },
                {
                    "id": "mean_sst",
                    "summary": "Mean Sea Surface Temperature",
                    "description": "Computes the arithmatic mean of sst data. The arithmetic mean is defined as the sum of all elements divided by the number of elements. The user defines a timeframe and optionally also a spatial subset, for which the mean is to be computed. For each day in the given timeframe the sea surface temperature values for a cell are summed up and divided by the number of days in the timeframe. This is done for all cells within the spatial subset or, if no bounding box was defined, for all cells in the dataset.",
                    "categories": [
                        "math",
                        "reducer"
                    ],
                    "parameters": [
                        {
                            "name": "data",
                            "description": "A raster data cube containing sst data.",
                            "schema": {
                                "type": "object",
                                "subtype": "raster-cube"
                            }
                        },
                        {
                            "name": "timeframe",
                            "description": "An array with two values: [start date, end date]. Timeframe values are strings of the format 'year-month-day'. For example: '1981-01-01'.",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "subtype": "date"
                                }
                            }
                        },
                        {
                            "name": "bbox",
                            "description": "An array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. For example: [0,-90,360,90]",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                }
                            },
                            "optional": True
                        }
                    ],
                    "returns": {
                        "description": "A raster data cube containing the computed mean sea surface temperature.",
                        "schema": {
                            "type": "object",
                            "subtype": "raster-cube"
                        }
                    },
                    "exceptions": {
                        "InvalidBboxLengthError": {
                            "message": "Parameter bbox is an array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. Please specify an array with exactly four values."
                        },
                        "InvalidLongitudeValueError": {
                            "message": "Longitude is out of bounds."
                        },
                        "InvalidLatitudeValueError": {
                            "message": "Latitude is out of bounds."
                        },
                        "InvalidTimeframeLengthError": {
                            "message": "Parameter timeframe is an array with two values: [start date, end date]. Please specify an array with exactly two values."
                        },
                        "InvalidTimeframeValueError": {
                            "message": "Timeframe values are strings of the format 'year-month-day'. For example '1981-01-01'. Please specify timeframe values that follow this format."
                        },
                        "ValueError": {
                            "message": "The timeframe values are invalid. Please specify actual dates as start and end date. "
                        }
                    },
                    "links": [
                        {
                            "rel": "about",
                            "href": "https://en.wikipedia.org/wiki/Arithmetic_mean",
                            "title": "Arithmetic mean explained by Wikipedia"
                        },
                        {
                            "rel": "about",
                            "href": "https://en.wikipedia.org/wiki/Sea_surface_temperature",
                            "title": "Sea surface temperature explained by Wikipedia"
                        }
                    ]
                }

            ],

            "links": [
                {
                    "rel": "alternate",
                    "href": "https://provider.com/processes",
                    "type": "text/html",
                    "title": "HTML version of the processes"
                }
            ]
        }  # Todo: Anpassen, Dev Team beauftragen das gleiche für SST zu schreiben, von Dev Team Verifizieren Lassen
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
        for i in Queue:
            data["jobs"].append(i)
        for i in Running:
            data["jobs"].append(i)

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
            resp = Response()
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
    Todo: Queue Implementieren welche Jobs nacheinander Abarbeitet. Fehler antwort senden wenn job bereits Prozessiert wird
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPatch = request.get_json()
    if (version == "v1"):
        if Eval.evalTask(dataFromPatch):
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
        for i in Queue:
            if i["id"] == uuid.UUID(str(id)):
                i["status"] = "created"
                Queue.remove(i)
                Datastore[uuid.UUID(str(id))] = i
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
    if (version == "v1"):
        job = Datastore[uuid.UUID(str(id))]
        job["status"] = "queued"
        Queue.append(job)
        Datastore.pop(uuid.UUID(str(id)))
        # Sende Job An Server
        temp = dict(job)
        temp["id"] = str(job["id"])
        requests.post("http://localhost:442/takeJob", json=temp)
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
    if (version == "v1"):
        data = None
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


@app.route("/data", methods=["POST"])
def postData():
    """
    Custom Route, welche nicht in der OpenEO API Vorgesehen ist. Nimmt die daten der Post request entgegen.
    Todo: Evtl. Verschieben das der Upload nur noch von der Lokalen Maschine aus möglich ist?
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPost = request.get_json()
    r = requests.post("http://localhost:443/data", json=dataFromPost)
    data = r.text
    return data


@app.route("/jobRunning/<uuid:id>", methods=["GET"])
def jobUpdate(id):
    c = 0
    for i in Queue:
        if i["id"] == uuid.UUID(id):
            i["status"] = "running"
            Running.append(i)
            Queue.pop(c)
        c = c + 1

    # Soll status updates in empfang nehmen und einpflegen, Todo: Implementieren


@app.route("/takeData/<uuid:id>", methods=["POST"])
def takeData(id):
    Datastore[id] = request.get_json()
    return Response(status=200)


def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    app.run(debug=True, host="0.0.0.0", port=80)  # Todo: Debug  Ausschalten, Beißt sich  mit Threading


if __name__ == "__main__":
    serverBoot()
