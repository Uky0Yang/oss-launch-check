# Security Policy

## Supported Versions

Security fixes target the latest release and the `main` branch. Users of older releases should upgrade before requesting a fix.

## Reporting a Vulnerability

Please do not open a public issue for a suspected vulnerability. Use the repository's **Security** tab and select **Report a vulnerability** to submit a private report.

Include the affected version, reproduction steps, expected impact, and any suggested remediation. Do not include real credentials or sensitive user data. We aim to acknowledge reports within seven days and will coordinate disclosure after a fix is available.

## Scope

Security reports are especially useful when they affect:

- secret detection behavior;
- generated report safety;
- accidental disclosure of local data; or
- unsafe default network or model calls.

The default audit path should remain local, deterministic, and safe for private repositories.
