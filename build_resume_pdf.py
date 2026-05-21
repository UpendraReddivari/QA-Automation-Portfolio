"""
Self-contained PDF generator for Upendra Reddivari's tailored QA resume.
Uses only the Python standard library. Produces a PDF with built-in Helvetica
fonts (no embedding needed).
"""

import zlib
from pathlib import Path

# ---------------------------------------------------------------------------
# Helvetica AFM character widths (units: 1/1000 em). Used for text wrapping.
# Bold uses slightly different widths but the regular table is a good
# approximation for layout purposes.
# ---------------------------------------------------------------------------
HELV_W = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
    "'": 191, '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333,
    '.': 278, '/': 278,
    '0': 556, '1': 556, '2': 556, '3': 556, '4': 556, '5': 556, '6': 556,
    '7': 556, '8': 556, '9': 556,
    ':': 278, ';': 278, '<': 584, '=': 584, '>': 584, '?': 556, '@': 1015,
    'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722,
    'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
    'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611,
    '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556, '`': 333,
    'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556,
    'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556,
    'o': 556, 'p': 556, 'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556,
    'v': 500, 'w': 722, 'x': 500, 'y': 500, 'z': 500,
    '{': 334, '|': 260, '}': 334, '~': 584,
}
# Bold widths roughly +5%
HELVB_FACTOR = 1.05


def text_width(text: str, font_size: float, bold: bool = False) -> float:
    """Approximate width in points for a string of Helvetica text."""
    w = 0.0
    for ch in text:
        w += HELV_W.get(ch, 500)
    pts = w * font_size / 1000.0
    if bold:
        pts *= HELVB_FACTOR
    return pts


def wrap_text(text: str, max_width: float, font_size: float,
              bold: bool = False) -> list[str]:
    """Word-wrap a single line of text to fit max_width in points."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        candidate = w if cur == '' else cur + ' ' + w
        if text_width(candidate, font_size, bold) <= max_width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def escape_pdf_string(s: str) -> str:
    """Escape parens and backslashes for PDF literal strings."""
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------
class PDF:
    PAGE_W = 595        # A4 width in points
    PAGE_H = 842        # A4 height in points
    MARGIN_L = 50
    MARGIN_R = 50
    MARGIN_T = 50
    MARGIN_B = 50

    def __init__(self):
        self.pages = []          # list of content streams (bytes)
        self.current = []        # current page commands as list of strings
        self.cursor_y = self.PAGE_H - self.MARGIN_T
        self._new_page()

    # -- low-level page management ----------------------------------------
    def _new_page(self):
        if self.current:
            self.pages.append('\n'.join(self.current).encode('latin-1'))
        self.current = []
        self.cursor_y = self.PAGE_H - self.MARGIN_T

    def _ensure_space(self, needed: float):
        if self.cursor_y - needed < self.MARGIN_B:
            self._new_page()

    def _emit_text(self, x: float, y: float, text: str, font: str,
                   size: float):
        """Emit a single line of text at (x, y) using the given font."""
        cmd = (f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td "
               f"({escape_pdf_string(text)}) Tj ET")
        self.current.append(cmd)

    def _emit_line(self, x1: float, y1: float, x2: float, y2: float,
                   width: float = 0.5, gray: float = 0.6):
        self.current.append(
            f"q {gray:.2f} G {width} w {x1:.2f} {y1:.2f} m "
            f"{x2:.2f} {y2:.2f} l S Q"
        )

    # -- high-level content helpers ---------------------------------------
    def name_header(self, name: str):
        size = 22
        leading = size * 1.1
        self._ensure_space(leading)
        w = text_width(name, size, bold=True)
        x = (self.PAGE_W - w) / 2
        self.cursor_y -= size
        self._emit_text(x, self.cursor_y, name, 'F2', size)
        self.cursor_y -= 4

    def role_subheader(self, text: str):
        size = 10
        self._ensure_space(size * 1.4)
        usable = self.PAGE_W - self.MARGIN_L - self.MARGIN_R
        lines = wrap_text(text, usable, size, bold=False)
        for line in lines:
            w = text_width(line, size, bold=False)
            x = (self.PAGE_W - w) / 2
            self.cursor_y -= size
            self._emit_text(x, self.cursor_y, line, 'F1', size)
            self.cursor_y -= 2
        self.cursor_y -= 4

    def contact_line(self, text: str):
        size = 9.5
        self._ensure_space(size * 1.4)
        w = text_width(text, size, bold=False)
        x = (self.PAGE_W - w) / 2
        self.cursor_y -= size
        self._emit_text(x, self.cursor_y, text, 'F1', size)
        self.cursor_y -= 2

    def hr(self, gap_before: float = 6, gap_after: float = 6):
        self._ensure_space(gap_before + gap_after + 1)
        self.cursor_y -= gap_before
        self._emit_line(self.MARGIN_L, self.cursor_y,
                        self.PAGE_W - self.MARGIN_R, self.cursor_y,
                        width=0.7, gray=0.5)
        self.cursor_y -= gap_after

    def section_heading(self, text: str):
        size = 12
        self._ensure_space(size * 2 + 6)
        self.cursor_y -= size + 4
        self._emit_text(self.MARGIN_L, self.cursor_y, text, 'F2', size)
        # Underline below heading
        self.cursor_y -= 2
        self._emit_line(self.MARGIN_L, self.cursor_y,
                        self.PAGE_W - self.MARGIN_R, self.cursor_y,
                        width=0.4, gray=0.65)
        self.cursor_y -= 6

    def sub_heading(self, text: str):
        size = 11
        self._ensure_space(size * 1.5)
        self.cursor_y -= size + 2
        self._emit_text(self.MARGIN_L, self.cursor_y, text, 'F2', size)
        self.cursor_y -= 3

    def role_block(self, line1: str, line2: str = ''):
        """Job title + company info."""
        size = 10.5
        self._ensure_space(size * 3)
        self.cursor_y -= size
        self._emit_text(self.MARGIN_L, self.cursor_y, line1, 'F2', size)
        self.cursor_y -= 2
        if line2:
            self.cursor_y -= size
            self._emit_text(self.MARGIN_L, self.cursor_y, line2, 'F1', size)
            self.cursor_y -= 2
        self.cursor_y -= 3

    def paragraph(self, text: str, size: float = 10, indent: float = 0):
        self._ensure_space(size * 1.4)
        usable = self.PAGE_W - self.MARGIN_L - self.MARGIN_R - indent
        lines = wrap_text(text, usable, size)
        leading = size * 1.35
        for line in lines:
            self._ensure_space(leading)
            self.cursor_y -= size
            self._emit_text(self.MARGIN_L + indent, self.cursor_y,
                            line, 'F1', size)
            self.cursor_y -= leading - size
        self.cursor_y -= 2

    def bullet(self, text: str, size: float = 10):
        """A bulleted line that wraps with hanging indent."""
        bullet_char = '\u2022'  # not in our latin-1 table, use '-' instead
        bullet_char = '-'
        bullet_w = text_width(bullet_char + '  ', size)
        usable = (self.PAGE_W - self.MARGIN_L - self.MARGIN_R - bullet_w)
        lines = wrap_text(text, usable, size)
        leading = size * 1.35
        if not lines:
            return
        # First line with bullet
        self._ensure_space(leading)
        self.cursor_y -= size
        self._emit_text(self.MARGIN_L, self.cursor_y,
                        bullet_char + '  ' + lines[0], 'F1', size)
        self.cursor_y -= leading - size
        # Continuation lines indented to match
        for line in lines[1:]:
            self._ensure_space(leading)
            self.cursor_y -= size
            self._emit_text(self.MARGIN_L + bullet_w, self.cursor_y,
                            line, 'F1', size)
            self.cursor_y -= leading - size

    def label_value(self, label: str, value: str, label_w: float = 140,
                    size: float = 10):
        """Two-column row used for skills/personal-details lists."""
        leading = size * 1.4
        usable = (self.PAGE_W - self.MARGIN_L - self.MARGIN_R - label_w - 6)
        value_lines = wrap_text(value, usable, size)
        if not value_lines:
            value_lines = ['']
        height = leading * len(value_lines)
        self._ensure_space(height + 2)
        # Label on first line
        self.cursor_y -= size
        self._emit_text(self.MARGIN_L, self.cursor_y, label, 'F2', size)
        self._emit_text(self.MARGIN_L + label_w, self.cursor_y,
                        value_lines[0], 'F1', size)
        self.cursor_y -= leading - size
        for line in value_lines[1:]:
            self._ensure_space(leading)
            self.cursor_y -= size
            self._emit_text(self.MARGIN_L + label_w, self.cursor_y,
                            line, 'F1', size)
            self.cursor_y -= leading - size
        self.cursor_y -= 1

    def spacer(self, h: float = 6):
        self.cursor_y -= h

    # -- finalisation ------------------------------------------------------
    def output(self, path: Path):
        if self.current:
            self.pages.append('\n'.join(self.current).encode('latin-1'))

        objects = []  # list of bytes
        # Object 1: Catalog
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        # Object 2: Pages (kids fixed up below)
        page_count = len(self.pages)
        kids_refs = ' '.join(f"{3 + 2 * i} 0 R" for i in range(page_count))
        objects.append(
            f"<< /Type /Pages /Count {page_count} /Kids [{kids_refs}] >>"
            .encode('latin-1')
        )
        # Pages alternate Page object + Content stream object
        for i, content in enumerate(self.pages):
            page_obj_num = 3 + 2 * i
            content_obj_num = page_obj_num + 1
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {self.PAGE_W} {self.PAGE_H}] "
                f"/Resources << /Font << "
                f"/F1 {3 + 2 * page_count} 0 R "
                f"/F2 {3 + 2 * page_count + 1} 0 R "
                f">> >> "
                f"/Contents {content_obj_num} 0 R >>"
            ).encode('latin-1')
            objects.append(page_dict)

            compressed = zlib.compress(content)
            stream_dict = (
                f"<< /Length {len(compressed)} /Filter /FlateDecode >>\n"
                f"stream\n"
            ).encode('latin-1')
            objects.append(stream_dict + compressed + b"\nendstream")

        # Font objects
        objects.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>"
        )
        objects.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
            b"/Encoding /WinAnsiEncoding >>"
        )

        # Assemble PDF
        out = bytearray()
        out += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        offsets = [0]  # offset[0] is reserved
        for i, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode('latin-1')
            out += obj
            out += b"\nendobj\n"

        xref_offset = len(out)
        out += f"xref\n0 {len(objects) + 1}\n".encode('latin-1')
        out += b"0000000000 65535 f \n"
        for off in offsets[1:]:
            out += f"{off:010d} 00000 n \n".encode('latin-1')
        out += (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode('latin-1')

        path.write_bytes(bytes(out))


# ---------------------------------------------------------------------------
# Build the resume content
# ---------------------------------------------------------------------------
def build():
    pdf = PDF()

    # Header
    pdf.name_header("UPENDRA REDDIVARI")
    pdf.role_subheader(
        "Software Test Engineer  |  Manual & Automation Testing  |  "
        "Web (Selenium) + REST API & Microservices Testing"
    )
    pdf.contact_line("Bengaluru, Karnataka, India")
    pdf.contact_line("reddivariupendra.mits@gmail.com  |  +91 9390880035")
    pdf.hr(gap_before=8, gap_after=4)

    # Summary
    pdf.section_heading("PROFESSIONAL SUMMARY")
    pdf.paragraph(
        "Software Test Engineer with 3.2 years of experience specializing in "
        "Manual Testing, Automation Testing, Web Application Testing, REST "
        "API Testing and Microservices Validation. Skilled in Python, Shell "
        "scripting and Java, with hands-on experience in Karate, Bohem, "
        "TestNG and Selenium WebDriver automation frameworks for regression "
        "and build validation. Strong working knowledge of Atlassian Jira "
        "and Zephyr for test management, bug tracking and QA metrics. "
        "Proven ability to manage the complete test lifecycle - from "
        "requirement and design-document review, detailed test plan and "
        "test case creation, test estimation and prioritization, execution "
        "of Sanity, Smoke and Regression cycles within the sprint, defect "
        "tracking and release sign-off - following Agile Scrum methodology, "
        "with active participation in grooming, planning, retrospectives "
        "and stakeholder communication."
    )

    # Skills
    pdf.section_heading("TECHNICAL SKILLS")
    skills = [
        ("Operating Systems", "Linux (Primary), Windows"),
        ("Programming", "Python, Shell Scripting, Bash, Java"),
        ("Testing Types",
         "Web UI Testing, API Testing, REST API Testing, Functional, "
         "Regression, Smoke, Sanity, Integration, E2E, System, "
         "Microservices, Performance Testing (Basic), JSON Validation, "
         "API Response Validation, BDD, TDD, UAT, Exploratory Testing"),
        ("API Testing Tools",
         "Postman, REST Assured, Karate, API Automation, JSON Schema / "
         "Payload Validation"),
        ("Web UI Automation",
         "Selenium WebDriver, Python, Java, TestNG"),
        ("Frameworks",
         "Karate, Bohem, TestNG, Selenium WebDriver, Backend Automation "
         "Framework"),
        ("CI/CD & DevOps",
         "CI/CD Pipeline Integration (Jenkins / GitLab CI), Build "
         "Validation, Automated Test Execution in Pipelines"),
        ("Database Testing",
         "SQL (queries, joins, aggregates - HackerRank certified), "
         "Cassandra, OpenSearch, Elasticsearch"),
        ("Performance & Monitoring",
         "Apache JMeter (Basic), Prometheus"),
        ("Test Management",
         "Atlassian Jira, Zephyr, Confluence, Defect Density & Open "
         "Defect Tracking, Release Notes"),
        ("Debugging & Analysis",
         "Log Analysis, Root Cause Analysis, Issue Troubleshooting"),
        ("Tools",
         "Git, Jira, Zephyr, Confluence, JMeter, Selenium, Postman, "
         "WinSCP, Linux CLI"),
        ("Methodologies",
         "Agile Scrum, SDLC, STLC, Test Estimation & Planning, "
         "Cross-Functional Collaboration, Client / Stakeholder "
         "Communication, Build Validation, Release Testing"),
        ("Soft Skills",
         "Quick Learner, Willing to Learn New Technologies Rapidly, "
         "Analytical Thinking, Problem Solving"),
    ]
    for label, value in skills:
        pdf.label_value(label, value, label_w=140, size=9.5)

    # Experience
    pdf.section_heading("PROFESSIONAL EXPERIENCE")
    pdf.role_block(
        "Software Test Engineer  -  3.2 Years Total  |  Nov 2022 - Jan 2026",
        "Synchronoss Technologies India Pvt Ltd (1.8 Yrs)  ->  acquired by "
        "Lumine Group  ->  Lumine Software Solutions India Pvt Ltd "
        "(Openwave Messaging) (1.7 Yrs)"
    )

    pdf.sub_heading("Requirements Review & Test Planning")
    pdf.bullet(
        "Reviewed requirements, specifications and technical design "
        "documents and provided timely, meaningful feedback during "
        "grooming and refinement."
    )
    pdf.bullet(
        "Created detailed, comprehensive and well-structured test plans "
        "and test cases in Zephyr, mapped to user stories in Jira."
    )
    pdf.bullet(
        "Estimated, prioritized, planned and coordinated sprint-level "
        "testing activities, including Sanity, Smoke and Regression "
        "scope, within the sprint timeline."
    )

    pdf.sub_heading("Testing (Manual, Web UI, API & Microservices)")
    pdf.bullet(
        "Designed and maintained test cases and scenarios based on "
        "functional requirements."
    )
    pdf.bullet(
        "Executed Functional, Sanity, Smoke, Regression, Integration, "
        "System, E2E and UI test cycles with systematic result "
        "documentation."
    )
    pdf.bullet(
        "Performed Web UI testing on EmailMX web modules (mailbox access, "
        "message views), validating user-facing flows end-to-end."
    )
    pdf.bullet(
        "Performed REST API Testing including JSON payload verification "
        "using Postman and REST Assured to ensure correctness and data "
        "integrity of backend service outputs."
    )
    pdf.bullet(
        "Validated microservices workflows by verifying individual "
        "service responses and end-to-end data flow across components."
    )
    pdf.bullet(
        "Conducted database validation on Cassandra and OpenSearch - "
        "queried and verified data storage, retrieval and search "
        "accuracy. Comfortable writing SQL queries (joins, aggregates, "
        "sub-queries) for relational data validation."
    )
    pdf.bullet(
        "Performed exploratory testing to identify edge cases and "
        "uncover hidden defects beyond scripted coverage."
    )

    pdf.sub_heading("Automation & Performance Testing")
    pdf.bullet(
        "Designed, developed and executed automation scripts using "
        "open-source tools - Karate, Bohem, TestNG, Selenium WebDriver, "
        "Python and Shell scripting - for regression and build validation."
    )
    pdf.bullet(
        "Upheld and enhanced automation frameworks to support sprint-level "
        "and release-level regression test execution."
    )
    pdf.bullet(
        "Integrated automated test execution into CI/CD pipelines "
        "(Jenkins / GitLab CI) for continuous build validation."
    )
    pdf.bullet(
        "Raised pull requests (PRs) for automation script changes, "
        "reviewed code and merged to the main branch following team "
        "standards."
    )
    pdf.bullet(
        "Performed basic performance testing using JMeter to evaluate "
        "system behavior under load."
    )

    pdf.sub_heading("Defect Management, QA Metrics & Release")
    pdf.bullet(
        "Identified, recorded, documented and tracked defects thoroughly "
        "in Jira / Zephyr with clear reproduction steps, logs and "
        "severity classification."
    )
    pdf.bullet(
        "Tracked QA metrics - defect density, open defect counts and "
        "regression pass-rate trends - across releases."
    )
    pdf.bullet(
        "Managed end-to-end build validation - from build installation "
        "and test execution through defect tracking and release sign-off."
    )
    pdf.bullet(
        "Analyzed application and system logs in Linux environments for "
        "root cause identification and developer triage support."
    )
    pdf.bullet(
        "Updated test plans, test execution status and release notes in "
        "Jira, Zephyr and Confluence."
    )

    pdf.sub_heading("Collaboration & Agile Scrum")
    pdf.bullet(
        "Collaborated with cross-functional development teams and "
        "client / stakeholders for defect triage, reproduction and "
        "fix verification."
    )
    pdf.bullet(
        "Independently communicated with development and stakeholders "
        "during grooming, sprint planning, daily stand-ups, "
        "retrospectives and status meetings, sharing test status, "
        "blockers and risks."
    )

    # Key project
    pdf.section_heading("KEY PROJECT - EMAILMX (OPENWAVE MESSAGING)")
    pdf.paragraph(
        "EmailMX is a large-scale enterprise email and messaging platform "
        "built using a distributed microservices architecture. It supports "
        "key functionalities such as mail delivery, mailbox access, "
        "message storage and queue processing through multiple "
        "interconnected services. The platform is designed to handle high "
        "volumes of data with a strong focus on availability, scalability "
        "and reliability, ensuring seamless communication and efficient "
        "processing across systems."
    )
    pdf.sub_heading("Key Contributions")
    pdf.bullet(
        "Delivered consistent testing support across multiple release "
        "cycles, ensuring platform stability and quality."
    )
    pdf.bullet(
        "Improved regression efficiency through automation scripts and "
        "reusable test components, reducing manual effort."
    )
    pdf.bullet(
        "Ensured high-quality releases by performing thorough Web UI, "
        "API and database validation, defect tracking and sign-off "
        "across sprints."
    )
    pdf.bullet(
        "Actively contributed to Agile processes including sprint "
        "planning, retrospectives and cross-team collaboration."
    )

    # Education
    pdf.section_heading("EDUCATION")
    pdf.paragraph(
        "Bachelor of Technology (B.Tech)  -  Madanapalle Institute of "
        "Technology and Science"
    )

    # Certifications
    pdf.section_heading("CERTIFICATIONS")
    pdf.bullet("Python  -  HackerRank")
    pdf.bullet("SQL  -  HackerRank")
    pdf.bullet("REST API  -  HackerRank")
    pdf.bullet("Java  -  HackerRank")
    pdf.bullet("Problem Solving  -  HackerRank")

    # Personal details
    pdf.section_heading("PERSONAL DETAILS")
    pdf.label_value("Date of Birth", "12 February 1999",
                    label_w=120, size=10)
    pdf.label_value("Nationality", "Indian", label_w=120, size=10)
    pdf.label_value("Languages", "English, Telugu", label_w=120, size=10)
    pdf.label_value("Location", "Bengaluru, Karnataka",
                    label_w=120, size=10)

    out_path = Path(__file__).parent / "Upendra_Reddivari_QA_Resume.pdf"
    pdf.output(out_path)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
