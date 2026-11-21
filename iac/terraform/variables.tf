variable "resource_group_name" {
  type        = string
  default     = "rg-sentinel-protected"
  description = "Name of the Azure Resource Group hosting the core Sentinel deployment."
}

variable "location" {
  type        = string
  default     = "australiaeast"
  description = "Australian Azure region for regional resources."

  validation {
    condition = contains([
      "australiaeast",
      "australiasoutheast",
      "australiacentral",
      "australiacentral2",
    ], var.location)
    error_message = "location must be an Australian Azure region (australiaeast, australiasoutheast, australiacentral or australiacentral2)."
  }
}

variable "workspace_name" {
  type        = string
  default     = "law-sentinel-protected"
  description = "Name of the Azure Log Analytics workspace hosting Microsoft Sentinel."
}

variable "retention_in_days" {
  type        = number
  default     = 90
  description = "Interactive Analytics retention in days (minimum 90 days included with Microsoft Sentinel; configure 365+ days total retention in the Sentinel data lake or archive for ISM-1988)."

  validation {
    condition     = var.retention_in_days >= 90 && var.retention_in_days <= 730
    error_message = "retention_in_days must be between 90 and 730."
  }
}

variable "daily_quota_gb" {
  type        = number
  default     = -1
  description = "Optional daily ingestion cap in GB. Set to -1 for unlimited ingestion."
}

variable "internet_ingestion_enabled" {
  type        = bool
  default     = false
  description = "Allow public internet ingestion to the Log Analytics workspace and DCE. False enforces AMPLS PrivateOnly mode."
}

variable "internet_query_enabled" {
  type        = bool
  default     = false
  description = "Allow public internet queries to the Log Analytics workspace. False enforces AMPLS PrivateOnly mode."
}

variable "deploy_private_link" {
  type        = bool
  default     = true
  description = "Deploy the hub Virtual Network, Private DNS zones, AMPLS, Data Collection Endpoint and Private Endpoint."
}

variable "vnet_name" {
  type        = string
  default     = "vnet-secops-protected"
  description = "Name of the security hub Virtual Network."
}

variable "vnet_address_space" {
  type        = list(string)
  default     = ["10.60.0.0/22"]
  description = "Address space for the security hub Virtual Network."
}

variable "private_endpoint_subnet_prefix" {
  type        = string
  default     = "10.60.1.0/26"
  description = "Address prefix for the Private Endpoints subnet."
}

variable "ampls_name" {
  type        = string
  default     = "ampls-sentinel-protected"
  description = "Name of the Azure Monitor Private Link Scope (AMPLS)."
}

variable "dce_name" {
  type        = string
  default     = "dce-sentinel-protected"
  description = "Name of the Data Collection Endpoint (DCE)."
}

variable "enable_delete_lock" {
  type        = bool
  default     = true
  description = "Apply a CanNotDelete management lock to the Log Analytics workspace (supports ISM-1815)."
}

variable "enable_diagnostic_settings" {
  type        = bool
  default     = true
  description = "Enable diagnostic settings auditing Log Analytics workspace operations."
}

variable "sentinel_reader_group_object_id" {
  type        = string
  default     = ""
  description = "Optional Entra ID security group object ID granted Microsoft Sentinel Reader on the workspace."
}

variable "sentinel_responder_group_object_id" {
  type        = string
  default     = ""
  description = "Optional Entra ID security group object ID granted Microsoft Sentinel Responder on the workspace."
}

variable "sentinel_contributor_group_object_id" {
  type        = string
  default     = ""
  description = "Optional Entra ID security group object ID granted Microsoft Sentinel Contributor on the workspace."
}

variable "tags" {
  type = map(string)
  default = {
    classification = "PROTECTED"
    workload       = "microsoft-sentinel"
    managedBy      = "terraform"
  }
  description = "Resource tags applied across deployed resources."
}
