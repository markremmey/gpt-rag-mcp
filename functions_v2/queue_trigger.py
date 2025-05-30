import azure.functions as func
import json
    
bp03 = func.Blueprint()

@bp03.queue_trigger(arg_name="req", queue_name="queue01", connection="AzureWebJobsStorage")
def method02(req:func.QueueMessage):
    pass