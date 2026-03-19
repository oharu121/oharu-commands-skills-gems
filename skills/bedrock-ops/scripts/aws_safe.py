"""AWS CLI safety wrapper.

Usage:
    uv run --with pyotp,boto3 python .claude/skills/bedrock-ops/scripts/aws_safe.py <aws-cli-args...>

Examples:
    aws_safe.py s3 ls
    aws_safe.py s3 sync ./output s3://bucket/path
    aws_safe.py s3 sync ./output s3://bucket/path --execute
    aws_safe.py s3 cp ./output s3://bucket/ --recursive --execute   # force-upload: bypasses sync size check
    aws_safe.py ce get-cost-and-usage --time-period ...

Safety enforced:
    1. Always injects --profile from aws-project.json
    2. Verifies account ID before write operations
    3. Dry-run before sync/deploy (add --execute to run for real)
    4. Blocks denied services
    5. Blocks --delete unless --i-understand-this-deletes is passed
    6. Auto-refreshes expired sessions
"""

import json
import subprocess
import sys
from pathlib import Path

# Operation classification
READ_VERBS = {"ls", "list", "describe", "get", "head", "get-caller-identity",
              "get-cost-and-usage", "get-cost-forecast", "get-metric-data"}
WRITE_VERBS = {"put", "create", "update", "sync", "upload", "cp", "mv",
               "start", "invoke", "run", "deploy", "publish", "tag"}
DESTRUCTIVE_VERBS = {"delete", "remove", "terminate", "deregister", "purge",
                     "rm", "destroy"}
DRYRUN_SUPPORTED = {"s3 sync", "s3 cp", "s3 mv", "s3 rm"}


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
        for key, value in local.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            else:
                config[key] = value
    return config


def classify_operation(args: list[str]) -> str:
    """Classify AWS CLI args as 'read', 'write', or 'destructive'."""
    # Check for --delete flag anywhere
    if "--delete" in args:
        return "destructive"

    # Find the service and verb
    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) >= 2:
        verb = non_flag_args[1].lower()
    elif len(non_flag_args) >= 1:
        verb = non_flag_args[0].lower()
    else:
        return "read"

    if verb in DESTRUCTIVE_VERBS:
        return "destructive"
    if verb in WRITE_VERBS:
        return "write"
    return "read"


def get_service_and_command(args: list[str]) -> tuple[str, str]:
    """Extract service name and full command from args."""
    non_flag = [a for a in args if not a.startswith("-")]
    service = non_flag[0] if non_flag else "unknown"
    command = " ".join(non_flag[:2]) if len(non_flag) >= 2 else service
    return service, command


def supports_dryrun(args: list[str]) -> bool:
    non_flag = [a for a in args if not a.startswith("-")]
    command = " ".join(non_flag[:2]) if len(non_flag) >= 2 else ""
    return command in DRYRUN_SUPPORTED


def verify_identity(profile: str, expected_account: str) -> bool:
    """Verify current identity matches expected account."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False
        identity = json.loads(result.stdout)
        actual_account = identity.get("Account", "")
        return actual_account == expected_account
    except Exception:
        return False


def print_banner(operation_type: str, profile: str, account: str, region: str,
                 command_str: str, mode: str):
    """Print confirmation banner."""
    type_label = {
        "read": "AWS READ OPERATION",
        "write": "AWS WRITE OPERATION",
        "destructive": "⚠ AWS DESTRUCTIVE OPERATION ⚠",
    }[operation_type]

    check = "✓" if verify_identity(profile, account) else "✗ MISMATCH"

    print("══════════════════════════════════════════════")
    print(f"  {type_label}")
    print(f"  Profile:  {profile}")
    print(f"  Account:  {account} {check}")
    print(f"  Region:   {region}")
    print(f"  Command:  aws {command_str}")
    print(f"  Mode:     {mode}")
    print("══════════════════════════════════════════════")
    print()


def ensure_session(config: dict, root: Path) -> str:
    """Ensure we have a valid session. Returns the profile to use."""
    profile = config["profile"]
    session_profile = f"{profile}-session"

    # Try session profile first (has temp creds from previous assume-role)
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", session_profile],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return session_profile
    except Exception:
        pass

    # Try base profile (may have cached MFA session)
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return profile
    except Exception:
        pass

    # Need to create a new session
    if config.get("auth", {}).get("mfa_required", True):
        print("Session expired. Creating new MFA session...", file=sys.stderr)
        scripts_dir = root / ".claude" / "skills" / "bedrock-ops" / "scripts"
        result = subprocess.run(
            ["uv", "run", "--with", "pyotp,boto3", "python",
             str(scripts_dir / "session.py"), "create"],
            capture_output=True, text=True, cwd=str(root)
        )
        if result.returncode == 0:
            return session_profile
        else:
            print(f"Failed to create session: {result.stderr}", file=sys.stderr)
            sys.exit(1)

    return profile


def main():
    if len(sys.argv) < 2:
        print("Usage: aws_safe.py <aws-cli-args...>", file=sys.stderr)
        print("       aws_safe.py s3 ls", file=sys.stderr)
        print("       aws_safe.py s3 sync ./dir s3://bucket/ --execute", file=sys.stderr)
        sys.exit(2)

    root = find_project_root()
    config = load_config(root)
    safety = config.get("safety", {})

    # Separate our custom flags from AWS args
    aws_args = []
    execute_mode = False
    force_delete = False
    for arg in sys.argv[1:]:
        if arg == "--execute":
            execute_mode = True
        elif arg == "--i-understand-this-deletes":
            force_delete = True
        else:
            aws_args.append(arg)

    # Check denied services
    service, command_str = get_service_and_command(aws_args)
    denied = safety.get("denied_services", [])
    if service in denied:
        print(f"Error: Service '{service}' is in the denied list.", file=sys.stderr)
        print(f"Denied services: {denied}", file=sys.stderr)
        sys.exit(1)

    # Classify operation
    op_type = classify_operation(aws_args)

    # Block destructive without explicit flag
    if op_type == "destructive" and not force_delete:
        if safety.get("block_delete_without_confirmation", True):
            print("Error: Destructive operation blocked.", file=sys.stderr)
            print("Add --i-understand-this-deletes to proceed.", file=sys.stderr)
            sys.exit(1)

    # Ensure valid session
    profile = ensure_session(config, root)
    account = config.get("account_id", "unknown")
    region = config.get("region", "ap-northeast-1")

    # For write/destructive ops, verify identity
    if op_type in ("write", "destructive"):
        if safety.get("require_identity_check", True):
            if not verify_identity(profile, account):
                print(f"Error: Account mismatch! Expected {account}.", file=sys.stderr)
                sys.exit(1)

    # Handle dry-run for supported commands
    if op_type in ("write", "destructive") and supports_dryrun(aws_args):
        if not execute_mode and safety.get("require_dry_run", True):
            # Dry-run mode
            print_banner(op_type, profile, account, region,
                        " ".join(aws_args), "DRY-RUN")
            cmd = ["aws"] + aws_args + ["--profile", profile, "--region", region, "--dryrun"]
            result = subprocess.run(cmd)
            print()
            print("Above is a DRY-RUN. Add --execute to run for real.")
            sys.exit(result.returncode)
        else:
            # Execute mode
            print_banner(op_type, profile, account, region,
                        " ".join(aws_args), "LIVE EXECUTION")
    elif op_type in ("write", "destructive"):
        print_banner(op_type, profile, account, region,
                    " ".join(aws_args),
                    "LIVE EXECUTION" if execute_mode else "EXECUTE")

    # Run the actual command — capture stderr to detect expired token, stdout still streams to terminal
    cmd = ["aws"] + aws_args + ["--profile", profile, "--region", region]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    # Handle expired token
    if result.returncode != 0:
        stderr = result.stderr or ""
        if "ExpiredToken" in stderr or "expired" in stderr.lower():
            print("Session expired. Refreshing...", file=sys.stderr)
            profile = ensure_session(config, root)
            cmd = ["aws"] + aws_args + ["--profile", profile, "--region", region]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
