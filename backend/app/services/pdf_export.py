from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_report_pdf(report: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Resume Career Advisor Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Target role: {report['selected_role']}", styles["Heading2"]))
    story.append(Paragraph(f"Coverage: {report['gap_analysis']['coverage_percent']}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    gap = report["gap_analysis"]
    table = Table(
        [
            ["Matched Skills", ", ".join(gap["matched_skills"]) or "None"],
            ["Missing Skills", ", ".join(gap["missing_skills"]) or "None"],
        ],
        colWidths=[120, 360],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4ff")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d5dd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    for index, item in enumerate(report["recommendations"], start=1):
        story.append(Paragraph(f"{index}. {item['title']} ({item['priority']})", styles["Heading3"]))
        story.append(Paragraph(item["detail"], styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Extracted Skills", styles["Heading2"]))
    skills = [[item["skill"], item["source"], f"{round(item['score'] * 100)}%"] for item in report["extracted_skills"]]
    if skills:
        skill_table = Table([["Skill", "Source", "Score"], *skills], colWidths=[240, 140, 80])
        skill_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123c69")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d5dd")),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.append(skill_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
