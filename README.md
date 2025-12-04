## Deploy MCP Server to Azure Container Apps (HTTP Streamable)

This repo enables you to deploy an MCP Server in an Azure Container App using the [Streamable HTTP Protocol](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#streamable-http).

### Azure Portal Deployment

#### Pre-Requisites

1. Create an Azure Container Registry
2. Create an Azure Container App Environment and Azure Container App
3. Push Container to Azure Container Registry (scripts/pushContainer.sh)

#### Start MCP Model Inspector
```bash
npx @modelcontextprotocol/inspector
```

