targetScope = 'resourceGroup'

@description('Azure region for all regional resources. Restricted to Australian regions for PROTECTED residency.')
@allowed([
  'australiaeast'
  'australiasoutheast'
  'australiacentral'
  'australiacentral2'
])
param location string = 'australiaeast'

@description('Name of the Azure Log Analytics workspace hosting Microsoft Sentinel.')
@minLength(4)
@maxLength(63)
param workspaceName string = 'law-sentinel-protected'

@description('Interactive Analytics retention in days. Minimum 90 days (included with Microsoft Sentinel). Configure total retention to 365+ days in the Sentinel data lake or archive for ISM-1988.')
@minValue(90)
@maxValue(730)
param retentionInDays int = 90

@description('Optional daily ingestion cap in GB. Set to -1 for unlimited ingestion.')
param dailyQuotaGb int = -1

@description('Control public network ingestion to the Log Analytics workspace. Disabled enforces Azure Monitor Private Link Scope.')
@allowed([
  'Disabled'
  'Enabled'
])
param publicNetworkAccessForIngestion string = 'Disabled'

@description('Control public network queries to the Log Analytics workspace. Disabled enforces private endpoint query access.')
@allowed([
  'Disabled'
  'Enabled'
])
param publicNetworkAccessForQuery string = 'Disabled'

@description('Deploy the security hub Virtual Network, Private DNS zones, AMPLS, Data Collection Endpoint and Private Endpoint.')
param deployPrivateLink bool = true

@description('Name of the Virtual Network hosting the AMPLS Private Endpoint.')
param vnetName string = 'vnet-secops-protected'

@description('Address prefix for the security hub Virtual Network.')
param vnetAddressPrefix string = '10.60.0.0/22'

@description('Address prefix for the Private Endpoints subnet.')
param privateEndpointSubnetPrefix string = '10.60.1.0/26'

@description('Name of the Azure Monitor Private Link Scope (AMPLS).')
param amplsName string = 'ampls-sentinel-protected'

@description('Name of the Data Collection Endpoint (DCE) for private AMA ingestion.')
param dceName string = 'dce-sentinel-protected'

@description('Apply a CanNotDelete resource lock to the Log Analytics workspace (supports ISM-1815).')
param enableDeleteLock bool = true

@description('Enable diagnostic settings auditing Log Analytics workspace operations.')
param enableDiagnosticSettings bool = true

@description('Optional Entra ID security group object ID assigned Microsoft Sentinel Reader on the workspace. Leave empty to skip.')
param sentinelReaderGroupObjectId string = ''

@description('Optional Entra ID security group object ID assigned Microsoft Sentinel Responder on the workspace. Leave empty to skip.')
param sentinelResponderGroupObjectId string = ''

@description('Optional Entra ID security group object ID assigned Microsoft Sentinel Contributor on the workspace. Leave empty to skip.')
param sentinelContributorGroupObjectId string = ''

@description('Tags applied to deployed resources.')
param tags object = {
  classification: 'PROTECTED'
  workload: 'microsoft-sentinel'
  managedBy: 'bicep'
}

// Built-in Azure RBAC role definition IDs:
// https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security
var sentinelReaderRoleId = '8d289c81-5878-46d4-8554-54e1e3d8b5cb'
var sentinelResponderRoleId = '3e150937-b8fe-4cfb-8069-0eaf05ecd056'
var sentinelContributorRoleId = 'ab8e14d6-4a74-4a29-9ba8-549422addade'

var privateDnsZoneNames = [
  'privatelink.monitor.azure.com'
  'privatelink.oms.opinsights.azure.com'
  'privatelink.ods.opinsights.azure.com'
  'privatelink.agentsvc.azure-automation.net'
]

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
    workspaceCapping: {
      dailyQuotaGb: dailyQuotaGb
    }
    publicNetworkAccessForIngestion: publicNetworkAccessForIngestion
    publicNetworkAccessForQuery: publicNetworkAccessForQuery
    features: {
      disableLocalAuth: true
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource sentinelOnboarding 'Microsoft.SecurityInsights/onboardingStates@2024-03-01' = {
  scope: workspace
  name: 'default'
  properties: {
    customerManagedKey: false
  }
}

resource workspaceDeleteLock 'Microsoft.Authorization/locks@2020-05-01' = if (enableDeleteLock) {
  scope: workspace
  name: '${workspaceName}-cannot-delete'
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects PROTECTED security event logs from unauthorised deletion (ISM-1815).'
  }
}

resource workspaceDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnosticSettings) {
  scope: workspace
  name: 'audit-to-workspace'
  properties: {
    workspaceId: workspace.id
    logs: [
      {
        categoryGroup: 'audit'
        enabled: true
      }
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' = if (deployPrivateLink) {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-private-endpoints'
        properties: {
          addressPrefix: privateEndpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

resource privateDnsZones 'Microsoft.Network/privateDnsZones@2024-06-01' = [
  for zoneName in privateDnsZoneNames: if (deployPrivateLink) {
    name: zoneName
    location: 'global'
    tags: tags
  }
]

resource privateDnsZoneLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [
  for (zoneName, i) in privateDnsZoneNames: if (deployPrivateLink) {
    parent: privateDnsZones[i]
    name: '${vnetName}-link'
    location: 'global'
    tags: tags
    properties: {
      virtualNetwork: {
        id: vnet.id
      }
      registrationEnabled: false
    }
  }
]

resource ampls 'Microsoft.Insights/privateLinkScopes@2021-07-01-preview' = if (deployPrivateLink) {
  name: amplsName
  location: 'global'
  tags: tags
  properties: {
    accessModeSettings: {
      ingestionAccessMode: publicNetworkAccessForIngestion == 'Disabled' ? 'PrivateOnly' : 'Open'
      queryAccessMode: publicNetworkAccessForQuery == 'Disabled' ? 'PrivateOnly' : 'Open'
    }
  }
}

resource dce 'Microsoft.Insights/dataCollectionEndpoints@2023-03-11' = if (deployPrivateLink) {
  name: dceName
  location: location
  tags: tags
  properties: {
    networkAcls: {
      publicNetworkAccess: publicNetworkAccessForIngestion
    }
  }
}

resource amplsScopedWorkspace 'Microsoft.Insights/privateLinkScopes/scopedResources@2021-07-01-preview' = if (deployPrivateLink) {
  parent: ampls
  name: '${workspaceName}-scoped'
  properties: {
    linkedResourceId: workspace.id
  }
}

resource amplsScopedDce 'Microsoft.Insights/privateLinkScopes/scopedResources@2021-07-01-preview' = if (deployPrivateLink) {
  parent: ampls
  name: '${dceName}-scoped'
  properties: {
    linkedResourceId: dce.id
  }
}

resource amplsPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-01-01' = if (deployPrivateLink) {
  name: 'pe-${amplsName}'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: vnet!.properties.subnets[0].id
    }
    privateLinkServiceConnections: [
      {
        name: 'plsc-${amplsName}'
        properties: {
          privateLinkServiceId: ampls.id
          groupIds: [
            'azuremonitor'
          ]
        }
      }
    ]
  }
}

resource amplsPrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-01-01' = if (deployPrivateLink) {
  parent: amplsPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      for (zoneName, i) in privateDnsZoneNames: {
        name: replace(zoneName, '.', '-')
        properties: {
          privateDnsZoneId: privateDnsZones[i].id
        }
      }
    ]
  }
}

resource sentinelReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(sentinelReaderGroupObjectId)) {
  scope: workspace
  name: guid(workspace.id, sentinelReaderGroupObjectId, sentinelReaderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', sentinelReaderRoleId)
    principalId: sentinelReaderGroupObjectId
    principalType: 'Group'
    description: 'Least-privilege Microsoft Sentinel Reader access for SOC triage analysts.'
  }
}

resource sentinelResponderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(sentinelResponderGroupObjectId)) {
  scope: workspace
  name: guid(workspace.id, sentinelResponderGroupObjectId, sentinelResponderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', sentinelResponderRoleId)
    principalId: sentinelResponderGroupObjectId
    principalType: 'Group'
    description: 'Microsoft Sentinel Responder access for incident investigation and response.'
  }
}

resource sentinelContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(sentinelContributorGroupObjectId)) {
  scope: workspace
  name: guid(workspace.id, sentinelContributorGroupObjectId, sentinelContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', sentinelContributorRoleId)
    principalId: sentinelContributorGroupObjectId
    principalType: 'Group'
    description: 'Microsoft Sentinel Contributor access for PIM-eligible detection engineers.'
  }
}

@description('Resource ID of the deployed Log Analytics workspace.')
output workspaceResourceId string = workspace.id

@description('Customer ID (GUID) of the deployed Log Analytics workspace.')
output workspaceCustomerId string = workspace.properties.customerId

@description('Resource ID of the Microsoft Sentinel onboarding state.')
output sentinelOnboardingStateId string = sentinelOnboarding.id

@description('Resource ID of the Azure Monitor Private Link Scope, when deployed.')
output amplsResourceId string = deployPrivateLink ? ampls.id : ''

@description('Resource ID of the Data Collection Endpoint, when deployed.')
output dceResourceId string = deployPrivateLink ? dce.id : ''
