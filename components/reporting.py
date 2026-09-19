from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_report_pdf(domain: str, values: dict[str, Any], result: dict[str, Any], lime_values: list[dict[str, Any]]) -> bytes:
    """Create a polished PDF summary of the current decision scenario."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )
    metric_style = ParagraphStyle(
        "MetricText",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
    )

    risk_level = result.get("level", "Unknown")
    probability = result.get("probability", 0.0)
    confidence = result.get("confidence", 0.0)
    summary_text = result.get("plain_language", "No summary available.")

    metric_rows = [
        [Paragraph("Risk level", metric_style), Paragraph(str(risk_level), body_style)],
        [Paragraph("Risk probability", metric_style), Paragraph(f"{probability:.0%}", body_style)],
        [Paragraph("Model confidence", metric_style), Paragraph(f"{confidence:.0%}", body_style)],
    ]
    metric_table = Table(metric_rows, colWidths=[170, 320])
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbeafe")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    input_rows = [[Paragraph("Feature", metric_style), Paragraph("Value", metric_style)]]
    input_rows.extend([[Paragraph(str(key), body_style), Paragraph(str(value), body_style)] for key, value in values.items()])
    input_table = Table(input_rows, colWidths=[170, 320])
    input_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    factor_rows = [[Paragraph("Factor", metric_style), Paragraph("Impact", metric_style)]]
    for item in result.get("factors", [])[:6]:
        factor_rows.append(
            [
                Paragraph(str(item.get("label", item.get("feature", "Factor"))), body_style),
                Paragraph(f"{item.get('impact', 0):+.2f}", body_style),
            ]
        )
    if len(factor_rows) == 1:
        factor_rows.append([Paragraph("No factors available", body_style), Paragraph("-", body_style)])
    factor_table = Table(factor_rows, colWidths=[260, 230])
    factor_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    lime_rows = [[Paragraph("Feature", metric_style), Paragraph("Impact", metric_style)]]
    for item in lime_values[:4]:
        lime_rows.append(
            [
                Paragraph(str(item.get("feature", "Feature")), body_style),
                Paragraph(f"{item.get('impact', 0):+.2f}", body_style),
            ]
        )
    if len(lime_rows) == 1:
        lime_rows.append([Paragraph("No local explanation available", body_style), Paragraph("-", body_style)])
    lime_table = Table(lime_rows, colWidths=[260, 230])
    lime_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbf7d0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story = [
        Paragraph(f"{domain} Decision Report", title_style),
        Spacer(1, 8),
        Paragraph("Scenario summary", section_style),
        metric_table,
        Spacer(1, 10),
        Paragraph("Interpretation", section_style),
        Paragraph(summary_text, body_style),
        Spacer(1, 10),
        Paragraph("Scenario inputs", section_style),
        input_table,
        Spacer(1, 10),
        Paragraph("Top contributing factors", section_style),
        factor_table,
        Spacer(1, 10),
        Paragraph("LIME comparison", section_style),
        lime_table,
    ]

    doc.build(story)
    return buffer.getvalue()
