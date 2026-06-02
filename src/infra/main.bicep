// InboxIQ — Azure Bicep IaC
// Provisions: AI Foundry, OpenAI, Cosmos DB, Container Apps, Speech, Key Vault

param location string = resourceGroup().location
param prefix string = 'inboxiq'

resource aoai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${prefix}-aoai'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: { customSubDomainName: '${prefix}-aoai' }
}

resource foundryHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: '${prefix}-foundry'
  location: location
  kind: 'Hub'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'InboxIQ Foundry Hub'
    publicNetworkAccess: 'Enabled'
  }
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-08-15' = {
  name: '${prefix}-cosmos'
  location: location
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [{ locationName: location }]
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
  }
}

resource speech 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${prefix}-speech'
  location: location
  kind: 'SpeechServices'
  sku: { name: 'S0' }
}

resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-cae'
  location: location
  properties: {}
}

output aoaiEndpoint string = aoai.properties.endpoint
output cosmosEndpoint string = cosmos.properties.documentEndpoint
