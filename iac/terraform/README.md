# Sample Terraform: Core PROTECTED Microsoft Sentinel Deployment

This Terraform configuration is the functional equivalent of the [Bicep sample](../bicep/README.md). It deploys a Log Analytics workspace with Microsoft Sentinel in **Australia East** (restricted to Australian Azure regions), Azure Monitor Private Link Scope (AMPLS), Data Collection Endpoint (DCE), Private DNS zones, diagnostic settings, a `CanNotDelete` management lock and least-privilege Sentinel RBAC assignments.

> **Disclaimer:** This is a community sample for reference and testing only. It is not produced, endorsed or supported by ASD, ACSC or Microsoft. Never apply directly to a production tenant without reviewing against your agency's security risk assessment, network architecture and current ISM release. All sample variable values use placeholder GUIDs.

## Resources deployed

- `azurerm_resource_group` in an approved Australian region
- `azurerm_log_analytics_workspace` (`PerGB2018`, `local_authentication_enabled = false`, minimum 90 days interactive retention)
- `azurerm_sentinel_log_analytics_workspace_onboarding`
- `azurerm_management_lock` (`CanNotDelete`, supports `ISM-1815`)
- `azurerm_monitor_diagnostic_setting` (`audit` and `allLogs` sent to the workspace, supports `ISM-1985`)
- Private Link networking (`deploy_private_link = true`):
  - `azurerm_virtual_network` and `azurerm_subnet` for Private Endpoints
  - `azurerm_private_dns_zone` and VNet links for the four Azure Monitor Private Link DNS zones
  - `azurerm_monitor_private_link_scope` (`PrivateOnly` when public ingestion and query are disabled)
  - `azurerm_monitor_data_collection_endpoint` and scoped services for workspace and DCE
  - `azurerm_private_endpoint` with Private DNS Zone Group
- `azurerm_role_assignment` for `Microsoft Sentinel Reader`, `Microsoft Sentinel Responder` and `Microsoft Sentinel Contributor` ([Azure built-in security roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security))

## Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `resource_group_name` | `string` | `rg-sentinel-protected` | Name of the Azure Resource Group. |
| `location` | `string` | `australiaeast` | Australian Azure region (`australiaeast`, `australiasoutheast`, `australiacentral` or `australiacentral2`). |
| `workspace_name` | `string` | `law-sentinel-protected` | Name of the Log Analytics workspace. |
| `retention_in_days` | `number` | `90` | Interactive Analytics retention (90 to 730 days). Configure 365+ days total retention in the Sentinel data lake or archive for `ISM-1988`. |
| `daily_quota_gb` | `number` | `-1` | Daily ingestion cap in GB (`-1` for unlimited). |
| `internet_ingestion_enabled` | `bool` | `false` | Enables public ingestion when `true`; `false` enforces AMPLS `PrivateOnly`. |
| `internet_query_enabled` | `bool` | `false` | Enables public queries when `true`; `false` enforces AMPLS `PrivateOnly`. |
| `deploy_private_link` | `bool` | `true` | Deploys VNet, Private DNS zones, AMPLS, DCE and Private Endpoint. |
| `vnet_name` | `string` | `vnet-secops-protected` | Name of the security hub VNet. |
| `vnet_address_space` | `list(string)` | `["10.60.0.0/22"]` | VNet CIDR block. |
| `private_endpoint_subnet_prefix` | `string` | `10.60.1.0/26` | Private Endpoints subnet CIDR. |
| `ampls_name` | `string` | `ampls-sentinel-protected` | Name of the Azure Monitor Private Link Scope. |
| `dce_name` | `string` | `dce-sentinel-protected` | Name of the Data Collection Endpoint. |
| `enable_delete_lock` | `bool` | `true` | Applies a `CanNotDelete` lock to the workspace. |
| `enable_diagnostic_settings` | `bool` | `true` | Enables workspace audit diagnostic settings. |
| `sentinel_reader_group_object_id` | `string` | `""` | Entra ID security group object ID granted `Microsoft Sentinel Reader`. |
| `sentinel_responder_group_object_id` | `string` | `""` | Entra ID security group object ID granted `Microsoft Sentinel Responder`. |
| `sentinel_contributor_group_object_id` | `string` | `""` | Entra ID security group object ID granted `Microsoft Sentinel Contributor`. |
| `tags` | `map(string)` | `{ classification = "PROTECTED", ... }` | Resource tags applied across deployed resources. |

## Validate and plan

Validate syntax and formatting locally without connecting to an Azure tenant:

```bash
terraform fmt -check -recursive iac/terraform
terraform -chdir=iac/terraform init -backend=false
terraform -chdir=iac/terraform validate
```

To preview changes in a non-production Azure subscription, copy `terraform.tfvars.example` to `terraform.tfvars`, replace placeholder group object IDs, and run `terraform plan`:

```bash
cp iac/terraform/terraform.tfvars.example iac/terraform/terraform.tfvars
terraform -chdir=iac/terraform plan -var-file=terraform.tfvars
```

## Related references

- [Sample Bicep deployment](../bicep/README.md)
- [Terraform AzureRM provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Design your Azure Monitor Private Link configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/private-link-design)
- [Reference architecture: single agency at PROTECTED](../../architectures/single-agency-protected.md)
