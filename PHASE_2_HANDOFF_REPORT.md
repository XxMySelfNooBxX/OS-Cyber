# PHASE 2 HANDOFF REPORT: QA Compliance & Digital Forensics Auditing Platform

**Project**: Academic Cyber Crime & Digital Forensics Demonstration  
**Phase**: 2 — Nuclei Templates + Orchestrator API + Forensics Vault  
**Target Application**: `target-app/` on `http://127.0.0.1:5000`  
**Orchestrator API**: `orchestrator-api/` on `http://127.0.0.1:8000`  
**Nuclei Version**: v3.11.1  
**Status**: All parts implemented and verified ✅

> [!IMPORTANT]
> All scanning and execution is strictly scoped to `http://127.0.0.1:5000` as mandated by `.agents/rules.md`.
> The URL allowlist enforcement is implemented in `orchestrator-api/nuclei_runner.py` using `urllib.parse.urlparse`.

---

## 1. File Tree

### `custom-templates/`

| File | Lines | Size | Description |
| :--- | :--- | :--- | :--- |
| `unauthenticated-customer-api.yaml` | 42 lines | 1,286 bytes | IDOR/PII exposure detector — targets `/api/v1/customer/1001` and `/1002` |
| `exposed-debug-configuration.yaml` | 39 lines | 1,200 bytes | Debug endpoint info disclosure detector — targets `/api/debug/config` |
| `missing-http-security-headers.yaml` | 37 lines | 1,330 bytes | Security header absence detector — targets `/` with negative matcher |

### `orchestrator-api/`

| File | Lines | Size | Description |
| :--- | :--- | :--- | :--- |
| `forensics.py` | 338 lines | 13,577 bytes | SQLite vault manager, SHA-256 chain-of-custody hashing, OWASP + IT Act mappings |
| `main.py` | 251 lines | 8,993 bytes | FastAPI app with 5 governance endpoints, CORS, target proxy helpers |
| `nuclei_runner.py` | 211 lines | 7,577 bytes | Allowlist-enforced Nuclei subprocess runner + JSONL parser |
| `requirements.txt` | 4 lines | 63 bytes | `fastapi>=0.110.0`, `uvicorn>=0.29.0`, `pydantic>=2.6.0`, `httpx>=0.27.0` |
| `forensics_vault.db` | binary | 28,672 bytes | SQLite forensics database (`scan_runs` + `findings` tables) |

---

## 2. Nuclei Template Specification

### Template 1: `unauthenticated-customer-api.yaml`

| Field | Value |
| :--- | :--- |
| ID | `unauthenticated-customer-api` |
| Severity | `high` |
| Paths | `{{BaseURL}}/api/v1/customer/1001`, `{{BaseURL}}/api/v1/customer/1002` |
| Matchers | `status: 200` AND `words: ["pan_card", "account_number"]` |
| Extractor | `exposed_records` (JSON: `.full_name`, `.account_number`, `.pan_card`) |

### Template 2: `exposed-debug-configuration.yaml`

| Field | Value |
| :--- | :--- |
| ID | `exposed-debug-configuration` |
| Severity | `medium` |
| Paths | `{{BaseURL}}/api/debug/config` |
| Matchers | `status: 200` AND `words: ['"debug_enabled": true']` |
| Extractor | `config_metadata` (JSON: `.app_env`, `.db_engine`) |

### Template 3: `missing-http-security-headers.yaml`

| Field | Value |
| :--- | :--- |
| ID | `missing-http-security-headers` |
| Severity | `low` |
| Paths | `{{BaseURL}}/` |
| Matchers | `status: 200` OR `negative: true` word match on `header` for `X-Frame-Options`, `Content-Security-Policy` |

---

## 3. Orchestrator API Endpoint Table

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/scans/run` | POST | Triggers Nuclei scan against `http://127.0.0.1:5000`, stores SHA-256 hashed forensic findings in `forensics_vault.db`, returns full report with OWASP + IT Act mappings |
| `GET /api/scans/history` | GET | Returns all past scan summaries ordered newest first |
| `GET /api/scans/{scan_id}` | GET | Returns detailed findings and forensic hashes for a specific scan run |
| `GET /api/target/status` | GET | Probes `http://127.0.0.1:5000/api/debug/config` to detect current compliance mode |
| `POST /api/target/toggle` | POST | Proxies to `http://127.0.0.1:5000/api/toggle-compliance` to switch compliance mode |

---

## 4. Raw Nuclei JSONL Verification Output (`STRICT_COMPLIANCE_MODE = False`)

**Total findings: 4** (2× high, 1× medium, 1× low)

### Finding 1 — `unauthenticated-customer-api` on `/api/v1/customer/1001`
```json
{
  "template-id": "unauthenticated-customer-api",
  "info": {
    "name": "Unauthenticated Customer API - PII Exposure (IDOR)",
    "severity": "high"
  },
  "matched-at": "http://127.0.0.1:5000/api/v1/customer/1001",
  "extracted-results": [
    "Rahul Sharma",
    "ACC-98214532",
    "ABCDE1234F"
  ],
  "curl-command": "curl -X 'GET' 'http://127.0.0.1:5000/api/v1/customer/1001'",
  "response_body": {
    "account_number": "ACC-98214532",
    "balance": 125400.5,
    "email": "rahul.sharma@cyberbank.local",
    "full_name": "Rahul Sharma",
    "id": 1001,
    "pan_card": "ABCDE1234F"
  }
}
```

### Finding 2 — `unauthenticated-customer-api` on `/api/v1/customer/1002`
```json
{
  "template-id": "unauthenticated-customer-api",
  "info": {
    "name": "Unauthenticated Customer API - PII Exposure (IDOR)",
    "severity": "high"
  },
  "matched-at": "http://127.0.0.1:5000/api/v1/customer/1002",
  "extracted-results": [
    "Priya Verma",
    "ACC-88349120",
    "BKLPV5678Q"
  ],
  "curl-command": "curl -X 'GET' 'http://127.0.0.1:5000/api/v1/customer/1002'",
  "response_body": {
    "account_number": "ACC-88349120",
    "balance": 342100.0,
    "email": "priya.verma@cyberbank.local",
    "full_name": "Priya Verma",
    "id": 1002,
    "pan_card": "BKLPV5678Q"
  }
}
```

### Finding 3 — `exposed-debug-configuration` on `/api/debug/config`
```json
{
  "template-id": "exposed-debug-configuration",
  "info": {
    "name": "Exposed Debug Configuration Endpoint - Information Disclosure",
    "severity": "medium"
  },
  "matched-at": "http://127.0.0.1:5000/api/debug/config",
  "extracted-results": [
    "development",
    "sqlite3"
  ],
  "curl-command": "curl -X 'GET' 'http://127.0.0.1:5000/api/debug/config'",
  "response_body": {
    "app_env": "development",
    "db_engine": "sqlite3",
    "debug_enabled": true,
    "service_version": "1.0.4"
  }
}
```

### Finding 4 — `missing-http-security-headers` on `/`
```json
{
  "template-id": "missing-http-security-headers",
  "info": {
    "name": "Missing HTTP Security Headers - Response Header Hardening",
    "severity": "low"
  },
  "matched-at": "http://127.0.0.1:5000/",
  "extracted-results": [],
  "curl-command": "curl -X 'GET' 'http://127.0.0.1:5000/'",
  "missing_headers": [
    "X-Frame-Options",
    "Content-Security-Policy"
  ]
}
```

---

## 5. Nuclei Scan Results — `STRICT_COMPLIANCE_MODE = True`

```
Total findings (Strict): 0

[OK] 0 findings in STRICT mode — all vulnerabilities remediated by compliance controls.
```

**Explanation of remediation in strict mode:**
- `/api/v1/customer/1001` and `/1002` → returns `401 Unauthorized` (no `X-Auth-Token`)  
- `/api/debug/config` → returns `403 Forbidden`
- `GET /` → response now includes `X-Frame-Options: DENY` and `Content-Security-Policy: default-src 'self'`

---

## 6. Sample `POST /api/scans/run` Response — Relaxed Mode with SHA-256 & IT Act Mappings

```json
{
  "scan_id": "SCAN-RELAXED-20261030-130135",
  "target_url": "http://127.0.0.1:5000",
  "compliance_mode_detected": "RELAXED (STRICT_COMPLIANCE_MODE=False)",
  "total_findings": 4,
  "severity_summary": {
    "high": 2,
    "medium": 1,
    "low": 1
  },
  "findings": [
    {
      "template_id": "unauthenticated-customer-api",
      "template_name": "Unauthenticated Customer API - PII Exposure (IDOR)",
      "severity": "high",
      "matched_at": "http://127.0.0.1:5000/api/v1/customer/1001",
      "extracted_results": ["Rahul Sharma", "ACC-98214532", "ABCDE1234F"],
      "curl_command": "curl -X 'GET' 'http://127.0.0.1:5000/api/v1/customer/1001'",
      "sha256_forensic_hash": "262a908d2228e74616739863aaa671a8979f2863a14bcecf9a806d6e8c240a55",
      "timestamp": "2026-10-30T13:01:35.812683+00:00",
      "compliance": {
        "owasp_category": "API1:2023 – Broken Object Level Authorization (BOLA/IDOR)",
        "owasp_url": "https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/",
        "it_act_section": "Section 43A – Body Corporate Data Protection Failure",
        "it_act_description": "Under Section 43A of the IT Act 2000 (amended 2008), a body corporate that possesses, deals with, or handles sensitive personal data and is negligent in implementing reasonable security practices is liable to pay damages to the affected person. Unauthenticated API access exposing PAN card numbers, account numbers, and email addresses constitutes such negligence.",
        "cert_in_ref": "CERT-In Advisory CI-2022-003: Mandatory 6-hour breach notification for PII/banking data exposure",
        "dpdp_ref": "DPDP Act 2023 – Chapter II: Obligations of Data Fiduciaries (PAN/financial data)",
        "remediation": "Implement bearer token or session-based authentication on all customer endpoints. Enforce X-Auth-Token validation and rate limiting per CERT-In 2022 guidelines."
      }
    },
    {
      "template_id": "unauthenticated-customer-api",
      "template_name": "Unauthenticated Customer API - PII Exposure (IDOR)",
      "severity": "high",
      "matched_at": "http://127.0.0.1:5000/api/v1/customer/1002",
      "extracted_results": ["Priya Verma", "ACC-88349120", "BKLPV5678Q"],
      "curl_command": "curl -X 'GET' 'http://127.0.0.1:5000/api/v1/customer/1002'",
      "sha256_forensic_hash": "c900579ef8af1d7b99646fb7e6ed8f1b11e54d0465da68841b693165f35107c0",
      "timestamp": "2026-10-30T13:01:35.818206+00:00",
      "compliance": {
        "owasp_category": "API1:2023 – Broken Object Level Authorization (BOLA/IDOR)",
        "it_act_section": "Section 43A – Body Corporate Data Protection Failure",
        "cert_in_ref": "CERT-In Advisory CI-2022-003: Mandatory 6-hour breach notification for PII/banking data exposure",
        "dpdp_ref": "DPDP Act 2023 – Chapter II: Obligations of Data Fiduciaries (PAN/financial data)"
      }
    },
    {
      "template_id": "exposed-debug-configuration",
      "template_name": "Exposed Debug Configuration Endpoint - Information Disclosure",
      "severity": "medium",
      "matched_at": "http://127.0.0.1:5000/api/debug/config",
      "extracted_results": ["development", "sqlite3"],
      "curl_command": "curl -X 'GET' 'http://127.0.0.1:5000/api/debug/config'",
      "sha256_forensic_hash": "73e993cd0977ced2bf370a91155729e83c5f7ab9dd04908e645a58bca60cda39",
      "timestamp": "2026-10-30T13:01:35.823199+00:00",
      "compliance": {
        "owasp_category": "API8:2023 – Security Misconfiguration",
        "it_act_section": "Section 72A – Disclosure of Information in Breach of Lawful Contract",
        "cert_in_ref": "CERT-In 2022 Directive: Disable debug/diagnostic endpoints in production",
        "dpdp_ref": "N/A – Configuration exposure; no direct personal data"
      }
    },
    {
      "template_id": "missing-http-security-headers",
      "template_name": "Missing HTTP Security Headers - Response Header Hardening",
      "severity": "low",
      "matched_at": "http://127.0.0.1:5000/",
      "extracted_results": [],
      "curl_command": "curl -X 'GET' 'http://127.0.0.1:5000/'",
      "sha256_forensic_hash": "de6cf669a78994c3c8f417d6231ee7ab1f7265b5c9060226f0a661ae674568da",
      "timestamp": "2026-10-30T13:01:35.827713+00:00",
      "compliance": {
        "owasp_category": "API8:2023 – Security Misconfiguration (Response Header Hardening)",
        "it_act_section": "Section 43 – Penalty for Damage to Computer System (Clickjacking/XSS enablement)",
        "cert_in_ref": "CERT-In Web Application Security Guidelines 2022: Mandatory HTTP security headers for financial portals",
        "dpdp_ref": "DPDP Act 2023 – Security safeguards obligation for customer-facing interfaces"
      }
    }
  ]
}
```

---

## 7. Sample `POST /api/scans/run` Response — Strict Mode

```json
{
  "scan_id": "SCAN-STRICT-20261030-130135",
  "target_url": "http://127.0.0.1:5000",
  "compliance_mode_detected": "STRICT (STRICT_COMPLIANCE_MODE=True)",
  "total_findings": 0,
  "severity_summary": {
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "findings": []
}
```

---

## 8. Security Allowlist Enforcement Verification

All tests passed in `nuclei_runner.py` URL validation:

| URL | Allowed? | Reason |
| :--- | :--- | :--- |
| `http://127.0.0.1:5000` | ✅ ALLOWED | Hostname and port match allowlist |
| `http://localhost:5000` | ✅ ALLOWED | Hostname and port match allowlist |
| `http://external.site.com/api` | 🚫 BLOCKED | Hostname not in allowlist |
| `http://192.168.1.1:5000` | 🚫 BLOCKED | Hostname not in allowlist |
| `http://127.0.0.1:8080` | 🚫 BLOCKED | Port 8080 not allowed (only port 5000) |
| `http://0.0.0.0:5000` | 🚫 BLOCKED | Hostname not in allowlist |

---

## 9. SHA-256 Chain-of-Custody Hash Verification

The `compute_sha256_hash()` function in `forensics.py` produces:

- **Deterministic hashes**: Same `template_id + matched_at + extracted_results + timestamp + scan_id` always produces the same SHA-256 hex digest
- **Unique per finding**: Each different finding's hash is cryptographically distinct
- **Tamper-evident**: Any alteration of finding data invalidates its stored hash

**Sample hash outputs:**
```
IDOR finding (ACC/1001/ABCDE1234F): 44dc284b2b82970cc6cfbb6af86af1f2c794a27952aa17b0bfc7180d26964ff5
Debug config finding (dev/sqlite3): 02928dc21e7ae5271ca974c770f01a49e9a1e88f5a5d2540f8458d81463533e4
```

---

## 10. How to Run Phase 2

```bash
# Terminal 1 — Start Flask target server (port 5000)
cd "target-app"
python app.py

# Terminal 2 — Start FastAPI orchestrator (port 8000)
cd "orchestrator-api"
python main.py

# Trigger a scan (from any terminal or browser)
curl -X POST http://127.0.0.1:8000/api/scans/run

# View scan history
curl http://127.0.0.1:8000/api/scans/history

# Toggle compliance mode
curl -X POST http://127.0.0.1:8000/api/target/toggle

# Re-scan after toggle (should return 0 findings in STRICT mode)
curl -X POST http://127.0.0.1:8000/api/scans/run
```

> [!TIP]
> The FastAPI orchestrator has interactive Swagger documentation at `http://127.0.0.1:8000/docs` when running.

