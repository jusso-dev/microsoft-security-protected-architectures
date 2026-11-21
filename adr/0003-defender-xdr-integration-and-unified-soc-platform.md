# 0003: Defender XDR Integration and Unified SOC Platform

- Status: accepted
- Date: 2026-11-21
- Deciders: Security Architecture, SOC Engineering
- Related: [Service availability, Australian regions and IRAP status](../docs/service-availability-and-irap.md), [ADR-0001](0001-workspace-and-tenant-design-at-protected.md), [ADR-0002](0002-retention-analytics-tier-and-data-lake.md)

## Context and Problem Statement

Microsoft has consolidated Microsoft Sentinel and Microsoft Defender XDR into a unified security operations experience in the Microsoft Defender portal. Official Microsoft Learn documentation states that **after 31 March 2027** (date verified 2026-11-21), Microsoft Sentinel will no longer be supported in the Azure portal and will be available exclusively in the Microsoft Defender portal ([Plan data retention and log plans in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/log-plans), [Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender)).

For Australian PROTECTED environments, adopting the unified Defender portal changes how SOC analysts query native Defender XDR tables versus ingested Sentinel data connector tables, how permissions are governed, how customer-managed keys (CMK) behave on alerts and incidents, and where XDR metadata is stored.

How should PROTECTED deployments integrate Microsoft Sentinel with Microsoft Defender XDR ahead of the 31 March 2027 Azure portal retirement?

## Decision Drivers

- Meet the mandatory transition away from Microsoft Sentinel in the Azure portal before **31 March 2027** ([Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender))
- Eliminate duplicate incident queues and enable unified correlation and automatic attack disruption across endpoints, identities, email, cloud apps and SIEM logs (`ISM-0120`, `ISM-1228`)
- Avoid unnecessary Sentinel ingestion charges for XDR telemetry while still meeting the 12-month searchable retention requirement (`ISM-1988`) ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring))
- Account transparently for PROTECTED data residency (Australia East and Australia Southeast for Defender XDR) and CMK limitations on alerts and incidents

## Considered Options

- Option 1: Onboard Microsoft Sentinel to the Microsoft Defender portal as the primary SOC console, use native XDR tables and custom detections for real-time XDR coverage, and retain XDR telemetry for 12+ months in Sentinel Analytics and the Sentinel data lake
- Option 2: Continue operating Microsoft Sentinel in the Azure portal with the legacy Defender XDR data connector until closer to 31 March 2027
- Option 3: Operate Microsoft Defender XDR and Microsoft Sentinel as separate portals with custom API or SOAR incident synchronisation

## Decision Outcome

Chosen option: **Option 1 (unified Microsoft Defender portal with selective XDR ingestion/data lake retention for 12-month ISM compliance)**, because Azure portal support ends on 31 March 2027, unified operations materially improve incident triage and hunting speed, and selective retention in Sentinel preserves `ISM-1988` compliance without duplicating every verbose XDR table at Analytics-tier rates.

### Consequences

- Good, because analysts investigate SIEM and XDR incidents in one queue, run unified Advanced Hunting queries across both native XDR tables and Sentinel workspace tables, and use unified automation rules ([Connect Microsoft Sentinel to Microsoft Defender XDR](https://learn.microsoft.com/en-us/unified-secops-platform/microsoft-sentinel-onboard), [Automation rules and playbooks in the Defender portal](https://learn.microsoft.com/en-us/defender-xdr/siem-defender-automation))
- Good, because onboarding does not require migrating or re-ingesting existing Log Analytics workspace data; the workspace remains in the customer's chosen Australian Azure region
- Good, because Microsoft Defender XDR unified RBAC allows role scoping across workloads and workspaces ([Update permissions and roles with Defender RBAC](https://learn.microsoft.com/en-us/azure/sentinel/transition-unified-rbac))
- Neutral, because native Defender XDR retention (30 days standard, or up to 90 days for supported tables with Microsoft 365 E5) is shorter than `ISM-1988` (12 months); agencies must still retain required XDR tables in Sentinel or the Sentinel data lake for at least 365 days ([Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy))
- Bad, because after onboarding to the Defender portal, alerts and incidents are no longer encrypted with customer-managed keys (CMK), even when CMK is enabled on the underlying Log Analytics workspace ([Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender))
- Bad, because several Azure-portal-only behaviours change on onboarding (for example, legacy Fusion rules are replaced by Defender XDR correlation, and incidents created directly via Azure portal APIs or Logic Apps are not synchronised to the Defender portal)

### Confirmation

- Confirm the primary Sentinel workspace is onboarded to the Microsoft Defender portal and verify tenant data storage is in Australia (Australia East and Australia Southeast)
- Audit Microsoft Defender XDR unified RBAC role assignments and ensure legacy Azure portal Sentinel roles are reconciled
- Verify that every Defender XDR table required for `ISM-1988` (such as `DeviceProcessEvents`, `DeviceNetworkEvents`, `IdentityLogonEvents`, `EmailEvents`, `CloudAppEvents`, `AlertInfo`, `AlertEvidence`) has a configured 12-month or longer retention path in Sentinel Analytics / Sentinel data lake
- Document the alert/incident CMK limitation and Defender XDR Australia East/Southeast storage location in the system's IRAP security risk management plan

## Data connectors versus XDR native tables

| Aspect | Native Defender XDR tables (Defender portal) | Microsoft Defender XDR data connector (Sentinel workspace / Data Lake) |
| :--- | :--- | :--- |
| Ingestion billing | Included with Defender XDR licences (no additional Sentinel GB charge) | Billed per GB into Sentinel Analytics (offset by eligible Microsoft 365 E5 data grant) or at lower Data Lake ingestion rates ([Data ingestion and billing in unified SecOps](https://learn.microsoft.com/en-us/defender-xdr/integrated-security-operations-data-billing-retention)) |
| Default retention | 30 days standard; up to 90 days queryable for supported data with M365 E5 | 90 days interactive in Analytics; up to 12 years total in Sentinel data lake or archive |
| Satisfies `ISM-1988` (12 months searchable) | No (30 to 90 days only) | Yes (configure total retention to at least 365 days) |
| Detection engine | Defender XDR custom detections and native correlation | Microsoft Sentinel scheduled / NRT analytics rules, summary rules and KQL jobs |
| Cross-source joins | Unified Advanced Hunting joins native XDR tables with Sentinel workspace tables across the 30 to 90 day window | Full joins across 12+ months when both XDR and non-Microsoft logs are retained in Sentinel / Data Lake |
| Recommended PROTECTED usage | Real-time triage, custom detections and 30 to 90 day Advanced Hunting | Mandatory long-term searchable retention (`ISM-1988`), multi-year forensics and correlation with non-Microsoft firewall/network logs |

## Pros and Cons of the Options

### Option 1: Unified Microsoft Defender portal with selective 12-month retention

Onboard Microsoft Sentinel to the Microsoft Defender portal immediately for new PROTECTED builds and migrate existing deployments well before 31 March 2027 ([Transition an existing Microsoft Sentinel deployment](https://learn.microsoft.com/en-us/azure/sentinel/transition-existing-sentinel-deployment)).

- Good, because it aligns with Microsoft's supported platform direction beyond 31 March 2027 and avoids rushed migration risk
- Good, because combining Defender custom detections with Sentinel Analytics and Data Lake retention optimises cost while maintaining 12-month `ISM-1988` compliance
- Good, because SOC analysts use one portal, one incident model and one Advanced Hunting query surface
- Bad, because alerts and incidents lose CMK coverage on onboarding, requiring formal risk acceptance or compensating controls
- Bad, because existing Azure-portal-centric SOC playbooks, analytics rules referencing legacy schemas, and RBAC assignments require testing and migration ([Update content to use Advanced Hunting tables](https://learn.microsoft.com/en-us/azure/sentinel/transition-advanced-hunting-tables))

### Option 2: Remain in the Azure portal until 31 March 2027

Keep running Microsoft Sentinel solely in the Azure portal using the legacy connector until the retirement deadline.

- Good, because existing Azure-portal-only runbooks and CMK coverage on Azure-portal Sentinel incidents remain temporarily unchanged
- Bad, because support ends on 31 March 2027, creating an unavoidable hard deadline and forcing a late migration under schedule pressure
- Bad, because teams miss unified incident correlation, automatic attack disruption, Defender multitenant management and Sentinel data lake capabilities managed through the Defender portal

### Option 3: Dual portals with custom API or SOAR synchronisation

Operate Defender XDR and Sentinel separately and synchronise alerts/incidents via custom Logic Apps or third-party SOAR tooling.

- Good, because teams retain custom middleware control over incident enrichment
- Bad, because custom synchronisation is brittle, adds operational overhead, duplicates alerting noise, and still does not avoid the 31 March 2027 retirement of Sentinel in the Azure portal

## Australian PROTECTED and ISM Considerations

- **Verification of retirement date:** Checked on 2026-11-21 against [Plan data retention and log plans in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/log-plans), which states: "After March 31, 2027, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal."
- **Data residency for Australia Central Sentinel workspaces:** Even if the Log Analytics workspace is deployed in Australia Central (Canberra), Microsoft Defender XDR stores Australian tenant data in Australia East and Australia Southeast ([Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy)). Confirm this cross-region Australian footprint is acceptable within the agency's IRAP scope.
- **Cryptography and CMK (`ISM-1080`, `ISM-1769`):** Microsoft encrypts Defender portal alerts, incidents and Sentinel data lake contents at rest with Microsoft-managed keys (AES-256). Where an agency policy specifies CMK (`ISM-1080` interpretation), document the Defender portal alert/incident CMK limitation explicitly for the Authorising Officer ([ISM Guidelines for Cryptography](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-cryptography)).
- **Timely detection and analyst tooling (`ISM-0120`, `ISM-1228`, `ISM-1987`):** Unified SecOps directly supports equipping cyber security personnel with integrated detection and incident identification tooling ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring)).

## More Information

- [Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender)
- [Connect Microsoft Sentinel to Microsoft Defender XDR](https://learn.microsoft.com/en-us/unified-secops-platform/microsoft-sentinel-onboard)
- [Connect data from Microsoft Defender XDR to Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/connect-microsoft-365-defender)
- [Transition an existing Microsoft Sentinel deployment](https://learn.microsoft.com/en-us/azure/sentinel/transition-existing-sentinel-deployment)
- [Update permissions and roles with Defender RBAC](https://learn.microsoft.com/en-us/azure/sentinel/transition-unified-rbac)
- [Update content to use Advanced Hunting tables](https://learn.microsoft.com/en-us/azure/sentinel/transition-advanced-hunting-tables)
- [Data ingestion and billing in unified security operations](https://learn.microsoft.com/en-us/defender-xdr/integrated-security-operations-data-billing-retention)
- [Microsoft Defender XDR data security and privacy](https://learn.microsoft.com/en-us/defender-xdr/data-privacy)
