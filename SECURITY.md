# Security Policy

## Supported Versions

This project is currently under active development.

At the moment, security updates are provided for the latest version available in the main branch.

| Version | Supported |
| ------- | --------- |
| main    | Yes       |
| older versions | No |

## Reporting a Security Issue

If you discover a security vulnerability, please do not create a public GitHub issue.

Instead, report the issue privately through the GitHub security reporting feature or contact the project maintainer directly.

Please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any relevant logs or technical details

## Security Principles

This project follows these principles:

- Database passwords and secrets are never stored in the repository.
- Environment-specific configuration is managed through `.env` files.
- The `.env` file is excluded from version control.
- Example configuration files contain placeholders only.
- Production credentials must never be committed.

## Development Environment

The project is designed for local development and testing environments.

Before using this project in production environments:

- Review all database permissions.
- Replace all default credentials.
- Use secure secret management solutions.
- Review deployment-specific security requirements.

