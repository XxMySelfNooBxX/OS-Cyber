"""
CyberBank QA Compliance & API Governance Test Server
Target application demonstrating API governance, digital forensics audit logging,
and strict compliance security controls.
"""

import os
import sqlite3
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string, Response, redirect
from flask_cors import CORS

# ---------------------------------------------------------
# Configuration & Database Setup
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cyber_bank.db")

app = Flask(__name__)
CORS(app)

# Global compliance state
STRICT_COMPLIANCE_MODE: bool = False


# ---------------------------------------------------------
# Database Helper Functions
# ---------------------------------------------------------
def get_db_connection() -> sqlite3.Connection:
    """Create and return a connection to cyber_bank.db with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert_audit_log(
    event_type: str,
    ip_address: str,
    status: str,
    details: str,
    account_id: int | None = None,
) -> None:
    """Insert a digital forensics audit log record into audit_logs table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO audit_logs (timestamp, event_type, account_id, ip_address, status, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (now_iso, event_type, account_id, ip_address, status, details),
    )
    conn.commit()
    conn.close()


def get_recent_audit_logs(limit: int = 50) -> list[dict]:
    """Fetch recent audit log records ordered newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, event_type, account_id, ip_address, status, details
        FROM audit_logs
        ORDER BY id DESC
        LIMIT ?
    """,
        (limit,),
    )
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs


def query_customer_by_id(account_id: int) -> dict | None:
    """Fetch customer record by primary key id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, email, account_number, balance, pan_card
        FROM customers
        WHERE id = ?
    """,
        (account_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_customers_by_name(query: str) -> list[dict]:
    """Search customers table using parameterized SQLite query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if query:
        cursor.execute(
            """
            SELECT id, full_name, email, account_number, balance, pan_card
            FROM customers
            WHERE full_name LIKE ?
        """,
            (f"%{query}%",),
        )
    else:
        cursor.execute(
            """
            SELECT id, full_name, email, account_number, balance, pan_card
            FROM customers
        """
        )
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


# ---------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------
@app.after_request
def apply_security_headers(response):
    """
    Attach standard HTTP security headers when STRICT_COMPLIANCE_MODE is True:
    - X-Frame-Options: DENY
    - X-Content-Type-Options: nosniff
    - Content-Security-Policy: default-src 'self'
    """
    if STRICT_COMPLIANCE_MODE:
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# ---------------------------------------------------------
# Dashboard & Stylesheet Routes
# ---------------------------------------------------------
CSS_CONTENT = """
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #1e293b;
    --border-color: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-blue: #38bdf8;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --accent-amber: #f59e0b;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 24px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}

.brand-title {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.status-badge {
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.5px;
}

.status-strict {
    background-color: rgba(34, 197, 94, 0.15);
    color: var(--accent-green);
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-relaxed {
    background-color: rgba(239, 68, 68, 0.15);
    color: var(--accent-red);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
}

.card-title {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.card-value {
    font-size: 1.25rem;
    font-weight: 700;
}

.card-desc {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

.toggle-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 28px;
    flex-wrap: wrap;
    gap: 16px;
}

.btn-toggle {
    background-color: var(--accent-blue);
    color: #0f172a;
    border: none;
    padding: 10px 22px;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    font-size: 0.95rem;
    transition: opacity 0.2s ease, transform 0.1s ease;
}

.btn-toggle:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.btn-toggle:active {
    transform: translateY(0);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 600;
}

.table-container {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 32px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    text-align: left;
}

th {
    background-color: rgba(15, 23, 42, 0.6);
    color: var(--text-secondary);
    font-weight: 600;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}

tr:last-child td {
    border-bottom: none;
}

tr:hover td {
    background-color: rgba(255, 255, 255, 0.02);
}

.badge {
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.badge-success {
    background-color: rgba(34, 197, 94, 0.2);
    color: var(--accent-green);
}

.badge-flagged {
    background-color: rgba(245, 158, 11, 0.2);
    color: var(--accent-amber);
}

.code-pill {
    background-color: #0f172a;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.8rem;
    color: var(--accent-blue);
}

footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.8rem;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
}
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberBank QA Compliance & API Governance Dashboard</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="brand-title">
                    <span>🛡️ CyberBank Compliance Engine</span>
                </div>
                <div class="brand-subtitle">Digital Forensics, Regulatory Governance & API Hardening Controller</div>
            </div>
            <div>
                {% if strict_mode %}
                    <span class="status-badge status-strict">● STRICT COMPLIANCE ACTIVE</span>
                {% else %}
                    <span class="status-badge status-relaxed">○ COMPLIANCE DISABLED (RELAXED)</span>
                {% endif %}
            </div>
        </header>

        <section class="toggle-section">
            <div>
                <h3>Governance Policy Enforcement</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">
                    Current Mode: <strong>{{ "STRICT COMPLIANCE (Hardened)" if strict_mode else "DEVELOPMENT / RELAXED (Vulnerable)" }}</strong>
                </p>
            </div>
            <form action="/api/toggle-compliance" method="POST" style="margin: 0;">
                <button type="submit" class="btn-toggle">
                    Switch to {{ "Relaxed Mode" if strict_mode else "Strict Compliance Mode" }}
                </button>
            </form>
        </section>

        <div class="grid">
            <div class="card">
                <div class="card-title">HTTP Security Headers</div>
                <div class="card-value" style="color: {{ 'var(--accent-green)' if strict_mode else 'var(--accent-red)' }};">
                    {{ "ENFORCED" if strict_mode else "OFF" }}
                </div>
                <div class="card-desc">
                    {{ "X-Frame-Options, X-Content-Type-Options, CSP" if strict_mode else "Headers stripped (remediation demo)" }}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Customer API Authentication</div>
                <div class="card-value" style="color: {{ 'var(--accent-green)' if strict_mode else 'var(--accent-red)' }};">
                    {{ "TOKEN REQUIRED" if strict_mode else "PUBLIC ACCESS" }}
                </div>
                <div class="card-desc">
                    {{ "Requires X-Auth-Token: valid-session-token" if strict_mode else "IDOR / unauthenticated access enabled" }}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Debug Config Endpoint</div>
                <div class="card-value" style="color: {{ 'var(--accent-green)' if strict_mode else 'var(--accent-red)' }};">
                    {{ "403 FORBIDDEN" if strict_mode else "200 EXPOSED" }}
                </div>
                <div class="card-desc">
                    {{ "Diagnostic endpoint disabled in strict mode" if strict_mode else "/api/debug/config publicly accessible" }}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Total Audit Trail Records</div>
                <div class="card-value" style="color: var(--accent-blue);">
                    {{ audit_logs|length }}
                </div>
                <div class="card-desc">Forensic logs in cyber_bank.db</div>
            </div>
        </div>

        <div class="section-header">
            <h2 class="section-title">Digital Forensics Audit Trail (cyber_bank.db)</h2>
            <span style="font-size: 0.85rem; color: var(--text-secondary);">Showing {{ audit_logs|length }} latest events</span>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp (UTC)</th>
                        <th>Event Type</th>
                        <th>Account ID</th>
                        <th>IP Address</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in audit_logs %}
                    <tr>
                        <td><span class="code-pill">#{{ log.id }}</span></td>
                        <td style="white-space: nowrap;">{{ log.timestamp }}</td>
                        <td><strong>{{ log.event_type }}</strong></td>
                        <td>{{ log.account_id if log.account_id else '—' }}</td>
                        <td><span class="code-pill">{{ log.ip_address }}</span></td>
                        <td>
                            {% if log.status == 'SUCCESS' %}
                                <span class="badge badge-success">{{ log.status }}</span>
                            {% else %}
                                <span class="badge badge-flagged">{{ log.status }}</span>
                            {% endif %}
                        </td>
                        <td>{{ log.details }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <footer>
            CyberBank Academic QA Compliance & API Governance Test Server | http://127.0.0.1:5000 | Connected to cyber_bank.db
        </footer>
    </div>
</body>
</html>
"""


@app.route("/style.css", methods=["GET"])
def serve_stylesheet():
    """Serve CSS stylesheet compliant with Content-Security-Policy default-src 'self'."""
    return Response(CSS_CONTENT, mimetype="text/css")


@app.route("/", methods=["GET"])
def dashboard():
    """
    Clean HTML dashboard displaying current compliance mode,
    toggle controls, and recent entries from audit_logs table.
    """
    logs = get_recent_audit_logs(limit=50)
    return render_template_string(
        DASHBOARD_HTML,
        strict_mode=STRICT_COMPLIANCE_MODE,
        audit_logs=logs,
    )


# ---------------------------------------------------------
# API Governance & Compliance Routes
# ---------------------------------------------------------
@app.route("/api/toggle-compliance", methods=["POST"])
def toggle_compliance():
    """
    Switch STRICT_COMPLIANCE_MODE between True and False.
    Accepts optional JSON payload or form data, or inverts current state.
    """
    global STRICT_COMPLIANCE_MODE

    data = request.get_json(silent=True) or {}
    if "strict_compliance_mode" in data:
        STRICT_COMPLIANCE_MODE = bool(data["strict_compliance_mode"])
    elif "enabled" in data:
        STRICT_COMPLIANCE_MODE = bool(data["enabled"])
    elif "mode" in request.form:
        val = request.form.get("mode", "").strip().lower()
        if val in ("true", "1", "enable", "enabled"):
            STRICT_COMPLIANCE_MODE = True
        elif val in ("false", "0", "disable", "disabled"):
            STRICT_COMPLIANCE_MODE = False
        else:
            STRICT_COMPLIANCE_MODE = not STRICT_COMPLIANCE_MODE
    else:
        STRICT_COMPLIANCE_MODE = not STRICT_COMPLIANCE_MODE

    # Audit log the compliance mode toggle
    mode_str = "ENABLED" if STRICT_COMPLIANCE_MODE else "DISABLED"
    insert_audit_log(
        event_type="COMPLIANCE_TOGGLE",
        ip_address=request.remote_addr or "127.0.0.1",
        status="SUCCESS",
        details=f"STRICT_COMPLIANCE_MODE set to {mode_str}",
    )

    # If called from standard HTML form POST without application/json accept header, redirect back
    if (
        request.content_type == "application/x-www-form-urlencoded"
        and "application/json" not in request.headers.get("Accept", "")
    ):
        return redirect("/")

    return jsonify(
        {
            "status": "success",
            "strict_compliance_mode": STRICT_COMPLIANCE_MODE,
            "message": f"Strict compliance mode is now {mode_str}",
        }
    ), 200


@app.route("/api/v1/customer/<int:account_id>", methods=["GET"])
def get_customer(account_id: int):
    """
    Queries customers table in cyber_bank.db for given account_id.
    - STRICT_COMPLIANCE_MODE = False: Returns customer JSON directly with HTTP 200.
    - STRICT_COMPLIANCE_MODE = True: Requires 'X-Auth-Token: valid-session-token', returns 401 if missing.
    """
    if STRICT_COMPLIANCE_MODE:
        token = request.headers.get("X-Auth-Token")
        if not token or token != "valid-session-token":
            return jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Missing or invalid X-Auth-Token header required in strict compliance mode.",
                }
            ), 401

    customer = query_customer_by_id(account_id)
    if customer is None:
        return jsonify(
            {
                "error": "Not Found",
                "message": f"Customer with account ID {account_id} not found.",
            }
        ), 404

    return jsonify(customer), 200


@app.route("/api/v1/transactions/search", methods=["GET"])
def search_transactions():
    """
    Reads query parameter 'q' and searches 'full_name' in customers table
    using parameterized SQLite queries, returning matching records as JSON.
    Also logs each search into the audit_logs table.
    """
    q = request.args.get("q", "").strip()
    results = search_customers_by_name(q)

    # Digital forensics: Log each search into audit_logs table
    ip_addr = request.remote_addr or "127.0.0.1"
    details_str = f"Transaction search query executed for term: '{q}' (matches: {len(results)})"
    insert_audit_log(
        event_type="SEARCH",
        ip_address=ip_addr,
        status="SUCCESS",
        details=details_str,
    )

    return jsonify(results), 200


@app.route("/api/debug/config", methods=["GET"])
def debug_config():
    """
    Diagnostic environment configuration route:
    - STRICT_COMPLIANCE_MODE = False: Returns HTTP 200 JSON with diagnostic settings.
    - STRICT_COMPLIANCE_MODE = True: Returns HTTP 403 Forbidden.
    """
    if STRICT_COMPLIANCE_MODE:
        return jsonify(
            {
                "error": "Forbidden",
                "message": "Debug configuration endpoint is disabled when strict compliance mode is active.",
            }
        ), 403

    return jsonify(
        {
            "app_env": "development",
            "debug_enabled": True,
            "service_version": "1.0.4",
            "db_engine": "sqlite3",
        }
    ), 200


# ---------------------------------------------------------
# Server Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

