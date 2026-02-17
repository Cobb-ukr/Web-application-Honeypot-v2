"""
playbook_loader.py — Loads attack playbook data from playbook.db and converts
verbose human-readable YAML/text into compact machine-readable JSON that can be
injected into the LLM prompt as attack context.

Tables in playbook.db:
- gtfobins (809 rows): binary, function, command_snippet, description
- atomic_red_team (324 rows): technique_id, technique_name, yaml_content
"""

import json
import os
import re
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "playbook.db")

# In-memory indexes (populated on first call)
_gtfobins_index = {}       # binary_name -> [{"function": ..., "cmd": ..., "desc": ...}]
_attack_index = {}          # technique_id -> {"name": ..., "commands": [...], "platform": ...}
_keyword_to_techniques = {} # keyword -> [technique_id, ...]
_loaded = False


def _load_playbook():
    """Load and index playbook.db once into memory."""
    global _gtfobins_index, _attack_index, _keyword_to_techniques, _loaded

    if _loaded:
        return

    if not os.path.exists(DB_PATH):
        logger.warning(f"Playbook DB not found at {DB_PATH}")
        _loaded = True
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # ── Load GTFOBins ──
        cursor.execute("SELECT binary, function, command_snippet, description FROM gtfobins")
        for binary, func, cmd, desc in cursor.fetchall():
            if binary not in _gtfobins_index:
                _gtfobins_index[binary] = []
            _gtfobins_index[binary].append({
                "function": func,
                "cmd": cmd,
                "desc": desc,
            })

        # ── Load Atomic Red Team ──
        cursor.execute("SELECT technique_id, technique_name, yaml_content FROM atomic_red_team")
        for tech_id, tech_name, yaml_content in cursor.fetchall():
            compact = _parse_yaml_to_compact(tech_id, tech_name, yaml_content)
            _attack_index[tech_id] = compact

            # Build keyword index from technique name and commands
            keywords = _extract_keywords(tech_name, compact.get("commands", []))
            for kw in keywords:
                if kw not in _keyword_to_techniques:
                    _keyword_to_techniques[kw] = []
                if tech_id not in _keyword_to_techniques[kw]:
                    _keyword_to_techniques[kw].append(tech_id)

        conn.close()
        _loaded = True
        logger.info(
            f"Playbook loaded: {len(_gtfobins_index)} GTFOBins binaries, "
            f"{len(_attack_index)} ATT&CK techniques, "
            f"{len(_keyword_to_techniques)} keywords indexed"
        )

    except Exception as e:
        logger.error(f"Failed to load playbook DB: {e}")
        _loaded = True


def _parse_yaml_to_compact(tech_id, tech_name, yaml_content):
    """
    Convert verbose YAML content into a compact dict with only the fields
    the LLM needs:
      - name: technique display name
      - platform: supported OS(es)
      - commands: list of actual command strings from executor blocks
      - description: short description (first sentence)
    """
    compact = {
        "name": tech_name,
        "platform": "",
        "commands": [],
        "description": "",
    }

    if not yaml_content:
        return compact

    # Extract platforms
    platform_match = re.findall(r"supported_platforms:\s*\n((?:\s*-\s*\w+\n?)+)", yaml_content)
    if platform_match:
        platforms = re.findall(r"-\s*(\w+)", platform_match[0])
        compact["platform"] = ", ".join(platforms)

    # Extract executor commands (the actual attack commands)
    cmd_blocks = re.findall(r"command:\s*\|?\s*\n((?:[ \t]+.+\n?)+)", yaml_content)
    for block in cmd_blocks:
        # Clean up indentation and extract meaningful command lines
        lines = block.strip().split("\n")
        for line in lines:
            line = line.strip()
            # Skip empty lines, comments, echo-only lines, and variable assignments
            if (line and
                not line.startswith("#") and
                not line.startswith("echo ") and
                len(line) > 3):
                compact["commands"].append(line)

    # Also capture single-line commands
    single_cmds = re.findall(r"command:\s*([^\n|]+)", yaml_content)
    for cmd in single_cmds:
        cmd = cmd.strip()
        if cmd and len(cmd) > 3:
            compact["commands"].append(cmd)

    # Deduplicate commands
    seen = set()
    unique_cmds = []
    for cmd in compact["commands"]:
        if cmd not in seen:
            seen.add(cmd)
            unique_cmds.append(cmd)
    compact["commands"] = unique_cmds[:10]  # Cap at 10 commands per technique

    # Extract first description
    desc_match = re.search(r"description:\s*\|?\s*\n\s+(.+)", yaml_content)
    if desc_match:
        compact["description"] = desc_match.group(1).strip()[:150]

    return compact


def _extract_keywords(tech_name, commands):
    """Extract searchable keywords from technique name and commands."""
    keywords = set()

    # Words from technique name
    for word in re.findall(r"[a-zA-Z]+", tech_name.lower()):
        if len(word) > 2:
            keywords.add(word)

    # Binary names from commands
    for cmd in commands:
        parts = cmd.strip().split()
        if parts:
            binary = parts[0].split("/")[-1].lower()  # Get basename
            binary = binary.replace(".exe", "")
            if len(binary) > 1:
                keywords.add(binary)

    return keywords


def get_relevant_context(command):
    """
    Given a terminal command, find relevant attack playbook entries.
    Returns a compact string suitable for injection into the LLM prompt.
    """
    _load_playbook()

    if not command:
        return ""

    parts = command.strip().split()
    cmd_binary = parts[0].lower() if parts else ""
    cmd_words = set(w.lower() for w in parts if len(w) > 2)

    context_parts = []

    # ── 1. Check GTFOBins for the binary ──
    if cmd_binary in _gtfobins_index:
        entries = _gtfobins_index[cmd_binary]
        gtfo_lines = []
        for entry in entries[:5]:  # Max 5 entries per binary
            gtfo_lines.append(f"  - {entry['function']}: {entry['cmd']} ({entry['desc']})")
        context_parts.append(
            f"[GTFOBins] '{cmd_binary}' can be exploited:\n" + "\n".join(gtfo_lines)
        )

    # ── 2. Check ATT&CK techniques by keyword match ──
    matched_techniques = set()
    for word in cmd_words:
        if word in _keyword_to_techniques:
            matched_techniques.update(_keyword_to_techniques[word])

    # Also check if the binary itself matches
    if cmd_binary in _keyword_to_techniques:
        matched_techniques.update(_keyword_to_techniques[cmd_binary])

    # Limit to top 3 most relevant techniques
    for tech_id in list(matched_techniques)[:3]:
        tech = _attack_index.get(tech_id, {})
        if tech:
            tech_str = f"[ATT&CK {tech_id}] {tech['name']}"
            if tech.get("platform"):
                tech_str += f" (platform: {tech['platform']})"
            if tech.get("description"):
                tech_str += f"\n  Description: {tech['description']}"
            if tech.get("commands"):
                tech_str += "\n  Commands: " + " | ".join(tech["commands"][:3])
            context_parts.append(tech_str)

    if not context_parts:
        return ""

    return "--- Attack Reference (from playbook database) ---\n" + "\n\n".join(context_parts)


def get_stats():
    """Return loader statistics for debugging."""
    _load_playbook()
    return {
        "gtfobins_binaries": len(_gtfobins_index),
        "attack_techniques": len(_attack_index),
        "keywords_indexed": len(_keyword_to_techniques),
        "db_path": DB_PATH,
        "db_exists": os.path.exists(DB_PATH),
    }
