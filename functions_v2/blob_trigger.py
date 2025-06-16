import azure.functions as func
import json

from configuration import Configuration

config = Configuration()

NEXT_STAGE = config.get_value("NEXT_STAGE")

    
bp02 = func.Blueprint()

@bp02.function_name(name="ai_doc_blob_trigger")
@bp02.blob_trigger(arg_name="req", path=f'{config.get_value("AI_DOC_PROC_CONTAINER_NAME","bronze")}/{{name}}', connection=config.get_value("AI_DOC_PROC_CONNECTION_NAME","AzureWebJobsStorage"), data_type=func.DataType.BINARY)
def method03(req:func.InputStream):
    pass