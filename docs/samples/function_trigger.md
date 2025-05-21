# Function Triggers (Blob, Queue, EventHub, etc)

This example shows how to utilize a function based event to start an MCP process.

## Create the Function App

Create a new function app to call your MCP tool.

- Create a new folder (ex: c:\github\function_trigger)
- Open Visual Studio Code to the new folder
- In a terminal window, run the following:

```powershell
func TODO
```

- Update the function code to the following:

```python
TODO
```

## Create the Custom Tool

Follow the instructions in [custom_tool.md](custom_tool.md) to create a custom tool with function entry points.  This will also show you how to add the tool to the MCP server and how to deploy the server.

## Test the custom tool

- Execute the following code to add a message to the storage queue.
- Wait for the function to return the echo message based on the queue message.

## Customize

- Create another custom plugin (`tools/custom/customer_name_plugin.py`), add your semantic kernel decorated methods.
- Replace the call to the Echo tool with a call to your plugin.
- Again, run the code to add a queue message, watch the magic happen!

Enjoy your journey with MCP!
