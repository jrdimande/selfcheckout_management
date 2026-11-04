from datetime import date
from io import BytesIO

from django.http import HttpResponse


def to_xlsx(report, kind):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = report["title"][:31]
    ws.append(report["headers"])
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in report["rows"]:
        ws.append([float(x) if isinstance(x, str) and _is_num(x) else x for x in r])
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(40, max(len(str(c.value or "")) for c in col) + 3)
    buf = BytesIO()
    wb.save(buf)
    resp = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{kind}_{date.today()}.xlsx"'
    return resp


def to_pdf(report, kind):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), title=report["title"])
    styles = getSampleStyleSheet()
    data = [report["headers"]] + [[str(c) for c in r] for r in report["rows"]]
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")])]))
    doc.build([Paragraph(report["title"], styles["Title"]), Paragraph(f"Gerado em {date.today():%d/%m/%Y}", styles["Normal"]),
               Spacer(1, 12), t])
    resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{kind}_{date.today()}.pdf"'
    return resp


def _is_num(s):
    try:
        float(s)
        return not s.strip().isdigit() or len(s) < 10
    except ValueError:
        return False
