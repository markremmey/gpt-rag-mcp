# GPT RAG Semantic Kernel Model Context Protocol Server

Welcome to the GPT-RAG Model Context Protocol (MCP) Server for the GPT-RAG series of repos. Note these currently point at the `givenscj` fork due to some reorganizing of the repos. The original repos are available in the `azure` organization, but will not currenlty work with the MCP server.

- [GPT-RAG](https://github.com/givenscj/gpt-rag)
- [GPT-RAG-AGENTIC](https://github.com/givenscj/gpt-rag-agentic)
- [GPT-RAG-ORCHESTATOR](https://github.com/givenscj/gpt-rag-orchestrator)
- [GPT-RAG-FRONTEND](https://github.com/givenscj/gpt-rag-frontend)
- [GPT-RAG-UI](https://github.com/givenscj/gpt-rag-ui)
- [GPT-RAG-INGESTION](https://github.com/givenscj/gpt-rag-ingestion)

This code enables the exposing of tools, prompts and resources to the [GPT-RAG-AGENITC](https://github.com/givenscj/gpt-rag-agentic) orchestrator and can be deployed as a Web App, ACA Container or AKS deployment.

## Currently Available Tools

We have started with a common set of tools that we use for the [GPT-RAG-AGENITC](https://github.com/givenscj/gpt-rag-agentic) strategies, but also added some extras to make things interesting!

- Azure AI Search
- Azure Blob Storage
- Code Interpreter (ACA Session Pools)
- Cosmos
- Document Intelligence
- Remote MCP Servers (such as custom Rest APIs exposed by APIM)
- NL2SQL

## Future Tools

- Databricks
- Fabric
- Office Documents (Excel/Word/PowerPoint)
- Rest APIs
- SharePoint

## Testing

- Clone the repo to `c:\github\azure`
- Run the following PowerShell to start the MCP Inspector server locally

```Powershell
npx @modelcontextprotocol/inspector uv --directory c:/github/azure/gpt-rag-mcp run server.py
```

- Using Visual Studio, use the `Run MCP Server` debug option to start the server

## Configuration

Tools are dynamically loaded using Python runtime instantiation techniques.  The agents and tools that are loaded are driven by the `tool_config.json` file. NOTE: This will be moved to cosmos in the future.

## Deployment

By default, GPT-RAG-MCP expects a landing zone to be in place for deployment.  This landing zone is driven by the GPT-RAG repo's bicep files.  Once you have deployed the landing zone using the `AZURE_USE_MCP=true` as an AZD ENV Variable, you will have the necessary resource to perform the following:

- Open a Visual Studio Code terminal
- Run the following:

```powershell
azd deploy mcpServer
```

The code will be packaged and deployed to the App Service with the tag `azd-service:mcpServer`

From there, you can interact with the MCP server over `SSE` via the `https:\\webappname.azurewebsites.net\sse` endpoint using the MCP inspector you have running from the commands above.
