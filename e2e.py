import requests
import json
#import testjob.json

def getData():
    requests.get("http://0.0.0.0:8080/api/v1/jobs")
   # requests.post("http://0.0.0.0:8080/api/v1/jobs", json=testjob.json, headers={"Content-Type": "application/json"})
    
    
testjob = {
  "title": "Example Title",
  "description": "Example Description",
  "process": {
    "process_graph": {
      "loadcollection1": {
        "process_id": "load_collection",
        "arguments": {
          "timeframe" : ["01-12-1981 00:00:00","30-12-1981 00:00:00","%d-%m-%Y %H:%M:%S"],
          "DataType": "SST"
        }
        },
        "SST": {
        "process_id": "mean_sst",
        "arguments": {
          "data":{
              "from_node": "loadcollection1"
          },
          "timeframe":["1981-12-01","1981-12-17"],
          "bbox":[-999,-999,-999,-999]
          }
        },
        "save":{
            "process_id": "save_result",
            "arguments":{
                "SaveData":{
                    "from_node":"SST"
                },
                "Format": "netcdf"
            }
        }
      }
      }
    }   

print(testjob)
