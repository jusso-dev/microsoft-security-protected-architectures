# Changelog

All notable changes to this repository are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-21

Initial v1.0.0 community release of reference architectures, Architecture Decision Records (ADRs), cost and ISM documentation, and Infrastructure as Code samples for Microsoft Sentinel, the Microsoft Sentinel data lake and Microsoft Defender XDR in Australian PROTECTED environments.

### Added

- **Reference architectures and Mermaid diagrams (`architectures/`):**
  - [Single agency at PROTECTED](architectures/single-agency-protected.md) covering identity, AMPLS private networking, log sources, Sentinel, Sentinel data lake, Defender XDR, SOAR and ISM control mapping
  - [Multi-tenant and MSSP at PROTECTED](architectures/multi-tenant-mssp-protected.md) covering dedicated managing SOC tenant, Azure Lighthouse eligible delegation, Defender multitenant management, segregation of duties, data boundaries and risk mitigations
  - [Hybrid and on-premises log sources at PROTECTED](architectures/hybrid-and-on-premises-sources.md) covering Azure Arc, AMA, HA Syslog/CEF collectors, Active Directory Domain Controllers, ExpressRoute, AMPLS and Private DNS isolation
- **Architecture Decision Records (`adr/`):**
  - MADR template ([adr/template.md](adr/template.md)) and CI-verified generated index ([adr/README.md](adr/README.md))
  - [ADR-0001: Workspace and tenant design at PROTECTED](adr/0001-workspace-and-tenant-design-at-protected.md)
  - [ADR-0002: Retention, analytics tier and Sentinel data lake](adr/0002-retention-analytics-tier-and-data-lake.md)
  - [ADR-0003: Defender XDR integration and unified SOC platform](adr/0003-defender-xdr-integration-and-unified-soc-platform.md) (verifying the 31 March 2027 end of Azure portal support for Microsoft Sentinel)
- **Research, cost and compliance documentation (`docs/`):**
  - [Service availability, Australian regions and IRAP status](docs/service-availability-and-irap.md) (checked 2026-11-21)
  - [Cost model for Australia East](docs/cost-model.md) for small, medium and large deployments using public Azure Retail Prices API rates (checked 2026-11-21)
  - [ISM control mapping](docs/ism-control-mapping.md) aligned to the September 2026 ISM release
- **Infrastructure as Code (`iac/`):**
  - [Sample Bicep deployment](iac/bicep/README.md) with compiled `azuredeploy.json`, Deploy to Azure button, sample `.bicepparam` using placeholder GUIDs and documented parameters
  - [Sample Terraform deployment](iac/terraform/README.md) providing the AzureRM equivalent of the Bicep core sample
- **CI and validation tooling:**
  - GitHub Actions workflow covering style and secret hygiene checks, ADR index verification, KQL validation, unit tests, Markdown linting, link checking, Mermaid SVG render validation, Bicep build and Terraform validate
