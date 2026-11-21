# Service Availability, Australian Regions and IRAP Status

This document records the regional availability of Microsoft Sentinel, the Microsoft Sentinel data lake, Microsoft Defender XDR and Azure Log Analytics across Australian Azure regions, summarises Microsoft's publicly documented IRAP assessment scope, and flags capability and assurance gaps relevant to Australian PROTECTED environments.

> **Disclaimer:** This is an independent community reference. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft. It summarises publicly available documentation only and never reproduces restricted or NDA-protected content from the Microsoft Service Trust Portal. Always validate against the latest assessment reports and your agency's security risk assessment.

## Regional availability in Australia

Date checked: **2026-11-21**.

Australia has four commercial and government-focused Azure regions:

- **Australia East** (New South Wales, Sydney)
- **Australia Southeast** (Victoria, Melbourne)
- **Australia Central** (Australian Capital Territory, Canberra, delivered from Canberra Data Centres facilities for Australian Government and critical infrastructure)
- **Australia Central 2** (Australian Capital Territory, Canberra, paired Canberra region)

| Capability | Australia East | Australia Southeast | Australia Central / Central 2 | Date checked | Official source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Azure Log Analytics workspace | Available | Available | Available | 2026-11-21 | [Azure Products by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/), [Data retention configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure) |
| Microsoft Sentinel (SIEM / Analytics tier) | Available | Available | Available | 2026-11-21 | [Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency) |
| Microsoft Sentinel data lake | Available (same region as primary workspace) | Available (same region as primary workspace) | Available (same region as primary workspace) | 2026-11-21 | [Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency), [Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview) |
| Microsoft Defender XDR data storage | Available (Australia geo primary/paired) | Available (Australia geo primary/paired) | Not a Defender XDR storage location (uses Australia East / Australia Southeast) | 2026-11-21 | [Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy) |
| Azure Monitor Private Link Scope (AMPLS) | Available | Available | Available | 2026-11-21 | [Design your Azure Monitor Private Link configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/private-link-design) |
| Azure Logic Apps (Sentinel SOAR playbooks) | Available | Available | Available | 2026-11-21 | [Azure Logic Apps for Microsoft Sentinel playbooks](https://learn.microsoft.com/en-us/azure/sentinel/automation/logic-apps-playbooks) |
| Azure Lighthouse (cross-tenant delegation) | Global control plane (supports all Australian regions) | Global control plane (supports all Australian regions) | Global control plane (supports all Australian regions) | 2026-11-21 | [Azure Lighthouse overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview) |
| Microsoft Defender multitenant management | Available via Defender portal | Available via Defender portal | Uses tenant Defender XDR storage in Australia East / Australia Southeast | 2026-11-21 | [Microsoft Defender multitenant management overview](https://learn.microsoft.com/en-us/defender-xdr/mto-overview) |

### Data residency notes

- **Raw log storage:** Microsoft Sentinel stores raw collected logs inside the customer's Azure Log Analytics workspace in the selected Australian Azure region ([Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency)).
- **Data lake colocation:** The Microsoft Sentinel data lake must be deployed in the exact same Azure region as the tenant's primary Microsoft Sentinel workspace ([Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency)).
- **Defender XDR tenant geography:** Microsoft Defender XDR tenant storage geography is fixed when the tenant is provisioned and cannot be moved later. For Australian tenants, Defender XDR stores data in Australia East and Australia Southeast ([Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy)).

## Published IRAP assessment scope

Microsoft engages independent ASD-endorsed Information Security Registered Assessors Program (IRAP) assessors to assess Microsoft cloud services (Azure, Microsoft 365 and Dynamics 365) against the Australian Government [Information Security Manual (ISM)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism) up to and including the **PROTECTED** classification level ([Australia IRAP - Azure Compliance](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-australia-irap)).

Key points from Microsoft's public compliance documentation:

1. **Where to inspect the authoritative scope:** Detailed IRAP assessment reports, the list of in-scope services by assessment cycle, and shared responsibility matrices are published to eligible enterprise and government customers through the Australia IRAP section of the [Microsoft Service Trust Portal](https://servicetrust.microsoft.com/). Restricted report details are intentionally not copied here.
2. **Australian region coverage:** Microsoft's public IRAP documentation notes that Azure services in Australian regions, including the Canberra regions (Australia Central and Australia Central 2, delivered from Canberra Data Centres facilities) as well as Australia East and Australia Southeast, are assessed for Australian Government workloads up to PROTECTED, subject to the exact in-scope service list and compensating controls in the current assessment report ([Australia IRAP - Azure Compliance](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-australia-irap)).
3. **Authorisation remains an agency decision:** An IRAP assessment provides independent assurance evidence against ISM controls; it does not constitute ASD certification or automatic authorisation. Under the ISM and Protective Security Policy Framework, each agency's Authorising Officer must review the current Service Trust Portal reports, apply customer-side compensating controls, and issue a formal Authority to Operate (ATO).

## Flagged gaps and PROTECTED design considerations

Architects and IRAP assessors should specifically review and document risk treatments for the following gaps:

| Gap or constraint | Detail | Impact at PROTECTED | Official reference |
| :--- | :--- | :--- | :--- |
| Sentinel data processing outside Australia | For Log Analytics workspaces outside Europe and Israel, Microsoft Sentinel processes certain customer data in a US region even while raw data remains stored in the Australian workspace region. | Must be explicitly documented in the agency's data sovereignty assessment and reconciled with the current Service Trust Portal IRAP report and agency data handling policy. | [Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency) |
| Defender XDR storage not in Australia Central | Microsoft Defender XDR stores Australian tenant data in Australia East and Australia Southeast, not in Australia Central or Australia Central 2. | Agencies hosting Sentinel in Australia Central will have XDR native tables and Defender portal metadata stored in Australia East/Southeast rather than Canberra. | [Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy) |
| Customer-managed keys (CMK) limitations in Defender portal and data lake | CMK encryption is not fully supported for data stored in the Microsoft Sentinel data lake. Additionally, after onboarding Sentinel to the Defender portal, alerts and incidents are no longer CMK-encrypted (workspace log data and analytics rules remain CMK-encrypted). | Organisations whose risk assessment mandates CMK across all alert, incident and archive tiers must treat this gap with compensating controls or risk acceptance. | [Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender), [Set up customer-managed keys](https://learn.microsoft.com/en-us/azure/sentinel/customer-managed-keys) |
| Azure portal retirement for Sentinel on 31 March 2027 | After 31 March 2027, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. | All new PROTECTED architectures must target the Defender portal and Unified RBAC model from inception; legacy Azure-portal-only runbooks and permissions must be migrated. | [Plan data retention and log plans](https://learn.microsoft.com/en-us/azure/sentinel/log-plans), [Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender) |
| IRAP assessment lag for newer capabilities | Newly released features (such as Sentinel data lake sub-capabilities, graph analytics, MCP/AI integrations or newly added connectors) may become generally available before appearing in a published IRAP PROTECTED assessment report. | Verify each specific feature against the latest Australia IRAP assessment report on the Service Trust Portal before enabling it for PROTECTED telemetry. | [Australia IRAP - Azure Compliance](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-australia-irap), [Microsoft Service Trust Portal](https://servicetrust.microsoft.com/) |
| Sentinel data lake BCDR and workspace limits | The Sentinel data lake supports up to 20 workspaces per tenant, must colocate with the primary workspace, and customer-enabled cross-region BCDR options have regional availability constraints. | Validate disaster recovery objectives (RPO/RTO) for Australia East and Australia Central designs, and plan workspace consolidation if approaching the 20-workspace limit. | [Microsoft Sentinel data lake service limits](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-service-limits), [Geographical availability and data residency in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency) |
| AMPLS does not cover SaaS/cloud connectors | Azure Monitor Private Link Scope secures agent-based ingestion (Azure Monitor Agent) and private query paths, whereas service-to-service connectors (Entra ID, Defender XDR, Microsoft 365) flow over Microsoft's backbone outside customer VNets. | Document both private VNet ingestion paths and Microsoft backbone connector paths in network architecture diagrams and gateway assessments. | [Design your Azure Monitor Private Link configuration](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/private-link-design) |

## Verification checklist for agencies

Before authorising a PROTECTED deployment:

1. Download the latest Australia IRAP PROTECTED assessment reports for Azure and Microsoft 365 from the [Microsoft Service Trust Portal](https://servicetrust.microsoft.com/).
2. Confirm that each selected service and regional deployment (Australia East, Australia Southeast, Australia Central or Australia Central 2) is listed in scope in the current report.
3. Review the customer responsibilities and compensating controls required by the report alongside the current [Information Security Manual (ISM)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism) release.
4. Confirm Defender XDR tenant storage location in the Microsoft Defender portal under **Settings > Microsoft Defender XDR > Account** before onboarding Sentinel.
