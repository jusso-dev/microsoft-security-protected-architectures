# Cost Model: Microsoft Sentinel and Data Lake in Australia East

This worked cost model estimates monthly and annualised Microsoft Sentinel and Microsoft Sentinel data lake spend for **small**, **medium** and **large** Australian PROTECTED deployments in the **Australia East** region using the tiered retention architecture defined in [ADR-0002](../adr/0002-retention-analytics-tier-and-data-lake.md).

> **Disclaimer:** This is an independent community estimate based on public list pricing. It is not produced, endorsed or supported by ASD, ACSC or Microsoft. Actual agency costs depend on your Enterprise Agreement or Whole-of-Government arrangement, exchange rates, data compression ratios and ingestion patterns. Always confirm current pricing in the [Microsoft Sentinel pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-sentinel/) page and Azure Pricing Calculator.

## Pricing date and public unit rates (Australia East)

- **Pricing date checked:** **2026-11-21**
- **Region:** Australia East (`australiaeast`)
- **Source:** Public consumption list prices retrieved via the official [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices) and cross-referenced with [Microsoft Sentinel pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-sentinel/) and [Azure Monitor pricing](https://azure.microsoft.com/en-us/pricing/details/monitor/) (excluding GST).

| Meter | Unit | Australia East (USD) | Australia East (AUD) | Notes |
| :--- | :--- | ---: | ---: | :--- |
| Sentinel Analytics Pay-As-You-Go (simplified pricing) | per GB | 6.2400 | 8.8680 | Includes Log Analytics ingestion, Sentinel analysis and 90 days interactive retention |
| Sentinel 50 GB/day Commitment Tier | per day | 233.8125 | 332.2852 | Effective USD 4.68/GB; breaks even against PAYG at 37.5 GB/day |
| Sentinel 100 GB/day Commitment Tier | per day | 419.4000 | 596.0350 | Effective USD 4.19/GB |
| Sentinel 300 GB/day Commitment Tier | per day | 1,133.0000 | 1,610.1755 | Effective USD 3.78/GB |
| Sentinel 500 GB/day Commitment Tier | per day | 1,791.0000 | 2,545.2995 | Effective USD 3.58/GB |
| Sentinel 1,000 GB/day Commitment Tier | per day | 3,511.0000 | 4,989.6966 | Effective USD 3.51/GB |
| Sentinel 2,000 GB/day Commitment Tier | per day | 6,794.0000 | 9,655.3684 | Effective USD 3.40/GB |
| Log Analytics interactive retention (beyond 90 days) | per GB/month | 0.1500 | 0.2132 | Applies only if interactive Analytics retention exceeds the 90 included days |
| Sentinel data lake ingestion | per GB | 0.0725 | 0.1030 | Direct ingestion into Data Lake tier tables |
| Sentinel data processing | per GB | 0.1450 | 0.2061 | Applied to incoming data lake ingestion streams requiring processing |
| Sentinel data lake storage | per GB/month | 0.0250 | 0.0355 | Long-term lake storage (up to 12 years total retention) |
| Sentinel data lake query | per GB analysed | 0.00725 | 0.0103 | Metered per GB scanned by KQL jobs and exploration queries |
| Sentinel Basic logs analysis (legacy workspace tier) | per GB | 1.2300 | 1.7480 | Shown for reference; superseded for most verbose sources by Data Lake tier |

## Assumptions

All worked models below use the following explicit assumptions:

1. **Billing period:** 30 days per month (360 days per modelled year for storage steady-state calculations).
2. **ISM retention baseline:** 12 months total searchable retention across all security telemetry to satisfy `ISM-1988` ([ISM Guidelines for System Monitoring](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism/cyber-security-guidelines/guidelines-system-monitoring)).
3. **Interactive versus data lake split:**
   - Primary high-signal security telemetry is ingested into the **Analytics tier** with **90 days** interactive retention (included with Microsoft Sentinel) and mirrored into the **Sentinel data lake** for the remaining 9 months (270 days) of paid storage to reach 12 months total retention.
   - Verbose network, firewall allow, DNS and web proxy logs are ingested directly into the **Sentinel data lake** (paying both data lake ingestion and data processing meters) and retained for 12 months (360 days) in data lake storage.
4. **Conservative storage sizing:** Data lake storage volumes are modelled on uncompressed ingested gigabytes. Because the Sentinel data lake stores data in compressed open formats, actual billed storage is typically lower than these conservative estimates ([Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview)).
5. **Free sources and grants:** Billable Analytics GB/day figures represent net billable volume *after* excluding free sources (`AzureActivity`, Microsoft 365 audit logs, Defender alerts) and eligible Microsoft 365 E5 data grants (5 MB per licensed user per day for supported tables) ([Plan costs and understand Microsoft Sentinel pricing and billing](https://learn.microsoft.com/en-us/azure/sentinel/billing)).
6. **Out-of-scope infrastructure costs:** Microsoft 365 / Defender XDR user licences, ExpressRoute circuits, Azure Firewall, AMPLS private endpoints, Azure Logic Apps (SOAR), Linux Syslog forwarder VMs, PAWs and SOC staffing are excluded from these SIEM meter tables and should be budgeted separately.
7. **Discounts and taxes:** List prices exclude GST, Whole-of-Government / Enterprise Agreement discounts and [Microsoft Sentinel pre-purchase plan](https://learn.microsoft.com/en-us/azure/sentinel/billing-pre-purchase-plan) savings.

## Deployment sizing profiles

| Profile | Indicative agency size | Billable Analytics (GB/day) | Analytics pricing plan | Direct Data Lake verbose logs (GB/day) | Monthly Data Lake query scan (GB/month) | Steady-state Month 12 Data Lake storage (GB) |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: |
| Small | 250 to 500 users | 15 | Pay-As-You-Go | 30 | 500 | 14,850 |
| Medium | 2,000 to 3,000 users | 100 | 100 GB/day Commitment Tier | 250 | 5,000 | 117,000 |
| Large | 10,000+ users or multi-domain portfolio | 500 | 500 GB/day Commitment Tier | 1,500 | 25,000 | 675,000 |

## Worked cost tables (Month 12 steady-state)

### Small deployment (15 GB/day Analytics + 30 GB/day Data Lake)

| Cost component | Formula (30-day month) | Monthly (USD) | Monthly (AUD) |
| :--- | :--- | ---: | ---: |
| Analytics ingestion (PAYG) | 15 GB/day x 30 days x USD 6.24 | 2,808.00 | 3,990.60 |
| Data lake ingestion and processing | 30 GB/day x 30 days x (USD 0.0725 + USD 0.145) | 195.75 | 278.19 |
| Data lake storage (Month 12 steady-state) | (15 x 270 + 30 x 360) = 14,850 GB x USD 0.025 | 371.25 | 527.17 |
| Data lake KQL query scan | 500 GB/month x USD 0.00725 | 3.63 | 5.15 |
| **Total monthly (steady-state)** | | **3,378.63** | **4,801.11** |
| **Annualised run-rate (12 months at steady-state)** | | **40,543.50** | **57,613.38** |

### Medium deployment (100 GB/day Analytics + 250 GB/day Data Lake)

| Cost component | Formula (30-day month) | Monthly (USD) | Monthly (AUD) |
| :--- | :--- | ---: | ---: |
| Analytics ingestion (100 GB Commitment Tier) | 30 days x USD 419.40/day | 12,582.00 | 17,881.05 |
| Data lake ingestion and processing | 250 GB/day x 30 days x (USD 0.0725 + USD 0.145) | 1,631.25 | 2,318.25 |
| Data lake storage (Month 12 steady-state) | (100 x 270 + 250 x 360) = 117,000 GB x USD 0.025 | 2,925.00 | 4,153.50 |
| Data lake KQL query scan | 5,000 GB/month x USD 0.00725 | 36.25 | 51.50 |
| **Total monthly (steady-state)** | | **17,174.50** | **24,404.30** |
| **Annualised run-rate (12 months at steady-state)** | | **206,094.00** | **292,851.60** |

### Large deployment (500 GB/day Analytics + 1,500 GB/day Data Lake)

| Cost component | Formula (30-day month) | Monthly (USD) | Monthly (AUD) |
| :--- | :--- | ---: | ---: |
| Analytics ingestion (500 GB Commitment Tier) | 30 days x USD 1,791.00/day | 53,730.00 | 76,358.99 |
| Data lake ingestion and processing | 1,500 GB/day x 30 days x (USD 0.0725 + USD 0.145) | 9,787.50 | 13,909.50 |
| Data lake storage (Month 12 steady-state) | (500 x 270 + 1,500 x 360) = 675,000 GB x USD 0.025 | 16,875.00 | 23,962.50 |
| Data lake KQL query scan | 25,000 GB/month x USD 0.00725 | 181.25 | 257.50 |
| **Total monthly (steady-state)** | | **80,573.75** | **114,488.49** |
| **Annualised run-rate (12 months at steady-state)** | | **966,885.00** | **1,373,861.82** |

## Comparison: Tiered Data Lake versus All-Analytics 12-Month Interactive

The table below compares the recommended tiered design (ADR-0002) against placing the entire combined ingestion volume in the Analytics tier with 12-month interactive retention (9 months paid interactive retention at USD 0.15/GB/month beyond the 90 included days, using optimal commitment tiers for each total volume):

| Profile | Combined daily volume | Tiered Analytics + Data Lake (USD/month) | All-Analytics 12m interactive (USD/month) | Estimated monthly saving |
| :--- | ---: | ---: | ---: | ---: |
| Small | 45 GB/day | 3,378.63 | 8,836.88 (50 GB tier + retention) | 61.8% |
| Medium | 350 GB/day | 17,174.50 | 53,830.00 (300 GB tier + overage + retention) | 68.1% |
| Large | 2,000 GB/day | 80,573.75 | 284,820.00 (2,000 GB tier + retention) | 71.7% |

## Extending retention beyond 12 months (records obligations)

Where agency records disposal authorities under the Archives Act 1983 (Cth) require retaining selected security audit or incident tables for 7 years (84 months) rather than 12 months, each additional 1 TB of steady-state stored data in the Sentinel data lake adds **USD 25.60 / month (AUD 36.35 / month)** at list price (1,024 GB x USD 0.025, conservative uncompressed basis). Restricting 7-year retention to audit, identity and incident tables rather than raw network allow flows keeps multi-year storage costs predictable.

## Cost governance levers

- **Monitor commitment tier break-even points:** Move from Pay-As-You-Go to the 50 GB/day Commitment Tier once sustained Analytics ingestion exceeds **37.5 GB/day** in Australia East ([Reduce Microsoft Sentinel costs](https://learn.microsoft.com/en-us/azure/sentinel/billing-reduce-costs)).
- **Filter noisy telemetry at collection:** Apply Data Collection Rule (DCR) XPath and KQL filters to drop non-security Windows events and debug records before ingestion.
- **Evaluate pre-purchase plans:** Agencies with predictable annual spend can stack a [Microsoft Sentinel pre-purchase plan](https://learn.microsoft.com/en-us/azure/sentinel/billing-pre-purchase-plan) for further savings on eligible meters.
- **Alert on ingestion spikes:** Configure Azure Cost Management budgets and Sentinel ingestion anomaly rules so misconfigured firewalls or verbose debug flags are detected within hours ([Monitor Microsoft Sentinel costs](https://learn.microsoft.com/en-us/azure/sentinel/billing-monitor-costs)).
