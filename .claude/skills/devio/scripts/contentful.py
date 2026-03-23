#!/usr/bin/env python3
"""Contentful CMA CLI — keeps credentials out of LLM context.

Usage:
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py setup [--check]
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py get <article-file>
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py create <article-file> --excerpt "..."
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py update <article-file> --excerpt "..."
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py tags --refresh
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py tags --search <query>
    python3 ${CLAUDE_SKILL_DIR}/scripts/contentful.py tags --resolve <name1> [name2 ...]

All output is JSON to stdout. Errors go to stderr with non-zero exit.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Project root is the current working directory (script is always invoked from project root)
ROOT = Path.cwd()
ENV_PATH = ROOT / ".env"
CONFIG_PATH = ROOT / ".claude" / "contentful-config.json"
TAGS_CACHE_PATH = ROOT / ".claude" / "tags-cache.json"

TAGS_CACHE_MAX_AGE_DAYS = 7

BASE_URL = "https://api.contentful.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def die(msg: str) -> None:
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(1)


def load_token() -> str:
    if not ENV_PATH.exists():
        die(f".env not found at {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "CONTENTFUL_CMA_TOKEN":
            value = value.strip().strip('"').strip("'")
            if value:
                return value
    die("CONTENTFUL_CMA_TOKEN not set in .env")
    return ""  # unreachable


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        die(f"Config not found at {CONFIG_PATH}. Run setup first.")
    return json.loads(CONFIG_PATH.read_text())


def api_request(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
    extra_headers: dict | None = None,
) -> dict:
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
        except json.JSONDecodeError:
            err_json = {"raw": err_body}
        die(f"HTTP {e.code}: {json.dumps(err_json)}")
        return {}  # unreachable


# ---------------------------------------------------------------------------
# Frontmatter parser (stdlib only)
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath: str) -> tuple[dict, str]:
    """Returns (frontmatter_dict, body_content)."""
    text = Path(filepath).read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        die(f"No YAML frontmatter found in {filepath}")
        return {}, ""

    fm_text, body = m.group(1), m.group(2)
    fm: dict = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for line in fm_text.split("\n"):
        # List item under current key
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_key:
            if current_list is None:
                current_list = []
            current_list.append(list_match.group(1).strip().strip('"').strip("'"))
            continue

        # Flush previous list
        if current_list is not None and current_key:
            fm[current_key] = current_list
            current_list = None
            current_key = None

        # Key: value pair
        kv_match = re.match(r'^(\w+)\s*:\s*(.*)$', line)
        if kv_match:
            key = kv_match.group(1)
            val = kv_match.group(2).strip().strip('"').strip("'")
            if val:
                fm[key] = val
                current_key = None
            else:
                # Value on next lines (list)
                current_key = key
                current_list = None

    # Flush trailing list
    if current_list is not None and current_key:
        fm[current_key] = current_list

    return fm, body


# ---------------------------------------------------------------------------
# Tag cache helpers
# ---------------------------------------------------------------------------

def load_tags_cache() -> list[dict]:
    """Load cached tag list. Dies if cache missing, warns if stale."""
    if not TAGS_CACHE_PATH.exists():
        die("Tag cache not found. Run: tags --refresh")
    data = json.loads(TAGS_CACHE_PATH.read_text(encoding="utf-8"))
    fetched_at = data.get("fetched_at", "")
    if fetched_at:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at)
        if age.days > TAGS_CACHE_MAX_AGE_DAYS:
            print(
                json.dumps({"warning": f"Tag cache is {age.days} days old. Consider running: tags --refresh"}),
                file=sys.stderr,
            )
    return data.get("tags", [])


def fetch_tags_from_api(token: str, config: dict) -> list[dict]:
    """Fetch the master tag list from the blogTags content type."""
    locale = config.get("locale", "en-US")
    data = api_request(
        "GET",
        f"/spaces/{config['space_id']}/environments/{config['environment_id']}/entries?content_type=blogTags&limit=1",
        token,
    )
    items = data.get("items", [])
    if not items:
        die("No blogTags entry found in Contentful")
    return items[0].get("fields", {}).get("tags", {}).get(locale, [])


def resolve_tag_names(names: list[str], tags: list[dict]) -> list[str]:
    """Convert human-readable tag names to numeric ID strings.

    Matches case-insensitively on the tag 'name' field.
    Dies with suggestions if a tag cannot be resolved.
    """
    name_to_id: dict[str, str] = {}
    for t in tags:
        name_to_id[t["name"].lower()] = str(t["id"])

    resolved = []
    for name in names:
        tag_id = name_to_id.get(name.lower())
        if tag_id:
            resolved.append(tag_id)
        else:
            # Find close matches for helpful error
            suggestions = [
                t["name"] for t in tags
                if name.lower() in t["name"].lower() or name.lower() in t["slug"].lower()
            ][:10]
            hint = f" Did you mean: {', '.join(suggestions)}" if suggestions else ""
            die(f"Tag not found: \"{name}\".{hint}")
    return resolved


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_setup(args: list[str]) -> None:
    """Auto-detect and save Contentful config, or check existing."""
    if "--check" in args:
        if CONFIG_PATH.exists():
            config = load_config()
            token = load_token()
            # Verify token works with a lightweight call
            api_request("GET", f"/spaces/{config['space_id']}", token)
            print(json.dumps({"ok": True, "space_id": config["space_id"]}))
        else:
            has_token = False
            try:
                load_token()
                has_token = True
            except SystemExit:
                pass
            print(json.dumps({"ok": False, "has_token": has_token, "has_config": False}))
        return

    token = load_token()

    if "--list-spaces" in args:
        data = api_request("GET", "/spaces", token)
        spaces = [{"id": s["sys"]["id"], "name": s["name"]} for s in data.get("items", [])]
        print(json.dumps({"spaces": spaces}))
        return

    if "--list-authors" in args:
        space_id = _require_arg(args, "--space-id")
        env_id = _require_arg(args, "--env-id", default="master")
        data = api_request(
            "GET",
            f"/spaces/{space_id}/environments/{env_id}/entries?content_type=authorProfile&limit=100",
            token,
        )
        authors = []
        for item in data.get("items", []):
            fields = item.get("fields", {})
            # Try common field names for author display
            name = (
                fields.get("name", {}).get("en-US", "")
                or fields.get("displayName", {}).get("en-US", "")
                or item["sys"]["id"]
            )
            authors.append({"id": item["sys"]["id"], "name": name})
        print(json.dumps({"authors": authors}))
        return

    if "--list-content-types" in args:
        space_id = _require_arg(args, "--space-id")
        env_id = _require_arg(args, "--env-id", default="master")
        data = api_request(
            "GET",
            f"/spaces/{space_id}/environments/{env_id}/content_types",
            token,
        )
        types = [{"id": ct["sys"]["id"], "name": ct["name"]} for ct in data.get("items", [])]
        print(json.dumps({"content_types": types}))
        return

    if "--describe-content-type" in args:
        space_id = _require_arg(args, "--space-id")
        env_id = _require_arg(args, "--env-id", default="master")
        ct_id = _require_arg(args, "--content-type-id", default="blogPost")
        data = api_request(
            "GET",
            f"/spaces/{space_id}/environments/{env_id}/content_types/{ct_id}",
            token,
        )
        fields = [
            {
                "id": f["id"],
                "name": f["name"],
                "type": f["type"],
                "items": f.get("items"),
                "validations": f.get("validations"),
            }
            for f in data.get("fields", [])
        ]
        print(json.dumps({"fields": fields}, ensure_ascii=False))
        return

    if "--save" in args:
        space_id = _require_arg(args, "--space-id")
        env_id = _require_arg(args, "--env-id", default="master")
        content_type_id = _require_arg(args, "--content-type-id", default="blogPost")
        author_id = _require_arg(args, "--author-id")
        locale = _require_arg(args, "--locale", default="en-US")

        config = {
            "space_id": space_id,
            "environment_id": env_id,
            "content_type_id": content_type_id,
            "author_id": author_id,
            "locale": locale,
            "fields": {
                "title": "title",
                "slug": "slug",
                "content": "content",
                "tags": "tags",
                "excerpt": "excerpt",
                "author": "author",
                "language": "language",
            },
        }
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")
        print(json.dumps({"ok": True, "config_path": str(CONFIG_PATH)}))
        return

    die("setup requires one of: --check, --list-spaces, --list-authors, --list-content-types, --describe-content-type, --save")


def cmd_get(args: list[str]) -> None:
    """Fetch an existing Contentful entry for a published article."""
    if not args:
        die("Usage: get <article-file>")

    filepath = args[0]
    fm, _ = parse_frontmatter(filepath)
    article_id = fm.get("articleId")
    if not article_id:
        die("No articleId in frontmatter — article has not been published yet")

    token = load_token()
    config = load_config()
    locale = config.get("locale", "en-US")

    entry = api_request(
        "GET",
        f"/spaces/{config['space_id']}/environments/{config['environment_id']}/entries/{article_id}",
        token,
    )

    version = entry["sys"]["version"]
    fields = entry.get("fields", {})

    # Extract localized values for comparison
    raw_tags = fields.get("tags", {}).get(locale, [])
    try:
        tag_cache = load_tags_cache()
        id_to_name = {str(t["id"]): t["name"] for t in tag_cache}
        display_tags = [id_to_name.get(t, t) for t in raw_tags]
    except SystemExit:
        display_tags = raw_tags

    result = {
        "entry_id": article_id,
        "version": version,
        "title": fields.get("title", {}).get(locale, ""),
        "slug": fields.get("slug", {}).get(locale, ""),
        "content": fields.get("content", {}).get(locale, ""),
        "tags": display_tags,
        "tag_ids": raw_tags,
        "excerpt": fields.get("excerpt", {}).get(locale, ""),
        "url": f"https://app.contentful.com/spaces/{config['space_id']}/entries/{article_id}",
    }
    print(json.dumps(result, ensure_ascii=False))


def cmd_create(args: list[str]) -> None:
    """Create a new draft entry in Contentful."""
    if not args:
        die("Usage: create <article-file> --excerpt '...'")

    filepath = args[0]
    excerpt = _require_arg(args, "--excerpt")

    fm, body = parse_frontmatter(filepath)
    if fm.get("articleId"):
        die("Article already has articleId — use 'update' instead")

    token = load_token()
    config = load_config()
    locale = config.get("locale", "en-US")

    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags = resolve_tag_names(tags, load_tags_cache())

    entry_body = {
        "fields": {
            "title": {locale: fm.get("title", "")},
            "slug": {locale: fm.get("slug", "")},
            "content": {locale: body},
            "tags": {locale: tags},
            "excerpt": {locale: excerpt},
            "language": {locale: "ja"},
            "targetLocales": {locale: ["en"]},
            "author": {
                locale: {
                    "sys": {
                        "type": "Link",
                        "linkType": "Entry",
                        "id": config["author_id"],
                    }
                }
            },
        }
    }

    entry = api_request(
        "POST",
        f"/spaces/{config['space_id']}/environments/{config['environment_id']}/entries",
        token,
        body=entry_body,
        extra_headers={"X-Contentful-Content-Type": config["content_type_id"]},
    )

    entry_id = entry["sys"]["id"]
    print(json.dumps({
        "entry_id": entry_id,
        "url": f"https://app.contentful.com/spaces/{config['space_id']}/entries/{entry_id}",
    }))


def cmd_update(args: list[str]) -> None:
    """Update an existing draft entry in Contentful (fetch-merge-put)."""
    if not args:
        die("Usage: update <article-file> --excerpt '...'")

    filepath = args[0]
    excerpt = _require_arg(args, "--excerpt")

    fm, body = parse_frontmatter(filepath)
    article_id = fm.get("articleId")
    if not article_id:
        die("No articleId in frontmatter — use 'create' instead")

    token = load_token()
    config = load_config()
    locale = config.get("locale", "en-US")

    # Fetch existing entry
    entry = api_request(
        "GET",
        f"/spaces/{config['space_id']}/environments/{config['environment_id']}/entries/{article_id}",
        token,
    )
    version = entry["sys"]["version"]
    fields = entry.get("fields", {})

    # Merge local fields only
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags = resolve_tag_names(tags, load_tags_cache())

    fields["title"] = {locale: fm.get("title", "")}
    fields["slug"] = {locale: fm.get("slug", "")}
    fields["content"] = {locale: body}
    fields["tags"] = {locale: tags}
    fields["excerpt"] = {locale: excerpt}
    fields["targetLocales"] = {locale: ["en"]}

    # PUT with version header
    updated = api_request(
        "PUT",
        f"/spaces/{config['space_id']}/environments/{config['environment_id']}/entries/{article_id}",
        token,
        body={"fields": fields},
        extra_headers={"X-Contentful-Version": str(version)},
    )

    new_version = updated["sys"]["version"]
    print(json.dumps({
        "entry_id": article_id,
        "version": new_version,
        "url": f"https://app.contentful.com/spaces/{config['space_id']}/entries/{article_id}",
    }))


def cmd_tags(args: list[str]) -> None:
    """Manage the local tag cache and search/resolve tags."""
    if "--refresh" in args:
        token = load_token()
        config = load_config()
        tags = fetch_tags_from_api(token, config)
        cache = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tags": tags,
        }
        TAGS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TAGS_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "count": len(tags)}))
        return

    if "--search" in args:
        query = _require_arg(args, "--search")
        tags = load_tags_cache()
        q = query.lower()
        results = [
            {"id": t["id"], "name": t["name"], "slug": t["slug"]}
            for t in tags
            if q in t["name"].lower() or q in t["slug"].lower()
        ][:20]
        print(json.dumps({"query": query, "count": len(results), "results": results}, ensure_ascii=False))
        return

    if "--resolve" in args:
        try:
            idx = args.index("--resolve")
            names = args[idx + 1:]
        except (ValueError, IndexError):
            names = []
        if not names:
            die("Usage: tags --resolve <name1> [name2 ...]")
        tags = load_tags_cache()
        resolved = resolve_tag_names(names, tags)
        print(json.dumps({"resolved": dict(zip(names, resolved))}))
        return

    die("tags requires one of: --refresh, --search, --resolve")


# ---------------------------------------------------------------------------
# Arg parsing helpers
# ---------------------------------------------------------------------------

def _require_arg(args: list[str], flag: str, default: str | None = None) -> str:
    try:
        idx = args.index(flag)
        return args[idx + 1]
    except (ValueError, IndexError):
        if default is not None:
            return default
        die(f"Missing required argument: {flag}")
        return ""  # unreachable


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMANDS = {
    "setup": cmd_setup,
    "get": cmd_get,
    "create": cmd_create,
    "update": cmd_update,
    "tags": cmd_tags,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(0 if sys.argv[1:] == ["--help"] else 1)

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        die(f"Unknown command: {cmd_name}. Available: {', '.join(COMMANDS)}")

    COMMANDS[cmd_name](sys.argv[2:])


if __name__ == "__main__":
    main()
