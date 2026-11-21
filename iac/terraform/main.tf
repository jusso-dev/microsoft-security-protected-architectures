locals {
  private_dns_zones = var.deploy_private_link ? toset([
    "privatelink.monitor.azure.com",
    "privatelink.oms.opinsights.azure.com",
    "privatelink.ods.opinsights.azure.com",
    "privatelink.agentsvc.azure-automation.net",
  ]) : toset([])

  rbac_assignments = {
    for k, v in {
      reader = {
        role         = "Microsoft Sentinel Reader"
        principal_id = var.sentinel_reader_group_object_id
        description  = "Least-privilege Microsoft Sentinel Reader access for SOC triage analysts."
      }
      responder = {
        role         = "Microsoft Sentinel Responder"
        principal_id = var.sentinel_responder_group_object_id
        description  = "Microsoft Sentinel Responder access for incident investigation and response."
      }
      contributor = {
        role         = "Microsoft Sentinel Contributor"
        principal_id = var.sentinel_contributor_group_object_id
        description  = "Microsoft Sentinel Contributor access for PIM-eligible detection engineers."
      }
    } : k => v if v.principal_id != ""
  }
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_log_analytics_workspace" "this" {
  name                         = var.workspace_name
  location                     = azurerm_resource_group.this.location
  resource_group_name          = azurerm_resource_group.this.name
  sku                          = "PerGB2018"
  retention_in_days            = var.retention_in_days
  daily_quota_gb               = var.daily_quota_gb
  internet_ingestion_enabled   = var.internet_ingestion_enabled
  internet_query_enabled       = var.internet_query_enabled
  local_authentication_enabled = false
  tags                         = var.tags
}

resource "azurerm_sentinel_log_analytics_workspace_onboarding" "this" {
  workspace_id                 = azurerm_log_analytics_workspace.this.id
  customer_managed_key_enabled = false
}

resource "azurerm_management_lock" "workspace" {
  count      = var.enable_delete_lock ? 1 : 0
  name       = "${var.workspace_name}-cannot-delete"
  scope      = azurerm_log_analytics_workspace.this.id
  lock_level = "CanNotDelete"
  notes      = "Protects PROTECTED security event logs from unauthorised deletion (ISM-1815)."
}

resource "azurerm_monitor_diagnostic_setting" "workspace" {
  count                      = var.enable_diagnostic_settings ? 1 : 0
  name                       = "audit-to-workspace"
  target_resource_id         = azurerm_log_analytics_workspace.this.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id

  enabled_log {
    category_group = "audit"
  }

  enabled_log {
    category_group = "allLogs"
  }
}

resource "azurerm_virtual_network" "this" {
  count               = var.deploy_private_link ? 1 : 0
  name                = var.vnet_name
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = var.vnet_address_space
  tags                = var.tags
}

resource "azurerm_subnet" "private_endpoints" {
  count                             = var.deploy_private_link ? 1 : 0
  name                              = "snet-private-endpoints"
  resource_group_name               = azurerm_resource_group.this.name
  virtual_network_name              = azurerm_virtual_network.this[0].name
  address_prefixes                  = [var.private_endpoint_subnet_prefix]
  private_endpoint_network_policies = "Disabled"
}

resource "azurerm_private_dns_zone" "this" {
  for_each            = local.private_dns_zones
  name                = each.value
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "this" {
  for_each              = local.private_dns_zones
  name                  = "${var.vnet_name}-link"
  resource_group_name   = azurerm_resource_group.this.name
  private_dns_zone_name = azurerm_private_dns_zone.this[each.key].name
  virtual_network_id    = azurerm_virtual_network.this[0].id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_monitor_private_link_scope" "this" {
  count                 = var.deploy_private_link ? 1 : 0
  name                  = var.ampls_name
  resource_group_name   = azurerm_resource_group.this.name
  ingestion_access_mode = var.internet_ingestion_enabled ? "Open" : "PrivateOnly"
  query_access_mode     = var.internet_query_enabled ? "Open" : "PrivateOnly"
  tags                  = var.tags
}

resource "azurerm_monitor_data_collection_endpoint" "this" {
  count                         = var.deploy_private_link ? 1 : 0
  name                          = var.dce_name
  resource_group_name           = azurerm_resource_group.this.name
  location                      = azurerm_resource_group.this.location
  public_network_access_enabled = var.internet_ingestion_enabled
  tags                          = var.tags
}

resource "azurerm_monitor_private_link_scoped_service" "workspace" {
  count               = var.deploy_private_link ? 1 : 0
  name                = "${var.workspace_name}-scoped"
  resource_group_name = azurerm_resource_group.this.name
  scope_name          = azurerm_monitor_private_link_scope.this[0].name
  linked_resource_id  = azurerm_log_analytics_workspace.this.id
}

resource "azurerm_monitor_private_link_scoped_service" "dce" {
  count               = var.deploy_private_link ? 1 : 0
  name                = "${var.dce_name}-scoped"
  resource_group_name = azurerm_resource_group.this.name
  scope_name          = azurerm_monitor_private_link_scope.this[0].name
  linked_resource_id  = azurerm_monitor_data_collection_endpoint.this[0].id
}

resource "azurerm_private_endpoint" "ampls" {
  count               = var.deploy_private_link ? 1 : 0
  name                = "pe-${var.ampls_name}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = var.tags

  private_service_connection {
    name                           = "plsc-${var.ampls_name}"
    private_connection_resource_id = azurerm_monitor_private_link_scope.this[0].id
    subresource_names              = ["azuremonitor"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = [for zone in azurerm_private_dns_zone.this : zone.id]
  }
}

resource "azurerm_role_assignment" "sentinel" {
  for_each             = local.rbac_assignments
  scope                = azurerm_log_analytics_workspace.this.id
  role_definition_name = each.value.role
  principal_id         = each.value.principal_id
  principal_type       = "Group"
  description          = each.value.description
}
