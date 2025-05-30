import azure.functions as func
import json
    
bp02 = func.Blueprint()

@bp02.blob_trigger(arg_name="req", path="container01/{name}", connection="AzureWebJobsStorage", data_type=func.DataType.BINARY)
def method03(req:func.InputStream):
    pass