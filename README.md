# GPT RAG Semantic Kernel Model Context Protocol Server
Part of [GPT‑RAG](https://aka.ms/gpt-rag)

The GPT-RAG MCP service deploys an MCP server that is used to enable agentic features in AI Chat Applications. Documentation on the Model Context Protocol can be found here: [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)

## Documentation

- Features
  - [Dynamic Tool Loading](/docs/features/dynamic_tool_loading.md)
- Samples
  - [Custom Tool](/docs/samples/custom_tool.md)
  - [Function Triggers](/docs/samples/function_trigger.md)

## Prerequisites

Before deploying the application, you must provision the infrastructure as described in the [GPT-RAG](https://github.com/azure/gpt-rag) repo. This includes creating all necessary Azure resources required to support the application runtime.

<details markdown="block">
<summary>Click to view <strong>software</strong> prerequisites</summary>
<br>
The machine used to customize and or deploy the service should have:

* Azure CLI: [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
* Azure Developer CLI (optional, if using azd): [Install azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
* Git: [Download Git](https://git-scm.com/downloads)
* Python 3.12: [Download Python 3.12](https://www.python.org/downloads/release/python-3120/)
* Docker CLI: [Install Docker](https://docs.docker.com/get-docker/)
* VS Code (recommended): [Download VS Code](https://code.visualstudio.com/download)
</details>

### Deploying the app with azd (recommended)

##### Set the required App Configuration Variables in Azure Portal
- Browse to the Azure Portal and your resource group
- Select the App Configuration resource
- Set the basic MCP variables:

```python
AGENT_STRATEGY=mcp
MCP_APP_APIKEY=<your-MCP-API-key> 
AZURE_MCP_SERVER_PORT=80
```
- MCP_APP_APIKEY Can be referenced via key vault
- You may need to restart the replica in azure container app or redeploy orchestrator component for the variable change above to be effective
- Sometimes the App config values can experience a lag after updating. When troubleshooting it may be helpful to temporarily hardcode the agent strategy or the port to ensure that they are updated.



##### Initialize the template:
```shell
azd init -t azure/gpt-rag-mcp
```
> [!IMPORTANT]
> Use the **same environment name** with `azd init` as in the infrastructure deployment to keep components consistent.

Update env variables then deploy:
```shell
azd env refresh
azd deploy 
```
> [!IMPORTANT]
> Run `azd env refresh` with the **same subscription** and **resource group** used in the infrastructure deployment.

- You will need to set the following variables:
```text
azd env set AZURE_USE_MCP true
azd env set USE_CAPP_API_KEY true
```

### Deploying the app with a shell script

To deploy using a script, first clone the repository, set the App Configuration endpoint, and then run the deployment script.

##### PowerShell (Windows)
- Ensure you have set the appropriate App Configuration values (see instructions above)
- You will need to set the following variables:
```text
azd env set AZURE_USE_MCP true
azd env set USE_CAPP_API_KEY true
```


```powershell
git clone https://github.com/Azure/gpt-rag-mcp.git
$env:APP_CONFIG_ENDPOINT = "https://<your-app-config-name>.azconfig.io"
cd gpt-rag-mcp
.\scripts\deploy.ps1
```

## MCP Tool Configuration

Tools are dynamically loaded using Python runtime instantiation techniques.  The agents and tools that are loaded are driven by the `tool_config.json` file. NOTE: This will be moved to cosmos in the future.

## Check Deployment
- By default the wikipedia search tool will deploy. Test the deployment by entering a query into the frontend such as "Summarize the wikipedia article on the Roman Empire"
- Inspect the log stream for the MCP Container and the orchestrator container to ensure that the MCP tools are being invoked.


## Testing using MCP Inspector 
MCP Inspector is a tool to test MCP servers using a standard client tool. Find documentation here: [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)

Local Deployment Steps
- Create and activate the python virtual environment
```python
python -m venv .venv
./.venv/scripts/activate.ps1
python -m pip install -r requirements.txt
```
- Run the following PowerShell to start the MCP Inspector server locally
```Powershell
cd gpt-rag-mcp
npx @modelcontextprotocol/inspector uv run server.py
```

- The script will display a session token
- Open the link https://localhost:6274
- Paste the session token under "Configuration"
- Add the deployed MCP Server URI (e.g. https://<mcp-container-app-name>.westus3.azurecontainerapps.io/sse)
- Add Authentication header: set X-API-KEY equal to the MCP API Key found in your key vault
- Click Connect to view the MCP tools available
