# Sample Bicep: Core PROTECTED Microsoft Sentinel Deployment

This sample Bicep template deploys the core Azure infrastructure for a single-agency Australian PROTECTED Microsoft Sentinel deployment in **Australia East** (with optional selection of Australia Southeast, Australia Central or Australia Central 2).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjusso-dev%2Fmicrosoft-security-protected-architectures%2Fmain%2Fiac%2Fbicep%2Fazuredeploy.json)

> **Disclaimer:** This is a community sample for reference and testing only. It is not produced, endorsed or supported by ASD, ACSC or Microsoft. Never deploy directly to a production tenant without reviewing against your agency's security risk assessment, network architecture and current ISM release. All sample parameter values use placeholder GUIDs.

## Resources deployed

- **Azure Log Analytics workspace** (`PerGB2018`, `disableLocalAuth: true`, resource-context RBAC enforced, minimum 90 days Analytics interactive retention)
- **Microsoft Sentinel onboarding state** (`Microsoft.SecurityInsights/onboardingStates`)
- **CanNotDelete resource lock** on the Log Analytics workspace (supports `ISM-1815`)
- **Workspace diagnostic settings** sending `audit` and `allLogs` categories to the workspace (supports `ISM-1985`)
- **Private Link networking** (when `deployPrivateLink` is `true`):
  - Hub Virtual Network with a dedicated Private Endpoints subnet
  - Private DNS Zones (`privatelink.monitor.azure.com`, `privatelink.oms.opinsights.azure.com`, `privatelink.ods.opinsights.azure.com`, `privatelink.agentsvc.azure-automation.net`) linked to the VNet
  - **Azure Monitor Private Link Scope (AMPLS)** scoped to the workspace and DCE
  - **Data Collection Endpoint (DCE)** for private Azure Monitor Agent ingestion
  - Private Endpoint and Private DNS Zone Group
- **Least-privilege Azure RBAC assignments** (optional, skipped when group object IDs are empty) using official [Azure built-in security roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security):
  - `Microsoft Sentinel Reader` (`8d289c81-5878-46d4-8554-54e1e3d8b5cb`)
  - `Microsoft Sentinel Responder` (`3e150937-b8fe-4cfb-8069-0eaf05ecd056`)
  - `Microsoft Sentinel Contributor` (`ab8e14d6-4a74-4a29-9ba8-549422addade`)

## Parameters

| Parameter | Type | Default | Allowed values | Description |
| :--- | :--- | :--- | :--- | :--- |
| `location` | `string` | `australiaeast` | `australiaeast`, `australiasoutheast`, `australiacentral`, `australiacentral2` | Target Australian Azure region for regional resources. |
| `workspaceName` | `string` | `law-sentinel-protected` | 4 to 63 chars | Name of the Log Analytics workspace hosting Microsoft Sentinel. |
| `retentionInDays` | `int` | `90` | 90 to 730 | Interactive Analytics retention in days. Configure 365+ days total retention in the Sentinel data lake or archive for `ISM-1988`. |
| `dailyQuotaGb` | `int` | `-1` | Integer (`-1` unlimited) | Optional daily ingestion cap in GB. |
| `publicNetworkAccessForIngestion` | `string` | `Disabled` | `Disabled`, `Enabled` | Controls public network ingestion to the workspace and DCE. |
| `publicNetworkAccessForQuery` | `string` | `Disabled` | `Disabled`, `Enabled` | Controls public network query access to the workspace. |
| `deployPrivateLink` | `bool` | `true` | `true`, `false` | Deploys VNet, Private DNS zones, AMPLS, DCE and Private Endpoint. |
| `vnetName` | `string` | `vnet-secops-protected` | String | Name of the hub Virtual Network. |
| `vnetAddressPrefix` | `string` | `10.60.0.0/22` | CIDR | Address prefix for the hub Virtual Network. |
| `privateEndpointSubnetPrefix` | `string` | `10.60.1.0/26` | CIDR | Address prefix for the Private Endpoints subnet. |
| `amplsName` | `string` | `ampls-sentinel-protected` | String | Name of the Azure Monitor Private Link Scope. |
| `dceName` | `string` | `dce-sentinel-protected` | String | Name of the Data Collection Endpoint. |
| `enableDeleteLock` | `bool` | `true` | `true`, `false` | Applies a `CanNotDelete` lock to the Log Analytics workspace. |
| `enableDiagnosticSettings` | `bool` | `true` | `true`, `false` | Enables workspace audit diagnostic settings. |
| `sentinelReaderGroupObjectId` | `string` | `''` | Entra group GUID or empty | Entra ID security group object ID granted `Microsoft Sentinel Reader`. |
| `sentinelResponderGroupObjectId` | `string` | `''` | Entra group GUID or empty | Entra ID security group object ID granted `Microsoft Sentinel Responder`. |
| `sentinelContributorGroupObjectId` | `string` | `''` | Entra group GUID or empty | Entra ID security group object ID granted `Microsoft Sentinel Contributor`. |
| `tags` | `object` | `{ classification: 'PROTECTED', ... }` | Key-value object | Resource tags applied across deployed resources. |

## Outputs

| Output | Description |
| :--- | :--- |
| `workspaceResourceId` | Full Azure Resource ID of the Log Analytics workspace |
| `workspaceCustomerId` | Log Analytics workspace Customer ID (GUID) |
| `sentinelOnboardingStateId` | Resource ID of the Microsoft Sentinel onboarding state |
| `amplsResourceId` | Resource ID of the AMPLS (empty if `deployPrivateLink` is `false`) |
| `dceResourceId` | Resource ID of the Data Collection Endpoint (empty if `deployPrivateLink` is `false`) |

## Build and deploy

Validate and compile locally without connecting to an Azure tenant:

```bash
az bicep build --file iac/bicep/main.bicep --outfile iac/bicep/azuredeploy.json
```

Preview and deploy to a non-production resource group (replacing placeholder group IDs in `main.bicepparam` first):

```bash
az group create --name rg-sentinel-protected-dev --location australiaeast
az deployment group what-if \
  --resource-group rg-sentinel-protected-dev \
  --template-file iac/bicep/main.bicep \
  --parameters iac/bicep/main.bicepparam
```

After deploying the core workspace, onboard Microsoft Sentinel to the Microsoft Defender portal and configure the Microsoft Sentinel data lake and 365+ day table retention as described in [ADR-0002](../../adr/0002-retention-analytics-tier-and-data-lake.md) and [ADR-0003](../../adr/0003-defender-xdr-integration-and-unified-soc-platform.md).

## Related references

- [Deploy Microsoft Sentinel using Bicep](https://learn.microsoft.com/en-us/azure/sentinel/quickstart-onboard)
- [Design your Azure Monitor Private Link configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/private-link-design)
- [Azure built-in security roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security)
- [Reference architecture: single agency at PROTECTED](../../architectures/single-agency-protected.md)
