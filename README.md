# microsoft-security-protected-architectures

Community reference architectures, Mermaid diagrams and ADRs for Microsoft Sentinel, the Sentinel data lake and Defender XDR in Australian PROTECTED environments.

> **Status:** early build. Work is tracked in [issues](https://github.com/jusso-dev/microsoft-security-protected-architectures/issues).

## Goal

Agencies and suppliers running Sentinel and Defender XDR at PROTECTED face the same design questions: workspace and tenant design, data residency in Australian regions, retention for ISM and Archives Act needs, the Sentinel data lake tiers, cost, and how Defender XDR fits. This repo gives reusable answers:

- Reference architectures with Mermaid diagrams for small, medium and multi-tenant (MSSP) deployments
- Architecture decision records (ADRs) for each major choice, with options considered and trade-offs
- Retention and cost models
- Mappings to ISM controls and the IRAP-assessed status of the services used, with links to Microsoft's published IRAP documentation
- Sample Bicep or Terraform for the core deployment

It is guidance only. Validate every design against your own security risk assessment, current ISM release and your IRAP assessor.

## Layout

```text
architectures/   Reference architectures with diagrams
adr/             Architecture decision records
iac/             Sample Bicep and Terraform
docs/            Retention, cost, ISM mapping, glossary
```

## Related projects

- [microsoft-security-logging-guide](https://github.com/jusso-dev/microsoft-security-logging-guide): which Microsoft security logs matter and how to get them into Sentinel
- [soc-ready-logging](https://github.com/jusso-dev/soc-ready-logging)
- [junction](https://github.com/jusso-dev/junction): Microsoft API runtime (Graph, Defender, Sentinel)

## Disclaimer

This is an independent community project. It is not produced, endorsed or supported by the Australian Signals Directorate (ASD), the Australian Cyber Security Centre (ACSC) or Microsoft. References to ASD publications, the ISM and the Essential Eight point to the official sources; always check the current release.

## Licence

Documentation, diagrams and ADRs are under [CC BY 4.0](LICENSE). Code samples (Bicep, Terraform, scripts) are under the [MIT License](LICENSE-code).
