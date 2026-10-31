"""
verify_e2e.py — End-to-End Verification Script for Phase 2

Tests:
1. Raw Nuclei JSONL output (STRICT_COMPLIANCE_MODE=False) — should find 3 templates
2. Raw Nuclei JSONL output (STRICT_COMPLIANCE_MODE=True) — should find 0 findings
3. Orchestrator FastAPI scan endpoint simulation (both modes)
"""

import sys
import os
import json
import threading
import time
import subprocess

# Add paths for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "target-app"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "orchestrator-api"))

from target_app_runner import start_flask_server, stop_flask_server
import forensics
import nuclei_runner

TARGET_URL = "http://127.0.0.1:5000"
NUCLEI_BIN = nuclei_runner.resolve_nuclei_binary()
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "custom-templates")

print("=" * 70)
print("PHASE 2 END-TO-END VERIFICATION")
print("=" * 70)
print(f"Nuclei Binary: {NUCLEI_BIN}")
print(f"Templates Dir: {TEMPLATES_DIR}")
print(f"Target URL:    {TARGET_URL}")
print()

