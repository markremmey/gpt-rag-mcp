import azure.functions as func 
from http_trigger import bp01
from blob_trigger import bp02
from queue_trigger import bp03

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) 

app.register_functions(bp01)
app.register_functions(bp02)
app.register_functions(bp03)