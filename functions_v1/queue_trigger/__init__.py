import json
import requests
import azure.functions as func
import logging

from configuration import Configuration
config = Configuration()

def main(msg: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                msg.get_body().decode('utf-8'))

    try:
        post = json.loads(msg.get_body().decode('utf-8'))
    except ValueError:
        pass

    # Send the blob data to the orchestrator function
    orchestrator_url = config.get_value("ORCHESTRATOR_ENDPOINT")
    function_key = config.get_value("AZURE_ORCHESTRATOR_FUNC_KEY")

    if function_key:
        headers = {
            "x-functions-key": function_key
        }
        
    response = requests.post(orchestrator_url, json=post)
    logging.info(f"Response from orchestrator: {response.status_code}")

    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
    )