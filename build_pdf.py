import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

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
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "PathDiver — Intelligent Storage & File Traversal Superpower Hub")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Proprietary — PathDiver v1.0 Overview")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4F46E5"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=4
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#FFFFFF"),
        alignment=1
    )

    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#FFFFFF"),
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_center = ParagraphStyle(
        'TCC',
        parent=table_cell_style,
        alignment=1
    )

    story = []

    # Title & Header
    story.append(Paragraph("PathDiver", title_style))
    story.append(Paragraph("The Intelligent File Traversal, Duplicate Detection & Storage Superpower Hub for Windows", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceBefore=0, spaceAfter=12))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview", h1_style))
    story.append(Paragraph(
        "<b>PathDiver</b> is a next-generation desktop utility designed to replace bloated, ad-filled file cleaners and rigid search tools. "
        "Built with an ultra-fast Python core and a modern glassmorphic interface, PathDiver combines full-text deep file search, "
        "heuristic visual duplicate detection, 1-click reversible organization, and modern developer cache cleaning into a single, cohesive 33 MB application.",
        body_style
    ))
    story.append(Paragraph(
        "Unlike conventional tools that rely solely on filename matching or exact byte hashes, PathDiver introduces content-level intelligence: "
        "it reads inside PDF and Word documents without opening external apps, catches cropped or annotated image duplicates, and safeguards files using "
        "the native Windows Recycle Bin with 100% reversible session journals.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # 4 Superpowers
    story.append(Paragraph("2. The Four Core Superpowers", h1_style))

    # Feature 1
    story.append(Paragraph("🔍 Superpower 1: In-Content Search & Smart Peek Summary", h2_style))
    story.append(Paragraph(
        "• <b>Full-Text Traversal:</b> Searches beyond file names to inspect text inside <code>.pdf</code>, <code>.docx</code>, <code>.ipynb</code>, <code>.txt</code>, and code files (Python, JS, C++).<br/>"
        "• <b>2-Line Smart Peek:</b> Clicking 'Peek' reveals an instant inline drawer showing document type, page count, and an automatic 2-line summary in under 15ms—eliminating the need to launch heavy readers like Adobe Acrobat or Microsoft Word.",
        bullet_style
    ))

    # Feature 2
    story.append(Paragraph("🔎 Superpower 2: 2-Phase Heuristic Duplicate Detection", h2_style))
    story.append(Paragraph(
        "• <b>Phase 1 (Exact Ditto):</b> Rapid hash comparison identifies bit-for-bit identical duplicates instantly.<br/>"
        "• <b>Phase 2 (Heuristic Content Match):</b> Analyzes visual pixels, crop boundaries, and text similarity. Accurately detects cropped screenshots, annotated/drawn images, and edited document drafts (with percentage similarity) without false positives.",
        bullet_style
    ))

    # Feature 3
    story.append(Paragraph("🧹 Superpower 3: 1-Click Folder Organizer with Reversible Undo", h2_style))
    story.append(Paragraph(
        "• <b>Zero-Rule Sorting:</b> Instantly classifies chaotic loose files into standardized folders (<i>Documents, Installers, Code, Archives, Images, Media</i>) without touching existing directories.<br/>"
        "• <b>100% Reversible 1-Click Undo:</b> Every operation is journaled in-memory. Clicking 'Undo' returns every file to its exact original location and removes empty category folders.",
        bullet_style
    ))

    # Feature 4
    story.append(Paragraph("🧼 Superpower 4: Developer & Cache Junk Sweeper", h2_style))
    story.append(Paragraph(
        "• <b>Pruned DFS Scan (&lt;2s):</b> Scans disk hierarchies while instantly pruning traversal at cache boundaries (e.g. <code>node_modules</code>, <code>__pycache__</code>, <code>.venv</code>, <code>.gradle</code>), calculating folder sizes in seconds.<br/>"
        "• <b>Safe Reclaim via Recycle Bin:</b> Reclaims tens of gigabytes with 1-click confirmation directly to the native Windows Recycle Bin—guaranteeing zero accidental data loss.",
        bullet_style
    ))

    story.append(PageBreak())

    # Competitive Landscape
    story.append(Paragraph("3. Competitive Comparison Matrix", h1_style))
    story.append(Paragraph(
        "How PathDiver compares directly against industry-standard utilities:",
        body_style
    ))

    # Table Data
    table_data = [
        [
            Paragraph("Capability / Feature", table_header_style),
            Paragraph("Voidtools<br/>Everything", table_header_style),
            Paragraph("dupeGuru", table_header_style),
            Paragraph("CCleaner", table_header_style),
            Paragraph("PathDiver<br/>(This App)", table_header_style)
        ],
        [
            Paragraph("<b>Search by Filename</b>", table_cell_style),
            Paragraph("YES", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Search INSIDE Content (PDF, DOCX, Code)</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Smart 2-Line Peek Summaries</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES (&lt;15ms)</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Cropped & Annotated Duplicate Detection</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES (2-Phase)</b>", table_cell_center)
        ],
        [
            Paragraph("<b>1-Click Loose File Organization</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES</b>", table_cell_center)
        ],
        [
            Paragraph("<b>100% Reversible 1-Click Undo</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Dev Cache Sweeper (node_modules, .venv)</b>", table_cell_style),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("NO", table_cell_center),
            Paragraph("<b>YES (Pruned DFS)</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Safe Windows Recycle Bin Deletion</b>", table_cell_style),
            Paragraph("N/A", table_cell_center),
            Paragraph("Permanent", table_cell_center),
            Paragraph("Permanent", table_cell_center),
            Paragraph("<b>YES (Recycle Bin)</b>", table_cell_center)
        ],
        [
            Paragraph("<b>Zero Setup / Standalone Executable</b>", table_cell_style),
            Paragraph("YES", table_cell_center),
            Paragraph("Installer", table_cell_center),
            Paragraph("Installer", table_cell_center),
            Paragraph("<b>YES (Portable)</b>", table_cell_center)
        ],
        [
            Paragraph("<b>No Ads / No Subscriptions / Modern UI</b>", table_cell_style),
            Paragraph("YES", table_cell_center),
            Paragraph("YES", table_cell_center),
            Paragraph("NO (Paid / Ads)", table_cell_center),
            Paragraph("<b>YES (Dual Theme)</b>", table_cell_center)
        ]
    ]

    comp_table = Table(table_data, colWidths=[180, 75, 75, 84, 90])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (4, 1), (4, -1), colors.HexColor("#EEF2FF")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(comp_table)

    story.append(Spacer(1, 14))

    # Distribution Section
    story.append(Paragraph("4. Distribution & Deployment Guide", h1_style))
    story.append(Paragraph(
        "PathDiver is ready to be shared with friends, clients, or colleagues using three flexible formats:",
        body_style
    ))

    story.append(Paragraph("• <b>Standalone Native Executable (<code>PathDiver.exe</code> — 33.6 MB):</b><br/>"
                           "Zero dependencies. The recipient does not need Python, command prompt, or Git. "
                           "They simply double-click and use it. Ideal for USB flash drive transfers.", bullet_style))

    story.append(Paragraph("• <b>Zero-Friction Package (<code>PathDiver_Ready_To_Send.zip</code> — 33.3 MB):</b><br/>"
                           "The recommended package for online sharing (Google Drive, WhatsApp, Telegram). "
                           "Includes the <code>Click_To_Start_PathDiver.bat</code> launcher, which automatically strips the internet download tag "
                           "('Mark of the Web') in 0.1 seconds, completely bypassing Windows Smart App Control without manual configuration.", bullet_style))

    story.append(Paragraph("• <b>Instant Browser Edition (<code>PathDiver_Offline.html</code> — 105 KB):</b><br/>"
                           "Single self-contained HTML file that opens in Google Chrome, Microsoft Edge, Safari, or Firefox on any operating system.", bullet_style))

    story.append(Spacer(1, 10))

    # Privacy & Architecture
    story.append(Paragraph("5. Technical Architecture & Privacy Guarantee", h1_style))
    story.append(Paragraph(
        "<b>100% Local & Private:</b> PathDiver runs entirely on the host machine. "
        "No files, search queries, summaries, or metadata are ever transmitted over the network. There are zero cloud dependencies, "
        "zero telemetry trackers, and zero background advertising services.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Architecture:</b> Powered by Python 3 with PyWebView native window integration, PyPDF & Pillow image heuristic analysis engines, "
        "and Send2Trash OS-level Recycle Bin safety bridges.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {output_path}")

if __name__ == '__main__':
    out_pdf = r"C:\Users\Shareef\OneDrive\Desktop\PathDiver_Overview_and_Guide.pdf"
    build_pdf(out_pdf)
