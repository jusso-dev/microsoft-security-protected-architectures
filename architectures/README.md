# Architectures

Reference architectures and Mermaid diagrams for Microsoft Sentinel, the Microsoft Sentinel data lake and Microsoft Defender XDR in Australian PROTECTED environments.

## Available architectures

- [Single agency at PROTECTED](single-agency-protected.md): Dedicated PROTECTED tenant, Australia East primary workspace, AMPLS private networking, Sentinel data lake, Defender XDR, SOAR and ISM control mapping
- [Multi-tenant and MSSP at PROTECTED](multi-tenant-mssp-protected.md): Dedicated managing SOC tenant, Azure Lighthouse eligible delegation, Microsoft Defender multitenant management, segregation of duties, data boundaries and risk mitigations
- [Hybrid and on-premises log sources at PROTECTED](hybrid-and-on-premises-sources.md): Azure Arc, Azure Monitor Agent (AMA), HA Syslog and CEF forwarders, Active Directory Domain Controllers, ExpressRoute, AMPLS and Private DNS isolation
