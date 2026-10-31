# PHASE 3 HANDOFF REPORT: React Dashboard UI & Unified Platform Deployment

**Project**: Academic Cyber Crime & Digital Forensics Demonstration  
**Phase**: 3 (Final Phase) — React + Tailwind Dashboard UI, Unified Launcher & End-to-End Orchestration  
**Status**: Completed, Verified & Built Successfully ✅  

---

## 1. Complete Workspace File Tree

```
project sem 7/
├── .agents/
│   └── rules.md                          (URL allowlist & execution safeguards)
├── custom-templates/
│   ├── exposed-debug-configuration.yaml  (Nuclei v3: Medium — /api/debug/config exposure)
│   ├── missing-http-security-headers.yaml(Nuclei v3: Low — Missing X-Frame-Options & CSP)
│   └── unauthenticated-customer-api.yaml (Nuclei v3: High — IDOR/PII leaks on customer endpoints)
├── target-app/
│   ├── app.py                            (Flask Target Server on port 5000, 659 lines)
│   ├── cyber_bank.db                     (SQLite DB: customers & digital forensics audit_logs)
│   ├── requirements.txt                  (flask>=2.3.0, flask-cors>=4.0.0)
│   └── seed_db.py                        (Database schema & forensic seeder)
├── orchestrator-api/
│   ├── forensics.py                      (Forensics vault, SHA-256 chain-of-custody, IT Act mappings)
│   ├── forensics_vault.db                (SQLite: scan_runs & tamper-evident findings)
│   ├── main.py                           (FastAPI Orchestrator on port 8000, 251 lines)
│   ├── nuclei_runner.py                  (Allowlist-guarded Nuclei subprocess runner, 215 lines)
│   └── requirements.txt                  (fastapi, uvicorn, pydantic, httpx)
├── dashboard-ui/
│   ├── index.html                        (HTML shell with print stylesheet)
│   ├── package.json                      (React 18, Vite 5, Tailwind CSS, Lucide Icons)
│   ├── postcss.config.js                 (PostCSS configuration)
│   ├── tailwind.config.js                (Tailwind dark theme tokens)
│   ├── vite.config.js                    (Vite config on port 5173)
│   └── src/
│       ├── App.jsx                       (Main Governance Center Dashboard state & view)
│       ├── index.css                     (Tailwind directives & custom cyber aesthetics)
│       ├── main.jsx                      (React entry point)
│       ├── api/
│       │   └── orchestrator.js           (FastAPI client for scans, status & toggles)
│       └── components/
│           ├── ControlBar.jsx            (Live posture banner, toggle button & scan trigger)
│           ├── FindingCard.jsx           (Forensic findings, extracted PII, SHA-256 & IT Act grid)
│           ├── MetricCards.jsx           (Executive severity summary & scan metadata)
│           ├── ScanHistorySidebar.jsx    (Historical scan browser & report selector)
│           └── SeverityBadge.jsx         (HIGH, MEDIUM, LOW, INFO badge chips)
├── .gitignore                            (Excludes node_modules, dist, __pycache__, logs)
├── start_project.ps1                     (Portable one-click 3-tier launcher script)
├── README.md                             (Comprehensive documentation & architecture guide)
├── PHASE_1B_HANDOFF_REPORT.md            (Target server report)
├── PHASE_2_HANDOFF_REPORT.md             (Templates & orchestrator report)
└── PHASE_3_HANDOFF_REPORT.md             (Frontend dashboard & final deployment report)
```

---

## 2. Summary of Frontend UI Components

| Component | File | Responsibilities |
| :--- | :--- | :--- |
| **App** | `src/App.jsx` | Coordinates live status polling (8s), scan executions, historical scan selection, and renders either the zero-exposure hardened banner or interactive finding cards. |
| **ControlBar** | `src/components/ControlBar.jsx` | Displays live target connectivity & compliance posture (`RELAXED MODE - UNPROTECTED` in red vs. `STRICT COMPLIANCE MODE - HARDENED` in emerald), provides real-time toggle button (`POST /api/target/toggle`), primary scan action, and print/export trigger. |
| **MetricCards** | `src/components/MetricCards.jsx` | 4 executive metric cards: Total Findings, High Severity, Medium Severity, Low Severity, alongside the unique Scan ID and UTC timestamp. |
| **FindingCard** | `src/components/FindingCard.jsx` | Detailed finding breakdown: matched endpoint, extracted PII/config chips (Customer Name, Account Number, PAN Card), SHA-256 chain-of-custody box with "Copy Hash" button, reproducible `curl` command, and collapsible Legal Compliance Accordion (OWASP API Security, Section 43A / 72A / 43 of Indian IT Act 2000, CERT-In 2022, DPDP Act 2023, and remediation). |
| **ScanHistorySidebar** | `src/components/ScanHistorySidebar.jsx` | Displays past audit runs from `forensics_vault.db` with status indicators, timestamps, and one-click report loading. |
| **SeverityBadge** | `src/components/SeverityBadge.jsx` | Color-coded severity badge (Red/Amber/Blue/Gray). |

---

## 3. Production Build Verification (`npm run build`)

Executing `npm run build` inside `dashboard-ui/` produced a clean, zero-error production build:

```
> dashboard-ui@1.0.0 build
> vite build

vite v5.4.21 building for production...
transforming...
✓ 1504 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.85 kB │ gzip:  0.49 kB
dist/assets/index-BOA_5k4y.css   18.49 kB │ gzip:  4.13 kB
dist/assets/index-CdlkxNaJ.js   172.95 kB │ gzip: 53.34 kB
✓ built in 3.37s
```

---

## 4. Live Demonstration Script for Evaluators

When presenting the project to examiners or evaluators, follow this script:

### Step 1: Launch the 3-Tier Platform
Open PowerShell and run:
```powershell
.\start_project.ps1
```
Show evaluators that three distinct services are active:
- **Target Flask App** on `http://127.0.0.1:5000` (backed by `cyber_bank.db`)
- **Orchestrator API** on `http://127.0.0.1:8000` (backed by `forensics_vault.db`, Swagger UI at `/docs`)
- **React Governance Center** on `http://127.0.0.1:5173`

### Step 2: Demonstrate Data Breach in Relaxed Mode
1. Open `http://127.0.0.1:5173` in a browser.
2. Note the banner: `⚠️ RELAXED MODE — UNPROTECTED`.
3. Click **"Run Live Nuclei Audit"**.
4. Point out the live findings:
   - **IDOR / PII Leaks**: Rahul Sharma & Priya Verma's PAN Card numbers and Bank Account numbers extracted live from the API without authentication.
   - **Debug Disclosure**: Internal environment settings (`app_env: development`, `db_engine: sqlite3`).
   - **Security Headers**: Missing `X-Frame-Options` and `Content-Security-Policy`.
5. Point out the **Digital Forensics Chain-of-Custody**:
   - Every finding has an immutable `SHA-256` integrity hash computed over the evidence.
   - Show the mapping to **Section 43A of the Indian IT Act 2000** (body corporate failure to protect sensitive personal data) and **DPDP Act 2023**.

### Step 3: Demonstrate Defensive Patching & Hardening
1. Click **"Toggle Compliance Mode"**.
2. Show the posture update: `✅ STRICT COMPLIANCE MODE — HARDENED`.
3. Click **"Run Live Nuclei Audit"** again.
4. Point out the green banner: **"All Compliance Controls Verified — 0 Exposures Detected"**.
   - Explain how `401 Unauthorized` blocked unauthenticated PII access.
   - Explain how `403 Forbidden` disabled debug endpoints.
   - Explain how `X-Frame-Options: DENY` and CSP headers mitigated clickjacking and injection.

### Step 4: Digital Evidence & Audit History
1. Click through the **Scan History Sidebar** to contrast the Relaxed scan vs. the Strict scan.
2. Click **"Print / Export"** to display the clean forensic audit report ready for court or regulatory submission.

