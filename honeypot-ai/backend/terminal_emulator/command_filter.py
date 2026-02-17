import re
from typing import Tuple

HARDCODED_COMMANDS = {
    "help",
    "ls",
    "cat",
    "whoami",
    "pwd",
    "clear",
    "exit",
    "cd",
    "mkdir",
    "rm",
    "echo",
    "uname",
    "ps",
    "netstat",
}

BLOCKED_PATTERNS = [
    r"\b(rm\s+-rf\s+/)\b",
    r"\b(shutdown|reboot|init\s+0)\b",
    r"\b(mkfs|dd\s+if=|:\(\)\s*\{:\|:\s*&\}\s*;)\b",
]

MAX_COMMAND_LENGTH = 200
MAX_OUTPUT_LENGTH = 2000


def normalize_command(command: str) -> str:
    return (command or "").strip()


def should_use_llm(command: str) -> Tuple[bool, str]:
    """
    Returns (allowed, reason). Only commands not hardcoded and not blocked are allowed.
    """
    cmd = normalize_command(command)
    if not cmd:
        return False, "empty"

    if len(cmd) > MAX_COMMAND_LENGTH:
        return False, "too_long"

    if any(ord(ch) < 32 and ch not in ("\n", "\r", "\t") for ch in cmd):
        return False, "control_chars"

    cmd_name = cmd.split()[0].lower()
    if cmd_name in HARDCODED_COMMANDS:
        return False, "hardcoded"

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, cmd, flags=re.IGNORECASE):
            return False, "blocked"

    return True, "allowed"


def sanitize_terminal_output(output: str) -> str:
    if not output:
        return ""

    sanitized = output.strip()

    # Remove Markdown code fences if present
    sanitized = re.sub(r"^```[\s\S]*?\n", "", sanitized)
    sanitized = re.sub(r"```$", "", sanitized)

    # Remove ANSI escape codes
    sanitized = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", sanitized)

    # Remove other control characters except newline and tab
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

    # Normalize line endings to \r\n for xterm.js compatibility
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")

    # Deduplicate consecutive repeated lines (LLM sometimes generates floods)
    lines = sanitized.split("\n")
    deduped = []
    for line in lines:
        if len(deduped) < 3 or line != deduped[-1]:
            deduped.append(line)

    # Remove fake bash error lines that the LLM adds after valid output
    # e.g. "bash: 1: curl: failed to connect..." after a real curl error
    cleaned = []
    for i, line in enumerate(deduped):
        stripped = line.strip()
        # Skip "bash: N: ..." numbered error lines (LLM artifact)
        if re.match(r"^bash:\s*\d+:", stripped) and i > 0:
            continue
        # Skip contradictory "command not found" after valid command output
        if (stripped.startswith("bash:") and "command not found" in stripped
                and i > 0 and cleaned):
            continue
        cleaned.append(line)

    # Cap at 20 lines to prevent overly long outputs
    if len(cleaned) > 20:
        cleaned = cleaned[:20]

    sanitized = "\n".join(cleaned)

    sanitized = sanitized.replace("\n", "\r\n")

    if len(sanitized) > MAX_OUTPUT_LENGTH:
        sanitized = sanitized[:MAX_OUTPUT_LENGTH].rstrip() + "..."

    return sanitized


def build_connection_error_message() -> str:
    return "Connection error: failed to reach response generator"
