targetScope = 'resourceGroup'

import * as const from 'constants/constants.bicep'

param environmentName string
param location string = resourceGroup().location
param label string = 'gpt-rag'

@description('Principal ID for role assignments. This is typically the Object ID of the user or service principal running the deployment.')
param principalId string

@description('Principal type for role assignments. This can be "User", "ServicePrincipal", or "Group".')
param principalType string = 'User'

@description('Tags to apply to all resources in the deployment')
param deploymentTags object = {}

param useUAI bool = true

var _containerDummyImageName string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
var resourceToken string = toLower(uniqueString(subscription().id, environmentName, location))

//get existing app config
resource appconfig 'Microsoft.AppConfiguration/configurationStores@2024-06-15-preview' existing = {
  name: '${const.abbrs.configuration.appConfiguration}${resourceToken}'
  
}

var appKeys = [
  {
    key: 'MCP_APP_APIKEY'
    value: resourceToken
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_PORT'
    value: 80
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_TIMEOUT'
    value: 600
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_MODE'
    value: 'fastapi'
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_TRANSPORT'
    value: 'sse'
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_HOST'
    value: ''
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_ENABLE_AUTH'
    value: true
    contentType: 'text/plain'
  }
  {
    key: 'AZURE_MCP_SERVER_JSON'
    value: true
    contentType: 'text/plain'
  }
  {
    key: 'USE_CODE_INTERPRETER'
    value: false
    contentType: 'text/plain'
  }
  {
    key: 'POOL_MANAGEMENT_ENDPOINT'
    value: 'https://dynamicsessions.io'
    contentType: 'text/plain'
  }
]

//add app config key
resource appconfigKey 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-06-15-preview' = [for key in appKeys: {
  name: '${appconfig.name}/${key.key}'
  properties: {
    value: key.value
    contentType: key.contentType
    tags: {
      label: label
    }
  }
}
]

//add cosmos db account
resource cosmosDBAccount 'Microsoft.DocumentDB/databaseAccounts@2025-05-01-preview' existing = {
  name: '${const.abbrs.databases.cosmosDBDatabase}${resourceToken}'
}

//get the cosmos database
resource cosmosDBDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2025-05-01-preview' existing = {
  name: '${const.abbrs.databases.cosmosDBDatabase}db${resourceToken}'
  parent: cosmosDBAccount
}

//add cosmos container - mcp
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2025-05-01-preview' = {
  name: 'mcp'
  parent: cosmosDBDatabase
  properties: {
    resource: {
      id: 'mcp'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

//get the azure container apps service
resource containerEnv 'Microsoft.App/managedEnvironments@2025-02-02-preview' existing = {
  name: '${const.abbrs.containers.containerAppsEnvironment}${resourceToken}'
}


//MCP ACA User Managed Identity
module mcpAcaUAI 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${const.abbrs.security.managedIdentity}${const.abbrs.containers.containerApp}${resourceToken}-mcp'
  params: {
    // Required parameters
    name: '${const.abbrs.security.managedIdentity}${const.abbrs.containers.containerApp}${resourceToken}-mcp'
    // Non-required parameters
    location: location
  }
}

module containerApps 'br/public:avm/res/app/container-app:0.17.0' = {
  name: '${const.abbrs.containers.containerApp}${resourceToken}-mcp'
  params: {
    name: '${const.abbrs.containers.containerApp}${resourceToken}-mcp'
    location:              location
    environmentResourceId: containerEnv.id

    ingressExternal:       true
    ingressTargetPort:     80
    ingressTransport:      'auto'
    ingressAllowInsecure:  false

    dapr: {
      enabled:     true
      appId:       'mcp'
      appPort:     80
      appProtocol: 'http'
    }

    managedIdentities: {
      systemAssigned: (useUAI) ? false : true
      userAssignedResourceIds: (useUAI) ? [mcpAcaUAI.outputs.resourceId] : []
    }

    scaleSettings: {
      minReplicas: 1
      maxReplicas: 1
    }
    
    containers: [
      {
        name:     'mcp'
        image:    _containerDummyImageName
        resources: {
          cpu:    '0.5'
          memory: '1.0Gi'
        }
        env: [
          {
            name:  'APP_CONFIG_ENDPOINT'
            value: 'https://${appconfig.name}.azconfig.io'
          }
          {
            name:  'AZURE_TENANT_ID'
            value: subscription().tenantId
          }
          {
            name:  'AZURE_CLIENT_ID'
            value: useUAI ? mcpAcaUAI.outputs.clientId : ''
          }
        ]
      }
    ]

    tags: {
      'azd-service-name': 'mcp'
    }
  }
}

// Cosmos DB Account - Cosmos DB Built-in Data Contributor -> Executor
module assignCosmosDBCosmosDbBuiltInDataContributorExecutor 'modules/security/cosmos-data-plane-role-assignment.bicep' = {
  name: 'assignCosmosDBCosmosDbBuiltInDataContributorExecutor'
  params: {
    #disable-next-line BCP318
    cosmosDbAccountName: cosmosDBAccount.name
    principalId: useUAI ? mcpAcaUAI.outputs.clientId : containerApps.outputs.systemAssignedMIPrincipalId
    roleDefinitionGuid: const.roles.CosmosDBBuiltInDataContributor.guid
    scopePath: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${const.abbrs.databases.cosmosDBDatabase}${resourceToken}/dbs/${const.abbrs.databases.cosmosDBDatabase}db${resourceToken}'
  }
}
