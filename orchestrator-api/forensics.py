"""
forensics.py — Digital Forensics Vault for CyberBank QA Compliance Platform
Manages SQLite forensics_vault.db with SHA-256 chain-of-custody hashing,
OWASP API Security Top 10 mappings, and Indian IT Act 2000 compliance references.
"""

import hashlib
import json
import sqlite3
import os
from datetime import datetime, timezone
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DB_PATH = os.path.join(BASE_DIR, "forensics_vault.db")

# ---------------------------------------------------------------------------
# OWASP API Security Top 10 (2023) + Indian IT Act 2000 Compliance Mappings
# ---------------------------------------------------------------------------
COMPLIANCE_MAPPINGS: dict[str, dict] = {
    "unauthenticated-customer-api": {
        "owasp_category": "API1:2023 – Broken Object Level Authorization (BOLA/IDOR)",
        "owasp_url": "https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/",
        "it_act_section": "Section 43A – Body Corporate Data Protection Failure",
        "it_act_description": (
            "Under Section 43A of the IT Act 2000 (amended 2008), a body corporate "
            "that possesses, deals with, or handles sensitive personal data and is "
            "negligent in implementing reasonable security practices is liable to pay "
            "damages to the affected person. Unauthenticated API access exposing PAN "
            "card numbers, account numbers, and email addresses constitutes such negligence."
        ),
        "cert_in_ref": "CERT-In Advisory CI-2022-003: Mandatory 6-hour breach notification for PII/banking data exposure",
        "dpdp_ref": "DPDP Act 2023 – Chapter II: Obligations of Data Fiduciaries (PAN/financial data)",
        "severity": "high",
        "remediation": (
            "Implement bearer token or session-based authentication on all customer endpoints. "
            "Enforce X-Auth-Token validation and rate limiting per CERT-In 2022 guidelines."
        ),
    },
    "exposed-debug-configuration": {
        "owasp_category": "API8:2023 – Security Misconfiguration",
        "owasp_url": "https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/",
        "it_act_section": "Section 72A – Disclosure of Information in Breach of Lawful Contract",
        "it_act_description": (
            "Section 72A of the IT Act 2000 penalizes disclosure of information without "
            "the consent of the person concerned, in breach of lawful contract. Exposing "
            "internal application configuration (debug mode, database engine, service version) "
            "can constitute unauthorized disclosure that aids adversarial exploitation, "
            "amounting to breach of an implied security obligation."
        ),
        "cert_in_ref": "CERT-In 2022 Directive: Disable debug/diagnostic endpoints in production; enforce environment-aware configuration",
        "dpdp_ref": "N/A – Configuration exposure; no direct personal data",
        "severity": "medium",
        "remediation": (
            "Disable debug endpoints in production configuration. "
            "Gate /api/debug/config behind authentication or restrict to internal network only."
        ),
    },
    "missing-http-security-headers": {
        "owasp_category": "API8:2023 – Security Misconfiguration (Response Header Hardening)",
        "owasp_url": "https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/",
        "it_act_section": "Section 43 – Penalty for Damage to Computer System (Clickjacking/XSS enablement)",
        "it_act_description": (
            "Section 43 of the IT Act 2000 imposes liability for unauthorized access or "
            "damage to a computer system. Absence of X-Frame-Options facilitates clickjacking "
            "attacks that can trick banking customers into performing unintended actions. "
            "Missing Content-Security-Policy enables XSS injection attacks against user sessions."
        ),
        "cert_in_ref": "CERT-In Web Application Security Guidelines 2022: Mandatory HTTP security headers for financial portals",
        "dpdp_ref": "DPDP Act 2023 – Security safeguards obligation for customer-facing interfaces",
        "severity": "low",
        "remediation": (
            "Configure X-Frame-Options: DENY, Content-Security-Policy: default-src 'self', "
            "and X-Content-Type-Options: nosniff in all HTTP responses. "
            "Enable STRICT_COMPLIANCE_MODE in the target application."
        ),
    },
}


# ---------------------------------------------------------------------------
# Database Initialisation
# ---------------------------------------------------------------------------
def init_vault_db(db_path: str = VAULT_DB_PATH) -> None:
    """Create forensics_vault.db with scan_runs and findings tables if they do not exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL UNIQUE,
            target_url TEXT NOT NULL,
            compliance_mode TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_findings INTEGER DEFAULT 0,
            nuclei_version TEXT,
            templates_used TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL,
            template_id TEXT NOT NULL,
            template_name TEXT,
            severity TEXT NOT NULL,
            matched_at TEXT NOT NULL,
            extracted_results TEXT,
            curl_command TEXT,
            sha256_hash TEXT NOT NULL,
            owasp_category TEXT,
            it_act_section TEXT,
            it_act_description TEXT,
            cert_in_ref TEXT,
            dpdp_ref TEXT,
            remediation TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(scan_id) REFERENCES scan_runs(scan_id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Chain-of-Custody SHA-256 Hashing
# ---------------------------------------------------------------------------
def compute_sha256_hash(
    template_id: str,
    matched_at: str,
    extracted_results: list,
    timestamp: str,
    scan_id: str,
) -> str:
    """
    Compute SHA-256 digital forensics integrity hash for chain-of-custody.
    Hash input: canonical JSON of template_id + matched_at + extracted_results + timestamp + scan_id.
    This ensures each finding can be independently verified for integrity.
    """
    evidence_payload = {
        "template_id": template_id,
        "matched_at": matched_at,
        "extracted_results": sorted(extracted_results) if extracted_results else [],
        "timestamp": timestamp,
        "scan_id": scan_id,
    }
    canonical_json = json.dumps(evidence_payload, sort_keys=True, separators=(",", ":"))
    sha256_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return sha256_hash


# ---------------------------------------------------------------------------
# Scan Run Management
# ---------------------------------------------------------------------------
def create_scan_run(
    scan_id: str,
    target_url: str,
    compliance_mode: str,
    nuclei_version: str = "v3.11.1",
    templates_used: str = "custom-templates/",
    db_path: str = VAULT_DB_PATH,
) -> None:
    """Insert a new scan run record into forensics_vault.db."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO scan_runs (scan_id, target_url, compliance_mode, started_at, nuclei_version, templates_used)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (scan_id, target_url, compliance_mode, now_iso, nuclei_version, templates_used))
    conn.commit()
    conn.close()


def complete_scan_run(
    scan_id: str,
    total_findings: int,
    db_path: str = VAULT_DB_PATH,
) -> None:
    """Update a scan run with completion timestamp and finding count."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE scan_runs
        SET completed_at = ?, total_findings = ?
        WHERE scan_id = ?
    """, (now_iso, total_findings, scan_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Finding Storage
# ---------------------------------------------------------------------------
def store_finding(
    scan_id: str,
    template_id: str,
    template_name: str,
    severity: str,
    matched_at: str,
    extracted_results: list,
    curl_command: str,
    db_path: str = VAULT_DB_PATH,
) -> dict:
    """
    Hash, enrich with compliance mappings, and persist a single Nuclei finding.
    Returns the complete enriched finding record including SHA-256 hash.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Compute chain-of-custody SHA-256 hash
    sha256_hash = compute_sha256_hash(
        template_id=template_id,
        matched_at=matched_at,
        extracted_results=extracted_results or [],
        timestamp=timestamp,
        scan_id=scan_id,
    )

    # Look up OWASP + IT Act compliance mapping
    mapping = COMPLIANCE_MAPPINGS.get(template_id, {
        "owasp_category": "Uncategorized",
        "owasp_url": "",
        "it_act_section": "Unknown",
        "it_act_description": "No compliance mapping defined for this template.",
        "cert_in_ref": "N/A",
        "dpdp_ref": "N/A",
        "severity": severity,
        "remediation": "Review template documentation.",
    })

    extracted_json = json.dumps(extracted_results or [])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO findings (
            scan_id, template_id, template_name, severity, matched_at,
            extracted_results, curl_command, sha256_hash,
            owasp_category, it_act_section, it_act_description,
            cert_in_ref, dpdp_ref, remediation, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id, template_id, template_name, severity, matched_at,
        extracted_json, curl_command or "", sha256_hash,
        mapping.get("owasp_category", ""),
        mapping.get("it_act_section", ""),
        mapping.get("it_act_description", ""),
        mapping.get("cert_in_ref", ""),
        mapping.get("dpdp_ref", ""),
        mapping.get("remediation", ""),
        timestamp,
    ))
    conn.commit()
    conn.close()

    return {
        "template_id": template_id,
        "template_name": template_name,
        "severity": severity,
        "matched_at": matched_at,
        "extracted_results": extracted_results or [],
        "curl_command": curl_command or "",
        "sha256_forensic_hash": sha256_hash,
        "timestamp": timestamp,
        "compliance": {
            "owasp_category": mapping.get("owasp_category"),
            "owasp_url": mapping.get("owasp_url"),
            "it_act_section": mapping.get("it_act_section"),
            "it_act_description": mapping.get("it_act_description"),
            "cert_in_ref": mapping.get("cert_in_ref"),
            "dpdp_ref": mapping.get("dpdp_ref"),
            "remediation": mapping.get("remediation"),
        },
    }


# ---------------------------------------------------------------------------
# Query Helpers
# ---------------------------------------------------------------------------
def get_scan_history(db_path: str = VAULT_DB_PATH) -> list[dict]:
    """Return all past scan run summaries ordered newest first."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, scan_id, target_url, compliance_mode, started_at,
               completed_at, total_findings, nuclei_version, templates_used
        FROM scan_runs
        ORDER BY id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_scan_findings(scan_id: str, db_path: str = VAULT_DB_PATH) -> dict:
    """Return a scan run and all its detailed findings for a given scan_id."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scan_runs WHERE scan_id = ?", (scan_id,))
    run_row = cursor.fetchone()
    if not run_row:
        conn.close()
        return {}

    run = dict(run_row)

    cursor.execute("""
        SELECT id, template_id, template_name, severity, matched_at,
               extracted_results, curl_command, sha256_hash,
               owasp_category, it_act_section, it_act_description,
               cert_in_ref, dpdp_ref, remediation, timestamp
        FROM findings
        WHERE scan_id = ?
        ORDER BY id ASC
    """, (scan_id,))

    findings = []
    for row in cursor.fetchall():
        f = dict(row)
        # Deserialize extracted_results from JSON string
        try:
            f["extracted_results"] = json.loads(f["extracted_results"])
        except (json.JSONDecodeError, TypeError):
            f["extracted_results"] = []
        findings.append(f)

    conn.close()
    run["findings"] = findings
    return run

