# 0002: Retention, Analytics Tier and Sentinel Data Lake

- Status: accepted
- Date: 2026-11-21
- Deciders: Security Architecture, SOC Engineering, Governance and Assurance
- Related: [Service availability, Australian regions and IRAP status](../docs/service-availability-and-irap.md), [ADR-0001](0001-workspace-and-tenant-design-at-protected.md)

## Context and Problem Statement

Australian PROTECTED environments must retain event logs in a searchable manner for at least 12 months under the [Information Security Manual (ISM)](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring) (`ISM-1988`) and meet longer statutory retention periods under the Archives Act 1983 (Cth) and National Archives of Australia (NAA) disposal authorities where applicable. Keeping high-volume telemetry such as firewall, proxy, DNS and network flow logs in the Microsoft Sentinel Analytics tier for 12 months or longer is prohibitively expensive, while discarding or exporting logs to cold storage without search capability fails `ISM-1988` and quarterly threat hunting (`ISM-2153`).

How should PROTECTED deployments combine the Analytics tier, legacy Basic and Auxiliary table plans, and the Microsoft Sentinel data lake to satisfy ISM retention, threat hunting and records obligations at sustainable cost?

## Decision Drivers

- Meet `ISM-1988` (searchable retention of event logs for at least 12 months) and `ISM-2153` (quarterly threat hunting) ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring))
- Support timely automated detection on high-value security logs (`ISM-1986`, `ISM-1987`, `ISM-1228`)
- Support multi-year records retention (up to 7 or 12 years) where required by agency records authorities under the Archives Act 1983 (Cth)
- Control ingestion and retention spend in Australia East by separating high-value detection telemetry from high-volume secondary logs
- Account for IRAP PROTECTED assurance scope and customer-managed key (CMK) constraints in the Sentinel data lake ([Service availability, Australian regions and IRAP status](../docs/service-availability-and-irap.md))

## Considered Options

- Option 1: Tiered Analytics plus Microsoft Sentinel data lake architecture (90 days interactive in Analytics for primary security sources, mirrored and direct-ingested into the Sentinel data lake for 12 months to 7 years total retention)
- Option 2: Analytics tier only with 12-month interactive retention across all tables
- Option 3: Analytics tier with 90-day interactive retention plus Log Analytics long-term retention (archive) and Azure Storage export (no Sentinel data lake)

## Decision Outcome

Chosen option: **Option 1 (tiered Analytics plus Microsoft Sentinel data lake)** as the target PROTECTED pattern, with **Option 3** documented as an interim fallback where an agency's current IRAP authorisation or CMK mandate does not yet cover the Sentinel data lake.

This tiered approach keeps high-signal detection sources in the Analytics tier for 90 days (included at no extra retention charge with Microsoft Sentinel) so scheduled analytics rules, near-real-time rules and quarterly threat hunting operate at full speed, while routing high-volume verbose logs directly to the data lake tier and extending total retention to at least 365 days (and up to 7 or 12 years for records classes) at a fraction of Analytics-tier cost ([Manage tables, tiers, and retention in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/manage-table-tiers-retention), [Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview)).

### Consequences

- Good, because primary security tables benefit from 90 days included Analytics retention and automatic mirroring to the data lake for 12+ months searchable retention ([Plan data retention and log plans](https://learn.microsoft.com/en-us/azure/sentinel/log-plans))
- Good, because high-volume secondary sources (firewall allow logs, DNS, proxy, NSG/VNet flow logs) ingested directly into the data lake tier avoid Analytics ingestion rates (Australia East list pricing: USD 0.0725/GB data lake ingestion vs USD 6.24/GB Analytics Pay-As-You-Go, checked 2026-11-21) ([Microsoft Sentinel pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-sentinel/))
- Good, because the data lake supports up to 12 years of retention, KQL jobs and Jupyter notebook exploration without restoring whole tables to hot Analytics storage ([Microsoft Sentinel data lake service limits](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-service-limits))
- Neutral, because KQL queries and jobs over the data lake incur per-GB scanned charges (USD 0.00725/GB in Australia East) and run asynchronously for large scans, requiring analysts to narrow time windows and filters
- Bad, because CMK encryption is not fully supported for data stored in the Microsoft Sentinel data lake ([Transition Your Microsoft Sentinel Environment to the Defender Portal](https://learn.microsoft.com/en-us/azure/sentinel/move-to-defender)); agencies with a mandatory CMK control across all archive tiers must use Option 3 or seek risk acceptance

### Confirmation

- Audit table plan configuration and retention settings across every Log Analytics table in the Defender portal and via Infrastructure as Code
- Confirm total retention is at least 365 days (`ISM-1988`) on all security-relevant tables, and longer where specified by the agency's records authority
- Verify Azure Monitor and Sentinel cost budgets and alerts are configured for Analytics ingestion, data lake storage and data lake query meters ([Plan costs and understand Microsoft Sentinel pricing and billing](https://learn.microsoft.com/en-us/azure/sentinel/billing))

## Retention table mapped to ISM controls

The following baseline maps common PROTECTED telemetry classes to recommended Sentinel tiers, retention durations and [ISM September 2026](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring) controls. Adjust total retention to match your agency's records disposal authority (for example National Archives of Australia AFDA Express Version 2).

| Telemetry class | Representative tables | Recommended tier | Analytics (interactive) retention | Total retention (Data Lake or Archive) | Relevant ISM controls | Cost and operational notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Identity and privileged access | `SigninLogs`, `AuditLogs`, `AADNonInteractiveUserSignInLogs`, `IdentityLogonEvents`, `IdentityDirectoryEvents` | Analytics (mirrored to Data Lake) | 90 days (included with Sentinel); optionally 365 days for rapid ad-hoc identity investigation | 365 days minimum; 2,555 days (7 years) where required by agency records policy | `ISM-1405`, `ISM-1986`, `ISM-1228`, `ISM-1988`, `ISM-2153` | High detection value; keep in Analytics for NRT and scheduled rules. |
| Endpoint and server security | `SecurityEvent`, `DeviceEvents`, `DeviceProcessEvents`, `DeviceNetworkEvents`, `Syslog` (auth and security) | Analytics (mirrored to Data Lake) | 90 days | 365 days minimum; up to 2,555 days for critical servers | `ISM-1986`, `ISM-1906`, `ISM-1907`, `ISM-0109`, `ISM-1988`, `ISM-2153` | Filter noisy Windows event IDs at collection with Data Collection Rules (DCRs) before ingestion. |
| Security products and alerts | `SecurityAlert`, `SecurityIncident`, `AlertInfo`, `AlertEvidence`, `EmailEvents`, `CloudAppEvents` | Analytics (mirrored to Data Lake) | 90 to 365 days | 2,555 days (7 years) recommended for incident audit trail | `ISM-1987`, `ISM-1228`, `ISM-1988`, `ISM-0125` | Low volume, high evidentiary value for incident registers and post-incident reviews. |
| Cloud control plane and audit | `AzureActivity`, `OfficeActivity`, `AzureDiagnostics` (Key Vault, Firewall, Policy) | Analytics (mirrored to Data Lake) | 90 days | 365 days minimum; 2,555 days where required by records authority | `ISM-1405`, `ISM-1985`, `ISM-1815`, `ISM-1988` | `AzureActivity` and several Microsoft 365 audit sources are free to ingest in Sentinel ([Microsoft Sentinel billing](https://learn.microsoft.com/en-us/azure/sentinel/billing)). |
| High-volume network allow, proxy and DNS logs | `CommonSecurityLog` (allow traffic), `DnsEvents`, `NTANetAnalytics`, custom proxy tables | Direct to Data Lake tier (with high-priority deny/alert subset routed to Analytics via DCR) | 0 days in Analytics (or summary/deny events only in Analytics for 90 days) | 365 days minimum (`ISM-1988`); up to 548 or 730 days per agency policy | `ISM-1960`, `ISM-1961`, `ISM-1988`, `ISM-2153` | Largest cost saving; use DCR transformations to send deny/threat events to Analytics and verbose allow traffic to Data Lake. |
| Auxiliary / verbose operational telemetry | Custom HTTP access logs, CDN logs, storage read logs | Direct to Data Lake tier (or Auxiliary table plan) | 0 days in Analytics | 365 days minimum if security-relevant | `ISM-1959`, `ISM-1988` | Query via KQL jobs or notebooks when hunting or responding to incidents. |

## Pros and Cons of the Options

### Option 1: Tiered Analytics plus Microsoft Sentinel data lake

Use Analytics tier (90 days interactive included) for security telemetry requiring real-time correlation and alerting, and use the Microsoft Sentinel data lake for both mirrored long-term retention (12 months to 12 years) and direct ingestion of high-volume secondary logs ([Direct ingestion into the data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-log-ingestion-guidance)).

- Good, because it reduces ingestion cost for high-volume network and proxy logs by more than 90 percent compared with Analytics Pay-As-You-Go while keeping logs searchable via KQL jobs and notebooks
- Good, because all Analytics tables can be retained for 12 months or up to 12 years in the data lake without paying USD 0.15/GB/month for extended interactive retention
- Good, because summary rules can promote aggregated indicators from the data lake back into Analytics tables for alerting
- Bad, because real-time scheduled analytics rules do not run directly over data lake-only tables (summary rules or KQL jobs are required)
- Bad, because CMK is not fully supported in the Sentinel data lake and agencies must verify data lake coverage in their current IRAP PROTECTED report

### Option 2: Analytics tier only with 12-month interactive retention

Ingest all telemetry into the Analytics tier and extend interactive retention to 365 days on every table ([Configure data retention and archive policies](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure)).

- Good, because every table supports full real-time KQL queries, joins and analytics rules across the full 12-month window with no asynchronous job delay
- Good, because CMK applies uniformly to Log Analytics workspace data (note Defender portal alerts and incidents are still not CMK-encrypted)
- Bad, because ingesting verbose network, DNS and proxy logs at Analytics rates plus 9 months of paid interactive retention (beyond the 90 included days) multiplies SIEM spend several times over

### Option 3: Analytics tier plus Log Analytics long-term retention (archive) and WORM Storage export

Keep 90 days in Analytics, move data aged 90 days to 12+ months into Log Analytics long-term retention (search jobs and restore), and optionally export to an immutable Azure Storage account with legal hold / time-based retention in Australia East or Australia Central ([Configure long-term retention and archive](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-archive)).

- Good, because it relies exclusively on mature Log Analytics and Azure Storage capabilities with long-standing IRAP PROTECTED assessment history and CMK support on storage accounts
- Good, because immutable Blob Storage (WORM) provides strong evidence for `ISM-1815` (protection from unauthorised modification and deletion) and multi-year Archives Act holdings
- Bad, because searching archived Log Analytics tables via restore jobs is slower and more operationally cumbersome than native Sentinel data lake KQL exploration and notebooks
- Bad, because verbose logs still require either Basic/Auxiliary table plans or Analytics ingestion before archiving

## Australian PROTECTED and ISM Considerations

- **Searchable 12-month baseline (`ISM-1988`):** Both mirrored data lake retention and Log Analytics long-term retention keep logs searchable across the 12-month window. Validate during IRAP assessment that query turnaround times for KQL jobs satisfy your agency's incident response service levels ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring)).
- **Integrity and immutability (`ISM-1815`, `ISM-1985`):** Protect Log Analytics workspaces and retention settings using Azure RBAC separation of duties, Azure Resource Locks (`CanNotDelete`), and Azure Policy denying reductions in workspace retention below 365 days total retention.
- **Structured format and time synchronisation (`ISM-1959`, `ISM-0988`):** Normalise incoming logs using Advanced Security Information Model (ASIM) parsers and Data Collection Rule transformations, and ensure source hosts synchronise to authoritative Australian NTP sources.
- **Records obligations:** Retain incident artefacts and relevant security audit logs in line with your agency's records disposal authority under the Archives Act 1983 (Cth); confirm exact disposal classes with your agency's information management team.

## More Information

- [Plan data retention and log plans in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/log-plans)
- [Manage tables, tiers, and retention in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/manage-table-tiers-retention)
- [Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview)
- [Direct ingestion into the Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-log-ingestion-guidance)
- [Log data plans in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-table-plans)
- [Configure data retention and archive in Azure Monitor Logs](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure)
- [Microsoft Sentinel pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-sentinel/)
- [ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring)
