"""Generate the executive-summary PDF from live dashboard data.

Returns PDF bytes (in-memory) so it works identically locally and on
Streamlit Cloud — no filesystem writes required.
"""
from io import BytesIO
from datetime import date

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)

BRAND = colors.HexColor("#1565C0")


def _brl(x: float) -> str:
    return f"R$ {x:,.0f}"


def build_executive_pdf(seg_summary: pd.DataFrame,
                        n_customers: int,
                        repeat_share: float,
                        total_value: float) -> bytes:
    """seg_summary needs columns: segment, n_customers, avg_value."""
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=20 * mm, bottomMargin=18 * mm,
                            leftMargin=18 * mm, rightMargin=18 * mm)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=BRAND,
                        fontSize=20, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9,
                         textColor=colors.grey, spaceAfter=14)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=BRAND,
                        fontSize=13, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10,
                          leading=15, spaceAfter=6)

    story = []

    # ---- Header ----
    story.append(Paragraph("Olist Customer Intelligence — Executive Summary", h1))
    story.append(Paragraph(f"Generated {date.today():%B %d, %Y} · "
                           f"Brazilian e-commerce marketplace, Sep 2016 – Aug 2018",
                           sub))

    # ---- Headline metrics table ----
    metrics = [
        ["Customers analyzed", f"{n_customers:,}"],
        ["Repeat-buyer share", f"{repeat_share:.1%}"],
        ["Total customer value", _brl(total_value)],
    ]
    t = Table(metrics, colWidths=[70 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.lightgrey),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # ---- Findings ----
    story.append(Paragraph("Three findings", h2))
    findings = [
        ("1. Retention is the core problem, not churn",
         "Cohort retention collapses to near-zero after the first month across "
         "every acquisition cohort. The strategic question is conversion of "
         "one-time buyers, not retention of an active base."),
        ("2. Future loyalty cannot be predicted at acquisition",
         "A first-order classifier predicts spend level well (ROC-AUC 0.97) but "
         "predicts repeat behavior essentially not at all (repeat-buyer recall "
         "~1%). Loyal customers cannot be identified from their first order."),
        ("3. Delivery speed causally improves satisfaction",
         "Propensity score matching (controlling for order value, freight, "
         "category, region, and promised delivery time) shows faster-than-"
         "promised delivery raises review scores. Magnitude is an upper bound; "
         "direction is robust. Satisfaction is a lever the business controls."),
    ]
    for title, text in findings:
        story.append(Paragraph(f"<b>{title}</b>", body))
        story.append(Paragraph(text, body))

    # ---- Segment table ----
    story.append(Paragraph("Customer segments", h2))
    data = [["Segment", "Customers", "Avg value", "Recommendation"]]
    recs = {
        "Repeat Buyers": "Protect — highest ROI per BRL",
        "High-Value One-Timers": "Convert — largest value pool",
        "Low-Value Recent": "Nurture selectively",
        "Dormant Low-Value": "Do not spend — negative ROI",
    }
    for _, r in seg_summary.iterrows():
        data.append([r["segment"], f"{int(r['n_customers']):,}",
                     _brl(r["avg_value"]),
                     recs.get(r["segment"], "")])
    seg_table = Table(data, colWidths=[42 * mm, 25 * mm, 28 * mm, 75 * mm])
    seg_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F5F7FA")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(seg_table)
    story.append(Spacer(1, 10))

    # ---- Recommendation ----
    story.append(Paragraph("Recommendation", h2))
    story.append(Paragraph(
        "Because loyalty cannot be predicted but satisfaction can be influenced, "
        "allocate retention spend by segment ROI and invest in delivery — the "
        "operational lever proven to move customer experience. Fund repeat "
        "buyers and high-value one-timers; do not spend on negative-ROI segments.",
        body))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Method: K-Means segmentation on RFM · random-forest prediction on "
        "first-order features · causal estimate via propensity score matching. "
        "See repository notebooks and docs/limitations.md for full caveats.",
        sub))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()