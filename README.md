# GPT RAG Semantic Kernel Model Context Protocol Server
Part of [GPT‑RAG](https://aka.ms/gpt-rag)

The GPT-RAG MCP service deploys an MCP server that is used to enable agentic features in AI Chat Applications. Documentation on the Model Context Protocol can be found here: [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)

Below aree links to the other repos to enable a full chat application solution that leverages this MCP server.
- [GPT-RAG](https://github.com/givenscj/gpt-rag)
- [GPT-RAG-ORCHESTATOR](https://github.com/givenscj/gpt-rag-orchestrator)
- [GPT-RAG-UI](https://github.com/givenscj/gpt-rag-ui)
- [GPT-RAG-INGESTION](https://github.com/givenscj/gpt-rag-ingestion)

## Pre-requistes

- Visual Studio Code
- Azure CLI
- Azure Developer CLI (1.14.100 or lower)
- Git
- Docker/Docker Desktop (for container builds/deployment)

## Currently Available Tools

We have started with a common set of tools that we use for the [GPT-RAG-AGENITC](https://github.com/givenscj/gpt-rag-agentic) strategies, but also added some extras to make things interesting!

- Azure AI Search
- Azure Blob Storage
- Code Interpreter (ACA Session Pools)
- Cosmos
- Document Intelligence
- Remote MCP Servers (such as custom Rest APIs exposed by APIM)
- NL2SQL

## Documentation

- Features
  - [Dynamic Tool Loading](/docs/features/dynamic_tool_loading.md)
- Samples
  - [Custom Tool](/docs/samples/custom_tool.md)
  - [Function Triggers](/docs/samples/function_trigger.md)

## Architecture
Model Context Protocol (MCP) Server

![Model Context Protocol (MCP) Server](media/mcp-server.png "Model Context Protocol (MCP) Server")

Model Context Protocol (MCP) Flow

![Model Context Protocol (MCP) Flow](media/mcp-flow.png "Model Context Protocol (MCP) Flow")


## MCP Tool Configuration

Tools are dynamically loaded using Python runtime instantiation techniques.  The agents and tools that are loaded are driven by the `tool_config.json` file. NOTE: This will be moved to cosmos in the future.


## Full Deployment steps

Run the following commands to provision and deploy the MCP server as a part of the larger [GPT RAG](https://github.com/azure/gpt-rag) solution

### Clone the GPT-RAG repo

```PowerShell
mkdir c:\gpt-rag-deployment
cd c:\gpt-rag-deployment
git clone https://github.com/azure/GPT-RAG
cd GPT-RAG
```

### Provision the resources

- You will need to set the following variables:

```text
azd env set AZURE_USE_MCP true
azd env set USE_CAPP_API_KEY true
```

- And run azd provision:

```PowerShell
azd provision
```
### Set the App Configuration Variables
- Browse to the Azure Portal and your resource group
- Select the App Configuration resource
- Set the basic MCP variables:

```python
AGENT_STRATEGY=mcp
MCP_APP_APIKEY=<your-MCP-API-key> 
AZURE_MCP_SERVER_PORT=80
```
- MCP_APP_APIKEY Can be referenced via key vault
- You may need to restart the replica in azure cotainer app or redeploy orchestrator component for the variable change above to be effective
- Sometimes the App config values can experience a lag after updating. When troubleshooting it may be helpful to temporarily hardcode the agent strategy or the port to ensure that they are updated.

### Deploy Services individually
- cd gpt-rag-orchestrator
- azd deploy (ensure .azure directory is present in root)
- Repeat for gpt-rag-orchestrator, gpt-rag-ui, etc.


## Check Deployment
- By default the wikipedia search tool will deploy. Test the deployment by entering a query into the frontend such as "Summarize the wikipedia article on the Roman Empire"
- Inspect the log stream for the MCP Container and the orchestrator container to ensure that the MCP tools are being invoked.

### Agentic Prompt Example

You can change the Agentic Prompt to guide the agent in its execution of the tools available from the MCP Server.

The prompt currently lives in the the GPT-RAG-AGENTIC code base (soon it will be moved to Cosmos).

A sample prompt for processing a set of documents in a bronze container with document intelligence, then applied an LLM pass to create a JSON document based on a specific schema, then saving to a silver container would look like the following:

```text
You are document processing orchestrator. Using the tools available to you, retrieve documents and process them. 

The processing task steps are: 
	1) Retrieve documents with sas urls from the bronze container using the 'cjg_process_document_bronze' tool.
	2) Pass the retrieved document urls to the 'docInt_process_document_url' tool for processing.
	3) Execute the 'docInt_process_document_text' tool, ensure the schema fields are .
	4) Execute the 'save_document_json' to save the json result as the filename with '.json' appended.
	4) Return the unmodified response from the 'docInt_process_document_text' in the "answer" field.
	5) Summarized your reasoning and put in the "reasoning" field.
	
Using the task steps defined, start with the bronze container and process all files returned.
```

## Testing

- Clone the repo to `c:\github\azure`
- Run the following PowerShell to start the MCP Inspector server locally

```Powershell
npx @modelcontextprotocol/inspector uv --directory c:/github/azure/gpt-rag-mcp run server.py
```

- Create a new virtual environment and install the requirements

```python
python venv .venv
./.venv/scripts/activate.ps1
python -m pip install -r requirements.txt
```

- Using Visual Studio, use the `Run MCP Server` debug option to start the server
