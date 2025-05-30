import requests
import azure.functions as func
import logging

from configuration import Configuration
config = Configuration()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        post = req.get_json()
    except ValueError:
        pass

    # Send the blob data to the orchestrator function
    orchestrator_url = config.get_value("ORCHESTRATOR_ENDPOINT")
    function_key = config.get_value("AZURE_ORCHESTRATOR_FUNC_KEY")

    if function_key:
        headers = {
            "x-functions-key": function_key
        }
    
    logging.info(f"Calling orchestrator: {orchestrator_url}")
    response = requests.post(orchestrator_url, json=post, headers=headers)
    logging.info(f"Response from orchestrator: {response.status_code}")

    return func.HttpResponse(
            response.content,
            status_code=200
    )