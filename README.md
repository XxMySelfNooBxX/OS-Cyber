# CyberBank — QA Compliance & Digital Forensics Auditing Platform

> **Academic Cyber Crime & Digital Forensics Demonstration Project**  
> Demonstrates API governance vulnerabilities, Nuclei v3 automated scanning, SHA-256 chain-of-custody forensics, and defensive patching mapped to the **Indian IT Act 2000** and **DPDP Act 2023**.

---

## 📐 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Tier 3: React Dashboard (port 5173)                            │
│  dashboard-ui/ · Vite + Tailwind CSS + Lucide Icons            │
│  Governance Center UI · Forensic Evidence Vault · Scan History  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP (fetch)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tier 2: FastAPI Orchestrator (port 8000)                       │
│  orchestrator-api/ · nuclei_runner.py · forensics.py           │
│  SHA-256 Chain-of-Custody · OWASP + IT Act mappings            │
│  SQLite forensics_vault.db                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │ subprocess (nuclei) + HTTP proxy
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tier 1: Flask Target Server (port 5000)                        │
│  target-app/app.py · SQLite cyber_bank.db                      │
│  STRICT_COMPLIANCE_MODE toggle · 5 API routes                   │
│  Intentionally vulnerable (relaxed) / hardened (strict)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
project sem 7/
├── .agents/rules.md                   # Agent security rules (URL allowlist)
├── custom-templates/                  # Nuclei v3 YAML compliance templates
│   ├── unauthenticated-customer-api.yaml   (HIGH — IDOR/PII exposure)
│   ├── exposed-debug-configuration.yaml    (MEDIUM — Info disclosure)
│   └── missing-http-security-headers.yaml  (LOW — Header hardening)
├── target-app/                        # Tier 1: Flask vulnerable/hardened API
│   ├── app.py                         # Flask server (port 5000)
│   ├── seed_db.py                     # DB schema + sample data seeder
│   ├── cyber_bank.db                  # SQLite: customers + audit_logs
│   └── requirements.txt
├── orchestrator-api/                  # Tier 2: FastAPI forensics orchestrator
│   ├── main.py                        # FastAPI server (port 8000)
│   ├── forensics.py                   # SHA-256 vault + compliance mappings
│   ├── nuclei_runner.py               # URL-allowlisted Nuclei subprocess
│   ├── forensics_vault.db             # SQLite: scan_runs + findings
│   └── requirements.txt
├── dashboard-ui/                      # Tier 3: React governance dashboard
│   ├── src/
│   │   ├── App.jsx                    # Root app + state management
│   │   ├── api/orchestrator.js        # FastAPI client
│   │   └── components/
│   │       ├── ControlBar.jsx         # Target status + action buttons
│   │       ├── MetricCards.jsx        # Severity summary stats
│   │       ├── FindingCard.jsx        # Full finding with forensics UI
│   │       ├── ScanHistorySidebar.jsx # Historical scan navigator
│   │       └── SeverityBadge.jsx     # Severity indicator component
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── start_project.ps1                  # One-click launcher (all 3 tiers)
├── PHASE_1B_HANDOFF_REPORT.md
├── PHASE_2_HANDOFF_REPORT.md
├── PHASE_3_HANDOFF_REPORT.md
└── README.md                          # This file
```

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Nuclei v3.11.1** at `C:\Users\Shaurya\.nuclei-bin\nuclei.exe`

### Option A — One-Click PowerShell Launcher
```powershell
cd "project sem 7"
.\start_project.ps1
```

### Option B — Manual (3 separate terminals)

**Terminal 1 — Flask Target Server:**
```bash
cd target-app
python app.py
# → http://127.0.0.1:5000
```

**Terminal 2 — FastAPI Orchestrator:**
```bash
cd orchestrator-api
pip install fastapi uvicorn httpx pydantic
python main.py
# → http://127.0.0.1:8000  |  Swagger: http://127.0.0.1:8000/docs
```

**Terminal 3 — React Dashboard:**
```bash
cd dashboard-ui
npm install
npm run dev
# → http://127.0.0.1:5173
```

---

## 🎯 Live Demo Walkthrough

### Step 1 — Relaxed Mode (Vulnerable Baseline)
1. Open **http://127.0.0.1:5173** in browser
2. Confirm posture badge shows: `⚠️ RELAXED MODE — UNPROTECTED`
3. Click **"Run Live Nuclei Audit"** — watch the spinner and JSONL scan execute
4. **Expected: 4 findings** (2× HIGH, 1× MEDIUM, 1× LOW)
   - Customer 1001 PII leaked: `Rahul Sharma · ACC-98214532 · ABCDE1234F`
   - Customer 1002 PII leaked: `Priya Verma · ACC-88349120 · BKLPV5678Q`
   - Debug config exposed: `app_env=development · db_engine=sqlite3`
   - Security headers missing: `X-Frame-Options · Content-Security-Policy`
5. Click **"▼ Legal & Regulatory Compliance Mapping"** on the IDOR finding
   - Shows `API1:2023 BOLA/IDOR → Section 43A IT Act 2000 → CERT-In 2022`
6. Click **"Copy Hash"** on any finding to copy SHA-256 forensic hash to clipboard

### Step 2 — Enable Strict Compliance (Remediation)
1. Click **"Toggle Compliance Mode"** — posture updates to `✅ STRICT COMPLIANCE MODE — HARDENED`
2. Click **"Run Live Nuclei Audit"** again
3. **Expected: 0 findings** — green banner:
   > "All Compliance Controls Verified — 0 Exposures Detected"
   - Customer API → `401 Unauthorized` (token gate active)
   - Debug Config → `403 Forbidden` (locked)
   - Dashboard → `X-Frame-Options: DENY · CSP: default-src 'self'` enforced

### Step 3 — Forensic History & Export
1. Use **Scan History sidebar** to compare Relaxed vs. Strict scan reports
2. Click any historical scan to reload its findings and SHA-256 hashes
3. Click **"Print / Export"** to generate a clean printable forensic report

---

## 🔐 Security Architecture & Compliance Mapping

### STRICT_COMPLIANCE_MODE Controls

| Control | Relaxed (False) | Strict (True) |
| :--- | :--- | :--- |
| Customer API `/api/v1/customer/<id>` | Public — returns PII directly (IDOR) | Requires `X-Auth-Token: valid-session-token` → 401 if missing |
| Debug Config `/api/debug/config` | Returns internal config (200 OK) | 403 Forbidden |
| HTTP Security Headers | Not set | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy: default-src 'self'` |

### Indian IT Act 2000 Compliance Mappings

| Vulnerability | OWASP Category | IT Act 2000 Section | Legal Basis |
| :--- | :--- | :--- | :--- |
| Unauthenticated Customer API (IDOR) | API1:2023 — BOLA | **Section 43A** — Body Corporate Data Protection Failure | Body corporate negligent in implementing reasonable security practices; liable for damages on PII exposure (PAN card, account numbers) |
| Exposed Debug Configuration | API8:2023 — Security Misconfiguration | **Section 72A** — Disclosure of Information in Breach of Lawful Contract | Disclosure of system configuration aids adversarial exploitation; constitutes breach of implied security obligation |
| Missing HTTP Security Headers | API8:2023 — Security Misconfiguration | **Section 43** — Penalty for Damage to Computer System | Missing `X-Frame-Options` enables clickjacking; missing CSP enables XSS attacks on banking sessions |

### Digital Forensics Chain-of-Custody
Each Nuclei finding is hashed using `hashlib.sha256` over a canonical JSON payload:
```json
{ "template_id": "...", "matched_at": "...", "extracted_results": [...], "timestamp": "...", "scan_id": "..." }
```
This SHA-256 hash is:
- **Deterministic**: Same evidence → same hash every time
- **Tamper-evident**: Any modification to evidence data invalidates the hash
- **Stored in `forensics_vault.db`** alongside OWASP + IT Act + CERT-In + DPDP mappings

---

## 🧪 API Reference — Orchestrator (port 8000)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/scans/run` | POST | Trigger Nuclei scan → store + return forensic report |
| `/api/scans/history` | GET | List all past scan runs |
| `/api/scans/{scan_id}` | GET | Detailed findings + hashes for a scan |
| `/api/target/status` | GET | Current compliance mode of Flask target |
| `/api/target/toggle` | POST | Toggle target compliance mode |
| `/docs` | GET | Interactive Swagger API documentation |

---

## 📚 References

- **OWASP API Security Top 10 (2023)**: https://owasp.org/API-Security/
- **Indian IT Act 2000 (Amended 2008)**: https://www.meity.gov.in/writereaddata/files/it_act_2000_updated.pdf
- **CERT-In 2022 Directives**: https://www.cert-in.org.in/
- **DPDP Act 2023**: https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf
- **Nuclei v3 Documentation**: https://nuclei.projectdiscovery.io/
- **Project Discovery Templates**: https://github.com/projectdiscovery/nuclei-templates

