"""AWS MFA session management.

Usage:
    uv run --with pyotp,boto3 python .claude/skills/bedrock-ops/scripts/session.py check
    uv run --with pyotp,boto3 python .claude/skills/bedrock-ops/scripts/session.py create
    uv run --with pyotp,boto3 python .claude/skills/bedrock-ops/scripts/session.py ensure

Commands:
    check   - Check if current session is valid. Exit 0=valid, 1=expired, 2=error.
    create  - Assume role with MFA using auto-generated TOTP code.
    ensure  - Check first, create if expired. Prints temp credentials as shell exports.
"""

import configparser
import json
import subprocess
import sys
import time
from pathlib import Path

import boto3
import pyotp


def find_project_root() -> Path:
    path = Path(__file__).resolve().parent.parent.parent.parent.parent
    if (path / "aws-project.json").exists():
        return path
    cwd = Path.cwd()
    if (cwd / "aws-project.json").exists():
        return cwd
    print("Error: aws-project.json not found.", file=sys.stderr)
    sys.exit(2)


def load_config(root: Path) -> dict:
    with open(root / "aws-project.json") as f:
        config = json.load(f)
    local_path = root / "aws-project.local.json"
    if local_path.exists():
        with open(local_path) as f:
            local = json.load(f)
        # Deep merge: local overrides shared
        for key, value in local.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            else:
                config[key] = value
    return config


def get_aws_profile_config(profile_name: str) -> dict:
    """Read a profile's settings from ~/.aws/config."""
    config = configparser.ConfigParser()
    config.read(Path.home() / ".aws" / "config")
    section = f"profile {profile_name}"
    if section not in config:
        return {}
    return dict(config[section])


def check_session(profile: str) -> bool:
    """Check if current session is valid."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(json.dumps(identity, indent=2))
            return True
        return False
    except (subprocess.TimeoutExpired, Exception):
        return False


def create_session(config: dict) -> dict:
    """Assume role with MFA using TOTP code. Returns temp credentials."""
    profile_config = get_aws_profile_config(config["profile"])
    role_arn = profile_config.get("role_arn")
    source_profile = config.get("auth", {}).get("source_profile") or profile_config.get("source_profile")
    mfa_serial = config.get("mfa_serial") or profile_config.get("mfa_serial")

    if not role_arn:
        print(f"Error: role_arn not found for profile '{config['profile']}'", file=sys.stderr)
        sys.exit(2)

    if not mfa_serial:
        print("Error: mfa_serial not found in local config or AWS profile", file=sys.stderr)
        sys.exit(2)

    # Generate TOTP code
    totp_secret = config.get("totp_secret")
    if not totp_secret or totp_secret == "REPLACE_WITH_YOUR_TOTP_SECRET":
        print("Error: totp_secret not configured in aws-project.local.json", file=sys.stderr)
        print("Replace it with your actual base32 TOTP secret.", file=sys.stderr)
        sys.exit(2)

    try:
        totp = pyotp.TOTP(totp_secret)
    except Exception as e:
        print(f"Error: Invalid TOTP secret: {e}", file=sys.stderr)
        sys.exit(2)

    # Try assume-role, retry once if TOTP timing issue
    for attempt in range(2):
        code = totp.now()
        try:
            # Use source profile credentials
            session = boto3.Session(profile_name=source_profile)
            sts = session.client("sts")
            response = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName="claude-aws-skill",
                SerialNumber=mfa_serial,
                TokenCode=code,
                DurationSeconds=3600,
            )
            creds = response["Credentials"]
            return {
                "AccessKeyId": creds["AccessKeyId"],
                "SecretAccessKey": creds["SecretAccessKey"],
                "SessionToken": creds["SessionToken"],
                "Expiration": creds["Expiration"].isoformat(),
                "Account": config.get("account_id", "unknown"),
                "Profile": config["profile"],
            }
        except Exception as e:
            if attempt == 0 and "invalid MFA" in str(e).lower():
                # Wait for next TOTP window and retry
                time.sleep(5)
                continue
            err = str(e)
            print(f"Error assuming role: {err}", file=sys.stderr)
            if "MultiFactorAuthentication" in err or "AccessDenied" in err:
                print(
                    "Hint: mfa_serial must be the ARN of the MFA device in the SOURCE IAM account "
                    "(the account where your IAM user lives, e.g. arn:aws:iam::123456789012:mfa/your-username), "
                    "NOT the target account you are assuming a role into.",
                    file=sys.stderr,
                )
            sys.exit(1)

    # Should not reach here, but satisfy type checker
    print("Error: Failed to assume role after retries.", file=sys.stderr)
    sys.exit(1)


def write_credentials_file(creds: dict, profile: str):
    """Write temp credentials to ~/.aws/credentials under a session profile."""
    creds_path = Path.home() / ".aws" / "credentials"
    config = configparser.ConfigParser()
    config.read(creds_path)

    session_profile = f"{profile}-session"
    if session_profile not in config:
        config.add_section(session_profile)
    config.set(session_profile, "aws_access_key_id", creds["AccessKeyId"])
    config.set(session_profile, "aws_secret_access_key", creds["SecretAccessKey"])
    config.set(session_profile, "aws_session_token", creds["SessionToken"])

    with open(creds_path, "w") as f:
        config.write(f)

    return session_profile


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("check", "create", "ensure"):
        print("Usage: session.py {check|create|ensure}", file=sys.stderr)
        sys.exit(2)

    command = sys.argv[1]
    root = find_project_root()
    config = load_config(root)
    profile = config["profile"]

    if command == "check":
        if check_session(profile):
            sys.exit(0)
        else:
            # Try session profile
            if check_session(f"{profile}-session"):
                sys.exit(0)
            print("Session expired or not found.", file=sys.stderr)
            sys.exit(1)

    elif command == "create":
        if not config.get("auth", {}).get("mfa_required", True):
            print("MFA not required for this profile. Use --profile directly.")
            sys.exit(0)
        creds = create_session(config)
        session_profile = write_credentials_file(creds, profile)
        print(f"Session created. Use --profile {session_profile}")
        print(f"Expires: {creds['Expiration']}")
        # Output as JSON for programmatic use
        print(json.dumps({"session_profile": session_profile, **creds}))

    elif command == "ensure":
        # Check if existing session works
        if check_session(f"{profile}-session"):
            print(f"Session valid. Profile: {profile}-session")
            sys.exit(0)
        if not config.get("auth", {}).get("mfa_required", True):
            # No MFA needed, check direct profile
            if check_session(profile):
                sys.exit(0)
            print("Error: Cannot authenticate with profile.", file=sys.stderr)
            sys.exit(1)
        # Create new session
        creds = create_session(config)
        session_profile = write_credentials_file(creds, profile)
        print(f"New session created. Profile: {session_profile}")
        print(f"Expires: {creds['Expiration']}")


if __name__ == "__main__":
    main()
