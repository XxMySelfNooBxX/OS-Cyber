"""
generate_guide_pdf.py
Generates a publication-grade, beautifully formatted PDF guide:
"CyberBank Platform — Antigravity Terminal Setup & Evaluator Demo Guide"
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Antigravity_Terminal_Setup_Guide.pdf")

# ----------------------------------------------------------------------
# Numbered Canvas for Two-Pass Page Count ("Page X of Y")
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "CyberBank — Antigravity Terminal Setup & Execution Guide")
            self.drawRightString(612 - 54, 755, "Academic Cyber Crime & Forensics Platform")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 612 - 54, 747)
        
        # Running footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        
        self.drawString(54, 32, "Confidential — Academic Research & Regulatory Demonstration | GitHub: XxMySelfNooBxX/OS-Cyber")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def create_code_block(code_text: str, styles: dict) -> Table:
    """Renders a dark-themed monospace code block with styled background."""
    formatted_lines = code_text.strip().replace("\n", "<br/>").replace(" ", "&nbsp;")
    code_para = Paragraph(f"<font face='Courier' color='#38BDF8' size=8.5>{formatted_lines}</font>", styles["Code"])
    t = Table([[code_para]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
    ]))
    return t


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    base_styles = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "DocTitle",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            alignment=0,
            spaceAfter=4,
        ),
        "Subtitle": ParagraphStyle(
            "DocSubTitle",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
            spaceAfter=14,
        ),
        "H1": ParagraphStyle(
            "Heading1",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#0284C7"),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "Heading2",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1E293B"),
            leftIndent=15,
            spaceAfter=3,
        ),
        "Code": ParagraphStyle(
            "CodeStyle",
            parent=base_styles["Code"],
            fontName="Courier",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#38BDF8"),
        ),
        "Callout": ParagraphStyle(
            "Callout",
            parent=base_styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#047857"),
        ),
    }

    story = []

    # ------------------------------------------------------------------
    # HEADER BANNER TABLE
    # ------------------------------------------------------------------
    header_content = [
        [
            Paragraph("<b>CYBER CRIME & DIGITAL FORENSICS PLATFORM</b>", ParagraphStyle(
                "BannerTitle", fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#0F172A")
            )),
            Paragraph("<font color='#0284C7'><b>ACADEMIC LAB GUIDE</b></font>", ParagraphStyle(
                "BannerTag", fontName="Helvetica-Bold", fontSize=9, alignment=2, textColor=colors.HexColor("#0284C7")
            ))
        ],
        [
            Paragraph("Terminal Setup, Dependency Installation & Live Evaluator Script", styles["Subtitle"]),
            Paragraph("<b>Target Host:</b> 127.0.0.1", ParagraphStyle("Right", alignment=2, fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#64748B")))
        ]
    ]
    banner_table = Table(header_content, colWidths=[360, 144])
    banner_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(banner_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=10))

    # Repository callout box
    repo_box = Table([[
        Paragraph(
            "<b>Official GitHub Repository:</b> <font color='#0284C7'><u>https://github.com/XxMySelfNooBxX/OS-Cyber</u></font><br/>"
            "This repository contains the complete 3-tier architecture: Flask QA Target, FastAPI Orchestrator, React Dashboard UI, and custom Nuclei v3 compliance templates.",
            styles["Body"]
        )
    ]], colWidths=[504])
    repo_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(repo_box)
    story.append(Spacer(1, 8))

    # ------------------------------------------------------------------
    # SECTION 1: SYSTEM PREREQUISITES
    # ------------------------------------------------------------------
    story.append(Paragraph("1. System Prerequisites Checklist", styles["H1"]))
    story.append(Paragraph("Before executing commands, ensure your friend's laptop has the following standard tools installed and added to the Windows PATH:", styles["Body"]))

    prereq_data = [
        ["Prerequisite", "Required Version", "Verification Command", "Purpose in Architecture"],
        ["Python", "3.11 or 3.12", "python --version", "Powers Flask target API (5000) & FastAPI orchestrator (8000)"],
        ["Node.js / npm", "Node 18+ / npm 9+", "node -v; npm -v", "Builds & serves React Vite Governance Dashboard (5173)"],
        ["Git", "2.30+", "git --version", "Clones repository and manages code versions"],
        ["Nuclei Scanner", "v3.11+", "nuclei -version", "Automated compliance scanner executing custom YAML templates"],
    ]
    prereq_table = Table(prereq_data, colWidths=[80, 85, 125, 214])
    prereq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(prereq_table)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # SECTION 2: ONE-TIME SETUP
    # ------------------------------------------------------------------
    story.append(Paragraph("2. Quick One-Time Setup (Terminal Commands)", styles["H1"]))
    story.append(Paragraph("Open the <b>Antigravity Terminal</b> (or PowerShell as Administrator) and paste the following sequential block to clone the codebase and install all dependencies:", styles["Body"]))

    setup_code = (
        "# Step A: Clone repository and enter directory\n"
        "git clone https://github.com/XxMySelfNooBxX/OS-Cyber.git\n"
        "cd OS-Cyber\n\n"
        "# Step B: Install Python backend dependencies (Target App & Orchestrator)\n"
        "python -m pip install -r target-app/requirements.txt\n"
        "python -m pip install -r orchestrator-api/requirements.txt\n\n"
        "# Step C: Install React Dashboard frontend dependencies\n"
        "cd dashboard-ui\n"
        "npm install\n"
        "cd ..\n\n"
        "# Step D: (Optional) Install Nuclei CLI if not present on system PATH\n"
        "winget install projectdiscovery.nuclei"
    )
    story.append(create_code_block(setup_code, styles))
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # SECTION 3: LAUNCHING THE 3-TIER PLATFORM
    # ------------------------------------------------------------------
    story.append(Paragraph("3. Launching the 3-Tier Platform (One-Click)", styles["H1"]))
    story.append(Paragraph(
        "A portable startup script (<b>start_project.ps1</b>) is included in the project root. It dynamically locates Python on any machine and automatically spawns all three tiers:",
        styles["Body"]
    ))

    launch_code = "powershell -ExecutionPolicy Bypass -File .\\start_project.ps1"
    story.append(create_code_block(launch_code, styles))
    story.append(Spacer(1, 6))

    tier_data = [
        ["Tier Component", "Local Binding URL", "Backing Technology & Role"],
        ["Tier 1: Target Flask App", "http://127.0.0.1:5000", "Simulated banking API; seeds cyber_bank.db with customer records and forensic logs."],
        ["Tier 2: Orchestrator API", "http://127.0.0.1:8000", "FastAPI backend; manages forensics_vault.db, executes Nuclei scans, hashes evidence with SHA-256."],
        ["Tier 3: React Dashboard", "http://127.0.0.1:5173", "Dark-mode Cyber Governance Center; real-time compliance toggles, evidence inspection, PDF print."],
    ]
    tier_table = Table(tier_data, colWidths=[120, 130, 254])
    tier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284C7")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # SECTION 4: ALTERNATIVE MANUAL LAUNCH
    # ------------------------------------------------------------------
    story.append(Paragraph("4. Alternative Manual Launch (3 Separate Terminals)", styles["H1"]))
    story.append(Paragraph("If your friend prefers to view server logs in separate terminal windows, execute each command in its own PowerShell tab:", styles["Body"]))

    manual_code = (
        "# --- TERMINAL 1: Target Flask Server (Port 5000) ---\n"
        "cd target-app\n"
        "python seed_db.py\n"
        "python app.py\n\n"
        "# --- TERMINAL 2: FastAPI Orchestrator (Port 8000) ---\n"
        "cd orchestrator-api\n"
        "python main.py\n\n"
        "# --- TERMINAL 3: React Governance UI (Port 5173) ---\n"
        "cd dashboard-ui\n"
        "npm run dev"
    )
    story.append(create_code_block(manual_code, styles))
    story.append(Spacer(1, 10))

    # Page break for clean evaluator presentation script
    story.append(PageBreak())

    # ------------------------------------------------------------------
    # SECTION 5: LIVE DEMO SCRIPT FOR EVALUATORS
    # ------------------------------------------------------------------
    story.append(Paragraph("5. Step-by-Step Live Evaluator Demonstration Script", styles["H1"]))
    story.append(Paragraph(
        "Have your friend follow this exact sequence when demonstrating the project to evaluators, professors, or exam committees:",
        styles["Body"]
    ))

    steps = [
        ("Step 1: Open the Governance Dashboard",
         "Open browser at <b>http://127.0.0.1:5173</b>. Point out the live connectivity indicator to the target server and the active posture badge: <font color='#DC2626'><b>RELAXED MODE — UNPROTECTED</b></font>."),
        
        ("Step 2: Execute Vulnerability Audit in Relaxed Mode",
         "Click <b>'Run Live Nuclei Audit'</b>. Point out the live loading spinner while Nuclei scans the target API. The scan returns <b>4 Critical Vulnerabilities</b> (2 High, 1 Medium, 1 Low)."),
        
        ("Step 3: Demonstrate Digital Forensic Evidence & Data Exfiltration",
         "Inspect the findings: (a) <b>IDOR / PII Leak</b>: Live extraction of Rahul Sharma and Priya Verma's <b>PAN Card</b> & <b>Bank Account Numbers</b> without authentication. (b) <b>Debug Exposure</b>: Internal environment settings leaked. (c) <b>Security Headers Missing</b>: Absence of X-Frame-Options and CSP."),
        
        ("Step 4: Highlight Chain-of-Custody Hashing & Legal Compliance",
         "Show the <b>SHA-256 Digital Forensics Integrity Hash</b> computed over the evidence payload. Click <i>'Copy Hash'</i> to prove tamper-evidence. Expand the <b>Legal & Regulatory Accordion</b> to show statutory mapping to <b>Section 43A of the Indian IT Act 2000</b> (body corporate data protection failure) and <b>DPDP Act 2023</b>."),
        
        ("Step 5: Demonstrate Real-Time Defensive Patching",
         "Click <b>'Toggle Compliance Mode'</b>. The badge updates dynamically to <font color='#059669'><b>STRICT COMPLIANCE MODE — HARDENED</b></font>. Click <b>'Run Live Nuclei Audit'</b> again. The dashboard immediately displays the green banner: <b>'All Compliance Controls Verified — 0 Exposures Detected'</b>. Explain that authentication (HTTP 401), debug lockouts (HTTP 403), and CSP headers successfully neutralized all attack vectors."),
        
        ("Step 6: Forensic Audit History & Report Export",
         "Use the <b>Scan History Sidebar</b> to switch between the Relaxed (breached) and Strict (remediated) reports. Click <b>'Print / Export'</b> to show the clean printable evidence report formatted for courtroom or forensic archival.")
    ]

    for title, desc in steps:
        step_box = Table([
            [Paragraph(f"<b>{title}</b>", styles["H2"])],
            [Paragraph(desc, styles["Body"])]
        ], colWidths=[504])
        step_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(step_box)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # SECTION 6: TROUBLESHOOTING & COMMON PITFALLS
    # ------------------------------------------------------------------
    story.append(Paragraph("6. Troubleshooting & Common Pitfalls", styles["H1"]))
    trouble_data = [
        ["Issue / Symptom", "Root Cause", "Quick Resolution"],
        ["Script execution disabled error", "Windows ExecutionPolicy restriction", "Run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"],
        ["Nuclei: command not found", "Nuclei CLI not on system PATH", "Run: winget install projectdiscovery.nuclei (then reopen terminal)"],
        ["Port 5000 / 8000 already in use", "Previous python background task running", "Run: Get-Process python* | Stop-Process -Force"],
        ["npm install fails / takes too long", "Cached npm modules or slow mirror", "Run: npm cache clean --force; npm install in dashboard-ui/"],
    ]
    trouble_table = Table(trouble_data, colWidths=[120, 130, 254])
    trouble_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(trouble_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated PDF: {PDF_OUTPUT_PATH} ({os.path.getsize(PDF_OUTPUT_PATH)} bytes)")

if __name__ == "__main__":
    build_pdf()
