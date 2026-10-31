"""
main.py — CyberBank QA Compliance Orchestrator API (FastAPI, Port 8000)

Endpoints:
  POST /api/scans/run         — Trigger live Nuclei scan, store forensic findings
  GET  /api/scans/history     — Return past scan summaries
  GET  /api/scans/{scan_id}   — Return detailed findings for a specific scan
  GET  /api/target/status     — Get current compliance mode of target Flask server
  POST /api/target/toggle     — Toggle compliance mode on target Flask server
"""

import uuid
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import forensics
import nuclei_runner

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CyberBank QA Compliance Orchestrator",
    description=(
        "Digital Forensics & API Governance platform for academic Cyber Crime demonstration. "
        "Executes Nuclei v3 compliance templates against http://127.0.0.1:5000 and stores "
        "SHA-256 hashed forensic evidence with OWASP & Indian IT Act 2000 mappings."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TARGET_BASE_URL = "http://127.0.0.1:5000"

# Initialize the forensics vault database on startup
forensics.init_vault_db()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class ScanRunRequest(BaseModel):
    target_url: str = TARGET_BASE_URL
    note: str = ""


class ToggleRequest(BaseModel):
    enabled: bool | None = None  # None = toggle; True/False = set explicitly


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/scans/run")
async def run_scan(request: ScanRunRequest = ScanRunRequest()):
    """
    Trigger a live Nuclei scan against the validated local Flask target server.

    1. Validates target URL against allowlist (127.0.0.1:5000 or localhost:5000 only).
    2. Resolves nuclei binary and executes: nuclei -u http://127.0.0.1:5000 -t custom-templates/ -jsonl -silent
    3. Parses each JSONL finding, computes SHA-256 chain-of-custody hash.
    4. Enriches each finding with OWASP API Security Top 10 + Indian IT Act 2000 mappings.
    5. Stores everything in forensics_vault.db and returns the complete report.
    """
    # Validate target URL before doing anything
    try:
        validated_url = nuclei_runner.validate_target_url(request.target_url)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Check if target Flask server is reachable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            probe = await client.get(f"{validated_url}/api/debug/config")
            if probe.status_code == 200:
                compliance_mode = "RELAXED (STRICT_COMPLIANCE_MODE=False)"
            elif probe.status_code == 403:
                compliance_mode = "STRICT (STRICT_COMPLIANCE_MODE=True)"
            else:
                compliance_mode = f"UNKNOWN (HTTP {probe.status_code})"
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot connect to target Flask server at http://127.0.0.1:5000. "
                "Start target-app/app.py first: python target-app/app.py"
            ),
        )

    # Generate unique scan ID
    scan_id = f"SCAN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"

    # Register scan run in forensics vault
    forensics.create_scan_run(
        scan_id=scan_id,
        target_url=validated_url,
        compliance_mode=compliance_mode,
        nuclei_version="v3.11.1",
        templates_used="custom-templates/",
    )

    # Execute Nuclei scan and collect findings
    findings = []
    errors = []

    try:
        for raw_finding in nuclei_runner.run_nuclei_scan(target_url=validated_url):
            stored = forensics.store_finding(
                scan_id=scan_id,
                template_id=raw_finding["template_id"],
                template_name=raw_finding["template_name"],
                severity=raw_finding["severity"],
                matched_at=raw_finding["matched_at"],
                extracted_results=raw_finding["extracted_results"],
                curl_command=raw_finding["curl_command"],
            )
            findings.append(stored)
    except FileNotFoundError as e:
        errors.append(f"Nuclei binary error: {str(e)}")
    except RuntimeError as e:
        errors.append(f"Nuclei runtime error: {str(e)}")

    # Complete scan run record
    forensics.complete_scan_run(scan_id=scan_id, total_findings=len(findings))

    # Severity summary
    severity_summary = {"high": 0, "medium": 0, "low": 0, "info": 0, "unknown": 0}
    for f in findings:
        sev = f.get("severity", "unknown").lower()
        severity_summary[sev] = severity_summary.get(sev, 0) + 1

    return {
        "scan_id": scan_id,
        "target_url": validated_url,
        "compliance_mode_detected": compliance_mode,
        "total_findings": len(findings),
        "severity_summary": severity_summary,
        "scan_note": request.note,
        "errors": errors,
        "findings": findings,
    }


@app.get("/api/scans/history")
async def get_scan_history():
    """Return all past scan run summaries from forensics_vault.db, ordered newest first."""
    history = forensics.get_scan_history()
    return {
        "total_scans": len(history),
        "scans": history,
    }


@app.get("/api/scans/{scan_id}")
async def get_scan_detail(scan_id: str):
    """Return detailed findings and SHA-256 forensic hashes for a specific scan_id."""
    result = forensics.get_scan_findings(scan_id=scan_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Scan ID '{scan_id}' not found in forensics_vault.db.",
        )
    return result


@app.get("/api/target/status")
async def get_target_status():
    """
    Proxy helper: Query http://127.0.0.1:5000/api/debug/config to detect the current
    compliance mode of the target Flask server. Returns mode, reachability, and debug config.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            debug_resp = await client.get(f"{TARGET_BASE_URL}/api/debug/config")

        if debug_resp.status_code == 200:
            return {
                "reachable": True,
                "strict_compliance_mode": False,
                "compliance_mode_label": "RELAXED (STRICT_COMPLIANCE_MODE=False)",
                "debug_config": debug_resp.json(),
            }
        elif debug_resp.status_code == 403:
            return {
                "reachable": True,
                "strict_compliance_mode": True,
                "compliance_mode_label": "STRICT (STRICT_COMPLIANCE_MODE=True)",
                "debug_config": None,
            }
        else:
            return {
                "reachable": True,
                "strict_compliance_mode": None,
                "compliance_mode_label": f"UNKNOWN (HTTP {debug_resp.status_code})",
                "debug_config": None,
            }
    except httpx.ConnectError:
        return {
            "reachable": False,
            "strict_compliance_mode": None,
            "compliance_mode_label": "TARGET SERVER UNREACHABLE",
            "debug_config": None,
        }


@app.post("/api/target/toggle")
async def toggle_target_compliance(request: ToggleRequest = ToggleRequest()):
    """
    Proxy helper: POST to http://127.0.0.1:5000/api/toggle-compliance to toggle
    or explicitly set the compliance mode on the target Flask server.
    """
    try:
        payload = {}
        if request.enabled is not None:
            payload = {"enabled": request.enabled}

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{TARGET_BASE_URL}/api/toggle-compliance",
                json=payload,
            )

        return {
            "success": True,
            "target_response": resp.json(),
        }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to target Flask server at http://127.0.0.1:5000.",
        )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

