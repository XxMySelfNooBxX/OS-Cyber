# PHASE 1B HANDOFF REPORT: Flask QA Compliance & API Governance Test Server

**Project**: Academic Cyber Crime & Digital Forensics Demonstration  
**Target Application**: `target-app/`  
**Host Binding**: `http://127.0.0.1:5000`  
**Database**: SQLite3 (`cyber_bank.db`)  
**Status**: Completed & Verified  

---

## 1. Workspace File Tree

Files inside `target-app/`:

| File Path | Type | Line Count | Description |
| :--- | :--- | :--- | :--- |
| `target-app/app.py` | Python Script | 659 lines | Main Flask governance and test application |
| `target-app/cyber_bank.db` | SQLite Database | Binary | SQLite database containing `customers` and `audit_logs` |
| `target-app/requirements.txt` | Requirements | 2 lines | Python dependencies (`flask>=2.3.0`, `flask-cors>=4.0.0`) |
| `target-app/seed_db.py` | Python Script | 79 lines | DB initialization & forensic seed generator |

---

## 2. Implemented Route Table

| Endpoint | HTTP Method | Behavior (`STRICT_COMPLIANCE_MODE = False`) | Behavior (`STRICT_COMPLIANCE_MODE = True`) |
| :--- | :--- | :--- | :--- |
| `POST /api/toggle-compliance` | `POST` | Toggles state to `True`. Logs transition to `audit_logs`. Returns HTTP 200 JSON (or redirects to `/` if standard form submit). | Toggles state to `False`. Logs transition to `audit_logs`. Returns HTTP 200 JSON (or redirects to `/` if standard form submit). |
| `GET /` | `GET` | Renders HTML dashboard with relaxed status indicator and recent entries from `audit_logs`. Standard HTTP headers. | Renders HTML dashboard with strict status indicator, recent entries from `audit_logs`, and attaches security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy: default-src 'self'`. |
| `GET /style.css` | `GET` | Serves dashboard stylesheet (CSS). | Serves dashboard stylesheet (CSS); adheres to CSP `default-src 'self'`. |
| `GET /api/v1/customer/<int:account_id>` | `GET` | Queries `customers` table in `cyber_bank.db`. Returns customer record as JSON with HTTP 200 directly (unauthenticated/IDOR simulation). | Requires `X-Auth-Token: valid-session-token` header. Returns **HTTP 401 Unauthorized** if token is absent/invalid; returns customer JSON with HTTP 200 if valid. |
| `GET /api/v1/transactions/search` | `GET` | Reads query parameter `q`, executes parameterized query `WHERE full_name LIKE ?`, logs search query into `audit_logs`, and returns matching records as JSON with HTTP 200. | Identical search behavior and forensic audit logging, with security response headers enforced. |
| `GET /api/debug/config` | `GET` | Returns HTTP 200 JSON with diagnostic environment config (`{"app_env": "development", "debug_enabled": true, "service_version": "1.0.4", "db_engine": "sqlite3"}`). | Returns **HTTP 403 Forbidden** with JSON error message indicating debug config is disabled in strict mode. |

---

## 3. Database Connection & Helper Functions

### Database Connection Path
The database connection dynamically resolves relative to `app.py`:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cyber_bank.db")
```

### Core Helper Functions in `app.py`
1. **`get_db_connection() -> sqlite3.Connection`**:
   - Opens SQLite connection to `cyber_bank.db`.
   - Sets `conn.row_factory = sqlite3.Row` for dictionary-like column access.
2. **`insert_audit_log(event_type, ip_address, status, details, account_id=None) -> None`**:
   - Creates tamper-evident digital forensic entries in the `audit_logs` table with UTC ISO 8601 timestamps (`datetime.now(timezone.utc).isoformat()`).
3. **`get_recent_audit_logs(limit=50) -> list[dict]`**:
   - Retrieves the most recent audit records ordered newest first (`ORDER BY id DESC`) for live monitoring in the HTML dashboard.
4. **`query_customer_by_id(account_id: int) -> dict | None`**:
   - Parameterized query targeting `customers` table by primary key `id`.
5. **`search_customers_by_name(query: str) -> list[dict]`**:
   - Executes parameterized query `WHERE full_name LIKE ?` with wildcard matching (`%query%`) to prevent SQL injection.
6. **`apply_security_headers(response)`**:
   - Flask `@app.after_request` middleware attaching strict security headers when `STRICT_COMPLIANCE_MODE` is enabled.

---

## 4. How to Run the Server

```bash
cd "target-app"
python app.py
```
- Server launches on `http://127.0.0.1:5000`

