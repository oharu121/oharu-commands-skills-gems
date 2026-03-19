"""Interactive AWS project configuration generator.

Usage:
    uv run python .claude/skills/aws/scripts/setup_project.py

Parses ~/.aws/config for available profiles, then generates aws-project.json.
"""

import configparser
import json
import re
import sys
from pathlib import Path


def parse_aws_config() -> dict[str, dict]:
    """Parse ~/.aws/config and return dict of profile_name -> settings."""
    config = configparser.ConfigParser()
    config_path = Path.home() / ".aws" / "config"
    if not config_path.exists():
        print("Error: ~/.aws/config not found.", file=sys.stderr)
        sys.exit(1)
    config.read(config_path)

    profiles = {}
    for section in config.sections():
        name = section.replace("profile ", "") if section.startswith("profile ") else section
        profiles[name] = dict(config[section])
    return profiles


def extract_account_id(role_arn: str) -> str | None:
    """Extract 12-digit account ID from a role ARN."""
    match = re.search(r":(\d{12}):", role_arn)
    return match.group(1) if match else None


def generate_config(profile_name: str, profile_settings: dict) -> dict:
    """Generate aws-project.json content from a profile."""
    role_arn = profile_settings.get("role_arn", "")
    account_id = extract_account_id(role_arn) or ""
    region = profile_settings.get("region", "ap-northeast-1")
    source_profile = profile_settings.get("source_profile")
    mfa_serial = profile_settings.get("mfa_serial")

    config = {
        "version": 1,
        "profile": profile_name,
        "account_id": account_id,
        "region": region,
        "auth": {
            "type": "role_assumption" if role_arn else "direct",
            "source_profile": source_profile,
            "mfa_required": bool(mfa_serial),
        },
        "defaults": {
            "s3_bucket": None,
            "s3_prefix": "",
        },
        "safety": {
            "require_identity_check": True,
            "require_dry_run": True,
            "block_delete_without_confirmation": True,
            "denied_services": ["iam", "organizations"],
            "max_s3_sync_size_mb": 500,
        },
        "tags": {
            "Project": "",
            "ManagedBy": "",
        },
    }

    local_config = {}
    if mfa_serial:
        local_config["mfa_serial"] = mfa_serial
        local_config["totp_secret"] = "REPLACE_WITH_YOUR_TOTP_SECRET"

    return config, local_config


def main():
    profiles = parse_aws_config()

    if not profiles:
        print("No profiles found in ~/.aws/config")
        sys.exit(1)

    # Output profiles as JSON for Claude to present to user
    output = {
        "profiles": {},
        "instructions": "Select a profile to generate aws-project.json"
    }

    for name, settings in profiles.items():
        role_arn = settings.get("role_arn", "")
        account_id = extract_account_id(role_arn) or "N/A"
        output["profiles"][name] = {
            "account_id": account_id,
            "role_arn": role_arn or "direct",
            "region": settings.get("region", "ap-northeast-1"),
            "source_profile": settings.get("source_profile", "N/A"),
            "mfa_required": bool(settings.get("mfa_serial")),
        }

    # If a profile name was passed as argument, generate config directly
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
        if profile_name not in profiles:
            print(f"Error: Profile '{profile_name}' not found.", file=sys.stderr)
            print(f"Available: {', '.join(profiles.keys())}", file=sys.stderr)
            sys.exit(1)

        config, local_config = generate_config(profile_name, profiles[profile_name])

        # Optional: s3 bucket from argv[2]
        if len(sys.argv) > 2:
            config["defaults"]["s3_bucket"] = sys.argv[2]

        # Write files
        root = Path.cwd()
        config_path = root / "aws-project.json"
        local_path = root / "aws-project.local.json"

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Created: {config_path}")

        if local_config:
            if local_path.exists():
                print(f"Skipped: {local_path} already exists")
            else:
                with open(local_path, "w") as f:
                    json.dump(local_config, f, indent=2, ensure_ascii=False)
                print(f"Created: {local_path}")
                print("⚠ Update totp_secret in aws-project.local.json with your actual TOTP secret")

        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        # Just list profiles
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
