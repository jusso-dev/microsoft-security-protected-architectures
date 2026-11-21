# 0001: Workspace and Tenant Design at PROTECTED

- Status: accepted
- Date: 2026-11-21
- Deciders: Security Architecture, SOC Engineering
- Related: [Service availability, Australian regions and IRAP status](../docs/service-availability-and-irap.md)

## Context and Problem Statement

Australian Government agencies and suppliers deploying Microsoft Sentinel and Microsoft Defender XDR at the PROTECTED level must decide how to structure Microsoft Entra ID tenants and Azure Log Analytics workspaces. Poor boundaries increase the blast radius of a compromised identity, complicate IRAP assessment scope, duplicate ingestion costs across tenants, or hinder SOC correlation across environments.

How should agencies and managed security service providers (MSSPs) structure workspaces and tenants for PROTECTED workloads while preserving central SOC visibility?

## Decision Drivers

- Maintain strict security domain separation between PROTECTED workloads and lower-classification (OFFICIAL or OFFICIAL: Sensitive) or separate agency environments
- Minimise ingestion cost, operational overhead and query complexity across analytics rules and hunting
- Preserve alignment with Microsoft Defender portal unified SecOps architecture, including primary and secondary workspace support and the Microsoft Sentinel data lake limit of 20 workspaces per tenant ([Microsoft Sentinel data lake service limits](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-service-limits))
- Enforce least-privilege, unidirectional cross-tenant access for central SOC or MSSP operations without copying PROTECTED logs out of their owning tenant
- Support ISM event logging, access protection and network/tenant segregation requirements ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring))

## Considered Options

- Option 1: One primary Sentinel workspace per PROTECTED tenant, separate Entra tenants for distinct classification or agency boundaries, and cross-tenant SOC visibility via Microsoft Defender multitenant management and Azure Lighthouse
- Option 2: Multiple Sentinel workspaces inside a single shared Entra tenant serving both OFFICIAL and PROTECTED workloads
- Option 3: Centralised log replication from all agency or domain tenants into a single central SOC Sentinel workspace

## Decision Outcome

Chosen option: **Option 1 (single primary workspace per PROTECTED tenant, separate tenants per security boundary, and cross-tenant visibility via Defender multitenant management and Azure Lighthouse)**, because it delivers the cleanest IRAP boundary, avoids identity-plane coupling across security domains, keeps PROTECTED logs inside the owning tenant in an Australian Azure region, and enables unified SOC triage without double-ingesting logs.

### Consequences

- Good, because all logs for a single PROTECTED agency remain correlated in one primary workspace in Australia East (or Australia Central where required), maximising commitment tier efficiency and avoiding cross-workspace join latency ([Design your Microsoft Sentinel workspace architecture](https://learn.microsoft.com/en-us/azure/sentinel/extend-sentinel-across-workspaces-tenants))
- Good, because separating tenants for distinct security domains isolates Microsoft Entra ID privileged roles, Conditional Access policies and Microsoft Defender XDR data stores
- Good, because [Azure Lighthouse](https://learn.microsoft.com/en-us/azure/lighthouse/overview) provides unidirectional delegated Azure RBAC and [Microsoft Defender multitenant management](https://learn.microsoft.com/en-us/defender-xdr/mto-overview) provides a unified incident queue, cross-tenant advanced hunting and content distribution across onboarded Sentinel workspaces
- Neutral, because organisations with strict internal data-access boundaries inside one PROTECTED tenant (for example, an isolated mission system) may still add a secondary workspace and attach it to the Defender portal alongside the primary workspace ([Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender))
- Bad, because managing multiple tenants increases identity lifecycle overhead, requires disciplined content distribution (analytics rules, automation rules and workbooks) across tenants, and requires per-tenant licensing and commitment tier sizing

### Confirmation

- Verify each PROTECTED tenant contains one primary Sentinel-enabled Log Analytics workspace in an approved Australian region (plus any formally justified secondary workspaces, staying well below the 20-workspace data lake ceiling)
- Confirm Microsoft Defender XDR data storage geography is set to Australia under **Settings > Microsoft Defender XDR > Account** ([Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy))
- Review Azure Lighthouse delegation templates and Defender multitenant management permissions to confirm unidirectional, least-privilege access with Privileged Identity Management (PIM) and phishing-resistant MFA

## Pros and Cons of the Options

### Option 1: Single primary workspace per PROTECTED tenant with Lighthouse and Defender multitenant management

Deploy one primary Microsoft Sentinel workspace per PROTECTED Entra tenant in Australia East (or Australia Central if mandated by agency policy). Use separate Entra tenants when separating different security classifications, independent agencies or distinct IRAP authorisation boundaries. Connect central SOC analysts via Microsoft Defender multitenant management and Azure Lighthouse ([Manage multiple tenants in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/multiple-tenants-service-providers)).

- Good, because single-workspace correlation simplifies analytics rules, entity mapping, UEBA and Sentinel data lake onboarding (the data lake colocates with the primary workspace) ([Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview))
- Good, because combining ingestion volume into one primary workspace reaches Sentinel commitment tiers sooner and lowers per-GB cost ([Plan costs and understand Microsoft Sentinel pricing and billing](https://learn.microsoft.com/en-us/azure/sentinel/billing))
- Good, because customer logs remain inside each tenant's subscription and Australian region, supporting data ownership and contract break clauses
- Good, because access from a managing SOC tenant via Azure Lighthouse is strictly unidirectional and auditable in the customer tenant's Activity Log
- Bad, because cross-tenant analytics rules are not executed natively in a single query engine; detection rules must be deployed per workspace using Defender multitenant content distribution or Infrastructure as Code
- Bad, because each tenant needs its own Defender XDR onboarding and commitment tier planning

### Option 2: Multiple Sentinel workspaces in a single shared Entra tenant

Place OFFICIAL and PROTECTED workloads inside one Entra tenant and attempt to isolate them solely through separate Azure subscriptions and separate Log Analytics workspaces.

- Good, because identity administration and Microsoft 365 licensing sit in a single directory
- Good, because Defender portal allows connecting one primary workspace and multiple secondary workspaces per tenant ([Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender))
- Bad, because Entra Global Administrators, Security Administrators and tenant-wide Defender XDR portals span the entire directory, expanding the PROTECTED IRAP assessment boundary to cover OFFICIAL systems and accounts
- Bad, because Defender XDR stores endpoint, identity and email telemetry at the tenant level, creating classification mixing risk between OFFICIAL and PROTECTED artefacts
- Bad, because splitting ingestion across multiple workspaces fragments commitment tiers and increases cross-workspace query overhead

### Option 3: Centralised log shipping into one shared SOC workspace

Forward or replicate raw security logs from multiple PROTECTED agency tenants into a single central SOC Log Analytics workspace owned by a hub agency or MSSP.

- Good, because analysts run every analytics rule and query in one workspace without cross-tenant joins
- Bad, because replicating logs incurs double ingestion and egress costs across source and central workspaces
- Bad, because co-mingling PROTECTED logs from multiple agencies in one workspace creates severe data-spillage and multi-agency confidentiality risks
- Bad, because offboarding an agency or exercising contractual data-ownership and break clauses becomes complex when logs are co-mingled in a provider-owned workspace

## Australian PROTECTED and ISM Considerations

- **Centralised logging and access protection (`ISM-1405`, `ISM-1985`, `ISM-1815`):** Each PROTECTED tenant operates a centralised Sentinel workspace protected by RBAC, resource locks and immutable retention policies ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring)).
- **Privileged operating environments (`ISM-1380`, `ISM-1688`):** SOC administrators accessing PROTECTED tenants through Azure Lighthouse or Defender multitenant management must operate from hardened privileged access workstations (PAWs) separated from unprivileged corporate environments ([ISM Guidelines for System Management](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-management)).
- **Data ownership and provider segregation (`ISM-1395`, `ISM-1451`, `ISM-1573`, `ISM-1577`):** Keeping raw logs in each agency's own Australian subscription and tenant directly supports clear data ownership, agency access to all logs, and network segregation from managed service providers ([ISM Guidelines for Procurement and Outsourcing](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-procurement-and-outsourcing), [ISM Guidelines for Networking](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-networking)).
- **Regional placement note:** If an agency places its primary Sentinel workspace in Australia Central (Canberra), note that Microsoft Defender XDR Australian data storage remains in Australia East and Australia Southeast ([Service availability, Australian regions and IRAP status](../docs/service-availability-and-irap.md)).

## More Information

- [Extend Microsoft Sentinel across workspaces and tenants](https://learn.microsoft.com/en-us/azure/sentinel/extend-sentinel-across-workspaces-tenants)
- [Manage multiple tenants in Microsoft Sentinel as an MSSP](https://learn.microsoft.com/en-us/azure/sentinel/multiple-tenants-service-providers)
- [Azure Lighthouse overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Microsoft Defender multitenant management overview](https://learn.microsoft.com/en-us/defender-xdr/mto-overview)
- [Microsoft Sentinel roles and permissions](https://learn.microsoft.com/en-us/azure/sentinel/roles)
- [Australia IRAP - Azure Compliance](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-australia-irap)
