# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| main    | ✅        |

## Reporting a Vulnerability

If you discover a security vulnerability in auto-dao, please report it responsibly:

1. **Do NOT open a public issue.**
2. Send a description of the vulnerability to the repository maintainer via [GitHub Security Advisories](https://github.com/Jun-maxs/auto-dao/security/advisories/new).
3. Include steps to reproduce, impact assessment, and any suggested fix.

We aim to acknowledge reports within **48 hours** and provide a fix or mitigation plan within **7 days** for confirmed vulnerabilities.

## Scope

This policy covers:

- All code in this repository (skills, scripts, templates).
- Configuration handling (API keys, `.env` files).
- Any third-party API interactions (e.g., MinerU API).

## Security Best Practices for Users

- **Never commit `settings/.env`** — it is already in `.gitignore`.
- **Review materials before uploading** to third-party conversion APIs (MinerU). See [PRIVACY.md](PRIVACY.md) for details.
- Keep your local dependencies up to date (`pip install --upgrade -r requirements.txt`).
