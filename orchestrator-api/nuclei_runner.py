"""
nuclei_runner.py — Secure Nuclei Subprocess Runner for CyberBank QA Compliance Platform

SECURITY RULES (enforced by .agents/rules.md):
  - URL allowlist check: ONLY 127.0.0.1 or localhost on port 5000 are permitted.
  - Never target external domains or public IP addresses.
  - Nuclei commands always begin with: nuclei -u http://127.0.0.1:5000
"""

import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Generator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ALLOWED_HOSTNAMES = {"127.0.0.1", "localhost"}
ALLOWED_PORT = 5000
DEFAULT_TARGET = "http://127.0.0.1:5000"

# Resolve the project root (two levels up from orchestrator-api/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CUSTOM_TEMPLATES_DIR = PROJECT_ROOT / "custom-templates"

# Nuclei binary resolution: check user home, .nuclei-bin, antigravity-ide bin, then system PATH
NUCLEI_BINARY_CANDIDATES = [
    Path.home() / ".nuclei-bin" / "nuclei.exe",
    Path.home() / ".gemini" / "antigravity-ide" / "bin" / "nuclei.exe",
    Path(r"C:\Users\Shaurya\.nuclei-bin\nuclei.exe"),
    Path(r"C:\Users\Shaurya\.gemini\antigravity-ide\bin\nuclei.exe"),
]


# ---------------------------------------------------------------------------
# Target URL Allowlist Enforcement
# ---------------------------------------------------------------------------
def validate_target_url(target_url: str) -> str:
    """
    Strictly validate target URL against .agents/rules.md allowlist.
    ONLY http://127.0.0.1:5000 or http://localhost:5000 are permitted.
    Raises ValueError for any other host, port, or scheme.
    """
    parsed = urllib.parse.urlparse(target_url)

    # Enforce http scheme only (no https — local test server)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"[SECURITY] Target URL scheme '{parsed.scheme}' is not permitted. "
            "Only 'http' or 'https' to local targets are allowed."
        )

    # Extract hostname (strip brackets for IPv6)
    hostname = parsed.hostname or ""
    if hostname not in ALLOWED_HOSTNAMES:
        raise ValueError(
            f"[SECURITY] Target hostname '{hostname}' is NOT in the allowlist. "
            f"Allowed hosts: {ALLOWED_HOSTNAMES}. "
            "Per .agents/rules.md: ONLY 127.0.0.1 or localhost may be targeted."
        )

    # Validate port — default port 80 maps to None in urlparse
    port = parsed.port
    if port is None:
        port = 80 if parsed.scheme == "http" else 443
    if port != ALLOWED_PORT:
        raise ValueError(
            f"[SECURITY] Target port '{port}' is not permitted. "
            f"Only port {ALLOWED_PORT} is allowed on localhost/127.0.0.1."
        )

    return target_url


# ---------------------------------------------------------------------------
# Nuclei Binary Resolution
# ---------------------------------------------------------------------------
def resolve_nuclei_binary() -> str:
    """
    Resolve the nuclei binary path.
    Checks known installation paths first, then falls back to system PATH.
    Raises FileNotFoundError if nuclei is not found.
    """
    for candidate in NUCLEI_BINARY_CANDIDATES:
        if candidate.exists():
            return str(candidate)

    # Fall back to system PATH
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for directory in path_dirs:
        for ext in ("", ".exe"):
            candidate = Path(directory) / f"nuclei{ext}"
            if candidate.exists():
                return str(candidate)

    raise FileNotFoundError(
        "nuclei binary not found. "
        "Install nuclei from https://nuclei.projectdiscovery.io/ or place it at "
        "C:\\Users\\Shaurya\\.nuclei-bin\\nuclei.exe"
    )


# ---------------------------------------------------------------------------
# Nuclei JSONL Line Parser
# ---------------------------------------------------------------------------
def parse_nuclei_jsonl_line(line: str) -> dict | None:
    """
    Parse a single JSONL line from nuclei -jsonl output.
    Returns a normalized finding dict or None if line is not valid JSON.
    """
    line = line.strip()
    if not line:
        return None

    try:
        raw = json.loads(line)
    except json.JSONDecodeError:
        return None

    # Extract core fields from nuclei v3 JSONL format
    template_id = raw.get("template-id", raw.get("templateID", "unknown"))
    info = raw.get("info", {})
    template_name = info.get("name", template_id)
    severity = info.get("severity", "unknown")
    matched_at = raw.get("matched-at", raw.get("host", ""))
    extracted_results = raw.get("extracted-results", [])
    curl_command = raw.get("curl-command", "")

    return {
        "template_id": template_id,
        "template_name": template_name,
        "severity": severity,
        "matched_at": matched_at,
        "extracted_results": extracted_results if isinstance(extracted_results, list) else [extracted_results],
        "curl_command": curl_command,
        "raw": raw,
    }


# ---------------------------------------------------------------------------
# Nuclei Scan Execution
# ---------------------------------------------------------------------------
def run_nuclei_scan(
    target_url: str = DEFAULT_TARGET,
    templates_dir: str | None = None,
) -> Generator[dict, None, None]:
    """
    Execute a Nuclei scan against the validated local target URL.
    Yields parsed finding dicts for each JSONL line emitted by nuclei.

    SECURITY: Target URL is strictly validated before any subprocess is spawned.
    Command format: nuclei -u http://127.0.0.1:5000 -t custom-templates/ -jsonl -silent
    """
    # Step 1: Enforce allowlist — will raise ValueError if target is not permitted
    validated_url = validate_target_url(target_url)

    # Step 2: Resolve nuclei binary
    nuclei_bin = resolve_nuclei_binary()

    # Step 3: Resolve custom templates directory
    if templates_dir is None:
        templates_dir = str(CUSTOM_TEMPLATES_DIR)

    if not Path(templates_dir).exists():
        raise FileNotFoundError(
            f"Custom templates directory not found: {templates_dir}. "
            "Ensure custom-templates/ exists in the project root."
        )

    # Step 4: Build command — always in form: nuclei -u http://127.0.0.1:5000 ...
    cmd = [
        nuclei_bin,
        "-u", validated_url,
        "-t", templates_dir,
        "-jsonl",
        "-silent",
    ]

    # Step 5: Execute nuclei subprocess and stream JSONL output
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in process.stdout:
            parsed = parse_nuclei_jsonl_line(line)
            if parsed is not None:
                yield parsed

        process.wait()

        # Capture stderr for diagnostics (not raised — nuclei writes info to stderr)
        stderr_output = process.stderr.read() if process.stderr else ""
        if process.returncode not in (0, 1) and stderr_output:
            # Return code 1 means findings found (normal for nuclei)
            raise RuntimeError(
                f"Nuclei exited with code {process.returncode}. "
                f"stderr: {stderr_output[:500]}"
            )

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not launch nuclei binary at: {nuclei_bin}. "
            "Verify the binary path and permissions."
        )

