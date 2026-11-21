# Contributing

Thanks for helping build and maintain this community reference repository.

## How work happens

1. Pick an open issue from the repository issue tracker.
2. Branch from `main` using `feat/<issue-number>-short-name` (for example `feat/4-workspace-tenant-adr`).
3. Keep each pull request focused on a single issue and include `Closes #<issue-number>` in the pull request description.
4. Ensure all CI checks pass before merging. Pull requests are squash-merged into `main`.

## Repository layout

- `architectures/`: Reference architectures with Mermaid diagrams and narratives
- `adr/`: Architecture decision records in MADR format
- `iac/`: Sample Bicep and Terraform for core deployments
- `docs/`: Research notes, retention and cost models, and ISM control mappings
- `scripts/`: Validation and generation scripts used locally and in CI
- `tests/`: Unit tests for repository scripts

## Style rules

- Use plain Australian English (organisation, licence, analyse, authorise, centralise).
- Do not use em dashes (`U+2014`) or emojis anywhere in documentation, diagrams or code comments.
- Link every factual claim about a Microsoft service or ASD publication to an official source (such as [Microsoft Learn](https://learn.microsoft.com/), the [Microsoft Service Trust Portal](https://servicetrust.microsoft.com/) or [cyber.gov.au](https://www.cyber.gov.au/)).
- Never copy restricted, NDA-only or non-public content (for example full IRAP assessment reports from the Service Trust Portal). Summarise publicly available scope and link to the official portal instead.
- Do not claim or imply official endorsement, approval or support by ASD, ACSC or Microsoft.
- Never commit real tenant IDs, subscription IDs, workspace IDs, secrets, credentials or customer data. Use placeholder GUIDs such as `00000000-0000-0000-0000-000000000000`.
- Keep all tooling and samples read-only where inspecting a tenant, and never connect tests to a real tenant.

## Local validation checks

Run these checks before opening a pull request:

```bash
# Style, secret hygiene and endorsement claim check
python3 scripts/check_style.py

# KQL syntax check
python3 scripts/check_kql.py

# Unit tests
python3 -m unittest discover -s tests -v

# Markdown lint
npx --yes markdownlint-cli2 "**/*.md" "#node_modules" "#.terraform"

# Mermaid diagram syntax check (or omit --syntax-only if mmdc is installed)
python3 scripts/check_mermaid.py --syntax-only
```

When modifying files in `iac/`:

```bash
# Bicep build check (when iac/bicep contains .bicep files)
az bicep build --file iac/bicep/main.bicep --outfile /tmp/main.json

# Terraform format and validate check (when iac/terraform contains .tf files)
terraform fmt -check -recursive iac/terraform
terraform -chdir=iac/terraform init -backend=false
terraform -chdir=iac/terraform validate
```
