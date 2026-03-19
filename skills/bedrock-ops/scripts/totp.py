"""Generate a TOTP MFA code from the project's local config.

Usage:
    uv run --with pyotp python .claude/skills/aws/scripts/totp.py

Reads totp_secret from aws-project.local.json and outputs a 6-digit code.
The secret never appears in stdout — only the code.
"""

import json
import sys
from pathlib import Path

import pyotp


def find_project_root() -> Path:
    """Walk up from script location to find aws-project.local.json."""
    # Script is at .claude/skills/aws/scripts/totp.py → project root is 4 levels up
    path = Path(__file__).resolve().parent.parent.parent.parent.parent
    local_config = path / "aws-project.local.json"
    if local_config.exists():
        return path
    # Also try cwd
    cwd = Path.cwd()
    if (cwd / "aws-project.local.json").exists():
        return cwd
    print("Error: aws-project.local.json not found.", file=sys.stderr)
    print("Create it with your TOTP secret:", file=sys.stderr)
    print('  {"totp_secret": "YOUR_BASE32_SECRET", "mfa_serial": "arn:aws:iam::..."}', file=sys.stderr)
    sys.exit(1)


def main():
    root = find_project_root()
    local_config = root / "aws-project.local.json"

    with open(local_config) as f:
        config = json.load(f)

    secret = config.get("totp_secret")
    if not secret:
        print("Error: totp_secret not found in aws-project.local.json", file=sys.stderr)
        sys.exit(1)

    if secret == "REPLACE_WITH_YOUR_TOTP_SECRET" or not secret.replace("=", "").isalnum():
        print("Error: Invalid totp_secret in aws-project.local.json", file=sys.stderr)
        print("Replace it with your actual base32 TOTP secret from your authenticator app setup.", file=sys.stderr)
        sys.exit(1)

    try:
        totp = pyotp.TOTP(secret)
        print(totp.now())
    except Exception as e:
        print(f"Error generating TOTP code: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
