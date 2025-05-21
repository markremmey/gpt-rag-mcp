# Custom Tools in GPT-RAG-MCP

The GPT-RAG-MCP provides several out of box tools for common Azure based operations.  However, it is very likely you will want to build your own tools for your agents to call.

## Create a new tool

Use the following steps to create a new custom tool:

- In the `tools` folder, add a new `custom` folder
- Create a new Python file called `echo_plugin.py`
- Add the following code to the tool:

```python
from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

class EchoPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize the Echo Plugin with the provided settings.
        """
        super().__init__(settings)

    @kernel_function(
        name="echo_tool",
        description="Echos the input provided.",
    )
    async def echo(self, echo_message : str) -> str:
        return f"[echo] {echo_message}"
```

- Notice the following:
  - The tool inherits from `BasePlugin`.
  - The tool accepts a Dict object called settings.
  - One of the inputs of the settings dictionary with be a `config` key that is an Application Configuration object which will allow you access to Application Configuration key/values (and backing key vault values).

- OPTIONAL:  Modify the functions/methods in the tool to add your own functions.  All function must be decorated with the `kernel_function` decorator:

```python
@kernel_function(
    name="echo_tool",
    description="Echos the input provided.",
)
```

- Update the `tool_config.json` to load your tool:

```json
{
    "name": "EchoPlugin", //name of the plugin for semantic kernel - this must be unique or later names will overwrite
    "module": "tools.custom.echo_plugin",  //path to the python file that contains the plugin
    "class": "EchoPlugin",  //name of the class in the python file
    "enabled": true,  //if the tools should be loaded or not
    "settings": {
        "prefix": "",  //This will add a prefix to all semantic kernel functions (at instansiation)
        "suffix": "",   //This will add a suffix to all semantic kernel functions (at instansiation)
        "echo_tool_description" : "" //Allows you to override the function description - format is '{FUNCTION_NAME}_description'
    }
}
```

> NOTE: Reference the [Dynamic Tool Loading](dynamic_tool_loading.md) documentation for how dynamic tool loading works.

- Dedeploy the MCP Server:

```powershell
azd deploy mcpServer
```

> NOTE: You can also manually deploy, but you will need to delete or rename the `azure.yaml` file to get the old style function deployment options in Visual Studio Code.
