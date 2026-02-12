#!/usr/bin/env python3
"""
CyberArk SCA and SIA Policy Retriever (AWS Secrets Manager)
============================================================
Retrieves all Secure Cloud Access (SCA) and Secure Infrastructure Access (SIA) policies
from CyberArk using the platform API. Authenticates via OAuth 2.0 client credentials
with all secrets stored in and retrieved from AWS Secrets Manager — no plaintext
credentials in code or environment variables.

Usage: python3 get_sca_sia_policies_aws.py
"""

import os
import json
import boto3
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
SECRET_NAME = os.getenv("AWS_SECRET_NAME")
REGION = os.getenv("AWS_REGION", "us-east-2")


def get_secret() -> dict:
    """Retrieve CyberArk API credentials from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(response["SecretString"])


def get_token(secret: dict) -> str:
    """Authenticate via OAuth 2.0 client credentials and return a bearer token."""
    url = f"https://{secret['identity_tenant_id']}.id.cyberark.cloud/oauth2/platformtoken"
    data = {
        "grant_type": "client_credentials",
        "client_id": secret["client_id"],
        "client_secret": secret["client_secret"],
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_sca_policies(subdomain: str, token: str) -> dict:
    """Retrieve all Secure Cloud Access (SCA) policies."""
    url = f"https://{subdomain}.sca.cyberark.cloud/api/policies"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return response.json()


def get_sia_policies(subdomain: str, token: str) -> dict:
    """Retrieve all Secure Infrastructure Access (SIA) policies."""
    url = f"https://{subdomain}.uap.cyberark.cloud/api/policies"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return response.json()


def display_sca_policies(sca_data: dict):
    """Format and display SCA policy results."""
    print("\n" + "=" * 60)
    print("SCA POLICIES (sca.cyberark.cloud)")
    print("=" * 60)
    for policy in sca_data.get("hits", []):
        print(f"\n  Name:        {policy.get('name')}")
        print(f"  Description: {policy.get('description')}")
        print(f"  Status:      {'Active' if policy.get('status') == 1 else 'Inactive'}")
        print(f"  Policy ID:   {policy.get('policyId')}")


def display_sia_policies(sia_data: dict):
    """Format and display SIA policy results."""
    print("\n" + "=" * 60)
    print("SIA POLICIES (uap.cyberark.cloud)")
    print("=" * 60)
    for policy in sia_data.get("results", []):
        metadata = policy.get("metadata", {})
        print(f"\n  Name:        {metadata.get('name')}")
        print(f"  Description: {metadata.get('description')}")
        print(f"  Status:      {metadata.get('status', {}).get('status')}")
        print(f"  Policy ID:   {metadata.get('policyId')}")


def main():
    print("=" * 60)
    print("CyberArk SCA & SIA Policy Retriever (AWS Secrets Manager)")
    print("=" * 60)

    # Validate environment variables
    if not SECRET_NAME:
        print("\n[ERROR] Missing AWS_SECRET_NAME environment variable.")
        print("Set AWS_SECRET_NAME in your .env file or environment.")
        print("See .env.example for reference.")
        return

    # Retrieve credentials from AWS Secrets Manager
    print("\n[1/4] Retrieving credentials from AWS Secrets Manager...")
    secret = get_secret()
    print("      ✓ Credentials retrieved")

    # Authenticate
    print("[2/4] Authenticating via OAuth 2.0...")
    token = get_token(secret)
    print("      ✓ Bearer token acquired")

    # Retrieve SCA policies
    print("[3/4] Retrieving SCA policies...")
    sca_data = get_sca_policies(secret["subdomain"], token)
    print("      ✓ Done")

    # Retrieve SIA policies
    print("[4/4] Retrieving SIA policies...")
    sia_data = get_sia_policies(secret["subdomain"], token)
    print("      ✓ Done")

    # Display results
    display_sca_policies(sca_data)
    display_sia_policies(sia_data)

    # Summary
    sca_total = sca_data.get("total", 0)
    sia_total = sia_data.get("total", 0)
    print("\n" + "=" * 60)
    print(f"TOTAL: {sca_total} SCA + {sia_total} SIA = {sca_total + sia_total} policies")
    print("=" * 60)


if __name__ == "__main__":
    main()
