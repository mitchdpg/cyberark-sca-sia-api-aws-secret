# CyberArk SCA & SIA Policy Retriever — AWS Secrets Manager (Python)

Created a script to authenticate with CyberArk's platform API using OAuth 2.0 client credentials, generate a bearer token, and retrieve all Secure Cloud Access (SCA) and Secure Infrastructure Access (SIA) policies. All API credentials are stored in and retrieved from AWS Secrets Manager — no plaintext credentials, no runtime prompts. 
Note: This enables full automation via launchd (macOS), Task Scheduler (Windows), or cron (Linux).

## Overview

This project demonstrates Python automation against CyberArk's SCA and SIA policy endpoints with an AWS-integrated credential management approach. Instead of prompting for credentials at runtime, the script retrieves the full set of API credentials (tenant ID, client ID, client secret, and subdomain) from AWS Secrets Manager at execution time.

This approach is suited for automated and scheduled workflows where interactive credential prompts are not practical, such as CI/CD pipelines, cron jobs, or serverless functions.

## Security Note

This project uses AWS Secrets Manager for all credential storage and retrieval.
No secrets, tokens, or tenant-specific identifiers are stored in the repository.
All examples use placeholder values.

## Configuration & Variables

This project uses environment variables to configure the AWS Secrets Manager lookup.

Required environment variables:

- `AWS_SECRET_NAME` – Name of the secret in AWS Secrets Manager
- `AWS_REGION` – AWS region where the secret is stored (defaults to `us-east-2`)

The AWS secret itself must contain the following keys:

- `identity_tenant_id` – CyberArk Identity tenant ID
- `subdomain` – Tenant subdomain for SCA and SIA API endpoints
- `client_id` – OAuth client ID for API authentication
- `client_secret` – OAuth client secret

AWS authentication is handled by the environment (IAM role, AWS CLI profile, or environment credentials). See `.env.example` for quick setup.

## What This Project Demonstrates

- OAuth 2.0 client credentials authentication against CyberArk Identity
- Secure bearer token generation
- AWS Secrets Manager integration for credential retrieval
- Authenticated REST API calls to SCA and SIA endpoints
- Retrieval and formatted display of access policies
- Zero-prompt execution suitable for automation pipelines

## Project Structure

```
cyberark-sca-sia-api-aws-secret/
├── get_sca_sia_policies_aws.py   # Retrieves all SCA and SIA policies
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## API Endpoints Used

The script interacts with three CyberArk cloud API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `https://<tenant>.id.cyberark.cloud/oauth2/platformtoken` | OAuth 2.0 token generation |
| `https://<subdomain>.sca.cyberark.cloud/api/policies` | Secure Cloud Access policy retrieval |
| `https://<subdomain>.uap.cyberark.cloud/api/policies` | Secure Infrastructure Access policy retrieval |

## AWS Secrets Manager Setup

Store your CyberArk credentials as a JSON secret in AWS Secrets Manager:

```json
{
  "identity_tenant_id": "your_tenant_id",
  "subdomain": "your_subdomain",
  "client_id": "your_client_id@cyberark.cloud.xxxxx",
  "client_secret": "your_client_secret"
}
```

The script's IAM principal (user, role, or instance profile) must have `secretsmanager:GetSecretValue` permission on the secret.

## Example Usage

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your AWS secret name and region

# Install dependencies
pip install -r requirements.txt

# Run the script (AWS credentials must be configured)
python3 get_sca_sia_policies_aws.py
```

Example output:

```
============================================================
CyberArk SCA & SIA Policy Retriever (AWS Secrets Manager)
============================================================

[1/4] Retrieving credentials from AWS Secrets Manager...
      ✓ Credentials retrieved
[2/4] Authenticating via OAuth 2.0...
      ✓ Bearer token acquired
[3/4] Retrieving SCA policies...
      ✓ Done
[4/4] Retrieving SIA policies...
      ✓ Done

============================================================
SCA POLICIES (sca.cyberark.cloud)
============================================================

  Name:        AWS Admin Access
  Description: Cloud admin policy for AWS workloads
  Status:      Active
  Policy ID:   a1b2c3d4-5678-90ab-cdef-example01

============================================================
TOTAL: 3 SCA + 2 SIA = 5 policies
============================================================
```

## Use Case

This project reflects common real-world security automation scenarios, such as:

- Automated policy auditing in CI/CD or scheduled workflows
- Secrets management integration for headless API automation
- Validating policy configurations during security evaluations
- Supporting presales demonstrations and proof of concept
- Bridging AWS and CyberArk ecosystems in cloud-first environments

## Disclaimer

This project is not affiliated with or officially supported by CyberArk or AWS.
It was created for learning and demonstration purposes using trial environments.
