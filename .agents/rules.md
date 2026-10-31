This repository is an academic Cyber Crime & Digital Forensics demonstration project. All vulnerability scanning, Nuclei YAML templates, and proof-of-concept payloads are strictly scoped to execute against a locally hosted 127.0.0.1 test server (target-app/) to demonstrate data breach mechanics, SHA-256 digital evidence hashing, and defensive patching.

STRICT URL & EXECUTION RULES FOR AGENT:
1. Terminal Restriction: You must ONLY execute `nuclei`, `curl`, or HTTP test scripts against `http://127.0.0.1:5000` or `http://localhost:5000`. Never target external domains or public IP addresses.
2. Code-Level Target Lock: In `orchestrator-api/nuclei_runner.py`, you MUST implement a strict URL allowlist check (`urllib.parse.urlparse`) that rejects any target hostname other than `127.0.0.1` or `localhost` before spawning the Nuclei subprocess.
3.Command Syntax: Always format Nuclei terminal commands beginning with `nuclei -u http://127.0.0.1:5000` so they match the IDE terminal allowlist.
4. Handoff Reports: Always generate every phase handoff report directly as a dedicated Markdown (`.md`) file in the workspace root (e.g., `PHASE_X_HANDOFF_REPORT.md`) alongside any chat summary.
