# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(blueprint) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints

import requests
import azure.functions as func
import logging

from configuration import Configuration
config = Configuration()

def main(inputBlob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {inputBlob.name}"
                f"Blob Size: {inputBlob.length} bytes")
    
    #call the orchestrator function
    post = {
        "name": inputBlob.name,
        "size": inputBlob.length,
        "data": inputBlob.read()
    }

    # Send the blob data to the orchestrator function
    orchestrator_url = config.get_value("ORCHESTRATOR_ENDPOINT")
    function_key = config.get_value("AZURE_ORCHESTRATOR_FUNC_KEY")

    if function_key:
        headers = {
            "x-functions-key": function_key
        }

    response = requests.post(orchestrator_url, json=post)
    logging.info(f"Response from orchestrator: {response.status_code}")