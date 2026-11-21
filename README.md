# microsoft-security-protected-architectures

Community reference architectures, Mermaid diagrams and ADRs for Microsoft Sentinel, the Sentinel data lake and Defender XDR in Australian PROTECTED environments.

> **Status:** v1.0.0 released. See [CHANGELOG.md](CHANGELOG.md) and [issues](https://github.com/jusso-dev/microsoft-security-protected-architectures/issues).

## Goal

Agencies and suppliers running Sentinel and Defender XDR at PROTECTED face the same design questions: workspace and tenant design, data residency in Australian regions, retention for ISM and Archives Act needs, the Sentinel data lake tiers, cost, and how Defender XDR fits. This repo gives reusable answers:

- Reference architectures with Mermaid diagrams for single-agency, multi-tenant (MSSP) and hybrid/on-premises deployments
- Architecture decision records (ADRs) for each major choice, with options considered and trade-offs
- Retention and worked Australia East cost models
- Mappings to September 2026 ISM controls and the IRAP-assessed status of the services used, with links to Microsoft's published IRAP documentation
- Sample Bicep and Terraform for the core deployment

It is guidance only. Validate every design against your own security risk assessment, current ISM release and your IRAP assessor.

## Contents

- **Reference architectures ([architectures/](architectures/README.md)):**
  - [Single agency at PROTECTED](architectures/single-agency-protected.md)
  - [Multi-tenant and MSSP at PROTECTED](architectures/multi-tenant-mssp-protected.md)
  - [Hybrid and on-premises log sources at PROTECTED](architectures/hybrid-and-on-premises-sources.md)
- **Architecture Decision Records ([adr/](adr/README.md)):**
  - [ADR-0001: Workspace and tenant design at PROTECTED](adr/0001-workspace-and-tenant-design-at-protected.md)
  - [ADR-0002: Retention, analytics tier and Sentinel data lake](adr/0002-retention-analytics-tier-and-data-lake.md)
  - [ADR-0003: Defender XDR integration and unified SOC platform](adr/0003-defender-xdr-integration-and-unified-soc-platform.md)
- **Documentation ([docs/](docs/README.md)):**
  - [Service availability, Australian regions and IRAP status](docs/service-availability-and-irap.md)
  - [Cost model for Australia East](docs/cost-model.md)
  - [ISM control mapping (September 2026 ISM)](docs/ism-control-mapping.md)
- **Infrastructure as Code ([iac/](iac/README.md)):**
  - [Sample Bicep deployment](iac/bicep/README.md) (with Deploy to Azure button)
  - [Sample Terraform deployment](iac/terraform/README.md)

## Layout

```text
architectures/   Reference architectures with diagrams
adr/             Architecture decision records (MADR format)
iac/             Sample Bicep and Terraform
docs/            Regional availability, IRAP status, cost model and ISM mapping
scripts/         Style, KQL, Mermaid and ADR index checks
tests/           Unit tests for repository checks
```

## Related projects

- [microsoft-security-logging-guide](https://github.com/jusso-dev/microsoft-security-logging-guide): which Microsoft security logs matter and how to get them into Sentinel
- [soc-ready-logging](https://github.com/jusso-dev/soc-ready-logging)
- [junction](https://github.com/jusso-dev/junction): Microsoft API runtime (Graph, Defender, Sentinel)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft. References to ASD publications, the ISM and the Essential Eight point to the official sources; always check the current release.

## Licence

Documentation, diagrams and ADRs are under [CC BY 4.0](LICENSE). Code samples (Bicep, Terraform, scripts) are under the [MIT License](LICENSE-code).
