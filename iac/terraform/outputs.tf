output "resource_group_id" {
  value       = azurerm_resource_group.this.id
  description = "Resource ID of the Resource Group hosting the Sentinel deployment."
}

output "workspace_resource_id" {
  value       = azurerm_log_analytics_workspace.this.id
  description = "Resource ID of the deployed Log Analytics workspace."
}

output "workspace_customer_id" {
  value       = azurerm_log_analytics_workspace.this.workspace_id
  description = "Customer ID (GUID) of the deployed Log Analytics workspace."
}

output "sentinel_onboarding_id" {
  value       = azurerm_sentinel_log_analytics_workspace_onboarding.this.id
  description = "Resource ID of the Microsoft Sentinel onboarding resource."
}

output "ampls_resource_id" {
  value       = var.deploy_private_link ? azurerm_monitor_private_link_scope.this[0].id : ""
  description = "Resource ID of the Azure Monitor Private Link Scope, when deployed."
}

output "dce_resource_id" {
  value       = var.deploy_private_link ? azurerm_monitor_data_collection_endpoint.this[0].id : ""
  description = "Resource ID of the Data Collection Endpoint, when deployed."
}
