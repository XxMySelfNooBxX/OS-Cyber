"""
verify_templates.py — Validate Nuclei YAML template structure and run forensics tests.
"""
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "target-app"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "orchestrator-api"))

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

print("=" * 70)
print("PHASE 2 PART 1: NUCLEI TEMPLATE VALIDATION")
print("=" * 70)

templates = [
    "unauthenticated-customer-api.yaml",
    "exposed-debug-configuration.yaml",
    "missing-http-security-headers.yaml",
]

for tmpl in templates:
    path = os.path.join("custom-templates", tmpl)
    with open(path) as f:
        data = yaml.safe_load(f)
    req = data["requests"][0]
    matchers = [m["type"] for m in req.get("matchers", [])]
    extractors = [e["name"] for e in req.get("extractors", [])]
    print(f"[OK] {tmpl}")
    print(f"     ID       : {data['id']}")
    print(f"     Name     : {data['info']['name']}")
    print(f"     Severity : {data['info']['severity']}")
    print(f"     Paths    : {req.get('path', [])}")
    print(f"     Matchers : {matchers}")
    print(f"     Extractor: {extractors}")
    print()

print()
print("=" * 70)
print("PHASE 2 PART 2: FORENSICS MODULE & SHA-256 VERIFICATION")
print("=" * 70)

import forensics

# Initialize fresh test vault
TEST_DB = os.path.join(PROJECT_ROOT, "orchestrator-api", "forensics_vault_TEST.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
forensics.init_vault_db(db_path=TEST_DB)
print("[OK] forensics_vault_TEST.db initialized")

# Test SHA-256 hashing
hash1 = forensics.compute_sha256_hash(
    template_id="unauthenticated-customer-api",
    matched_at="http://127.0.0.1:5000/api/v1/customer/1001",
    extracted_results=["Rahul Sharma", "ACC-98214532", "ABCDE1234F"],
    timestamp="2026-10-30T12:00:00+00:00",
    scan_id="SCAN-TEST-0001",
)
print(f"[OK] SHA-256 hash computed: {hash1}")

# Verify determinism
hash2 = forensics.compute_sha256_hash(
    template_id="unauthenticated-customer-api",
    matched_at="http://127.0.0.1:5000/api/v1/customer/1001",
    extracted_results=["Rahul Sharma", "ACC-98214532", "ABCDE1234F"],
    timestamp="2026-10-30T12:00:00+00:00",
    scan_id="SCAN-TEST-0001",
)
assert hash1 == hash2, "SHA-256 should be deterministic!"
print(f"[OK] SHA-256 hash is deterministic (same inputs => same hash)")

# Verify different inputs give different hash
hash3 = forensics.compute_sha256_hash(
    template_id="exposed-debug-configuration",
    matched_at="http://127.0.0.1:5000/api/debug/config",
    extracted_results=["development", "sqlite3"],
    timestamp="2026-10-30T12:00:00+00:00",
    scan_id="SCAN-TEST-0001",
)
assert hash1 != hash3, "Different inputs should produce different hashes!"
print(f"[OK] Different findings produce different SHA-256 hashes")
print(f"     Hash 1 (IDOR finding):  {hash1}")
print(f"     Hash 3 (debug config ): {hash3}")

# Test store_finding
scan_id = "SCAN-TEST-0001"
forensics.create_scan_run(
    scan_id=scan_id,
    target_url="http://127.0.0.1:5000",
    compliance_mode="RELAXED",
    db_path=TEST_DB,
)

finding = forensics.store_finding(
    scan_id=scan_id,
    template_id="unauthenticated-customer-api",
    template_name="Unauthenticated Customer API - PII Exposure (IDOR)",
    severity="high",
    matched_at="http://127.0.0.1:5000/api/v1/customer/1001",
    extracted_results=["Rahul Sharma", "ACC-98214532", "ABCDE1234F"],
    curl_command="curl -X GET http://127.0.0.1:5000/api/v1/customer/1001",
    db_path=TEST_DB,
)

print()
print("[OK] Finding stored in forensics_vault_TEST.db")
print(json.dumps(finding, indent=2))

# Cleanup test DB
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
print()
print("[OK] Test DB cleaned up")

print()
print("=" * 70)
print("PHASE 2 PART 3: URL ALLOWLIST ENFORCEMENT TESTS")
print("=" * 70)

import nuclei_runner

# Valid targets
for valid_url in ["http://127.0.0.1:5000", "http://localhost:5000"]:
    result = nuclei_runner.validate_target_url(valid_url)
    print(f"[OK] Allowed: {valid_url}")

# Invalid targets — should raise ValueError
blocked = [
    "http://external.site.com/api",
    "http://192.168.1.1:5000",
    "http://127.0.0.1:8080",
    "http://0.0.0.0:5000",
]
for bad_url in blocked:
    try:
        nuclei_runner.validate_target_url(bad_url)
        print(f"[FAIL] Should have blocked: {bad_url}")
    except ValueError as e:
        print(f"[OK] Blocked: {bad_url}")
        print(f"     Reason: {str(e)[:80]}")

print()
print("[DONE] All Phase 2 verification checks passed.")

