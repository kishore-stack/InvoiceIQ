"""
Five distinct invoice layout templates using ReportLab canvas.
Each template function draws one invoice onto a canvas starting at y_start
and returns the y position after drawing (so multi-invoice stacking works).
"""
import random
from typing import Dict, Any, List, Optional
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

PAGE_W, PAGE_H = A4  # 595.27, 841.89 pts

# ── helpers ──────────────────────────────────────────────────────────────────

def _fmt(amount: float, symbol: str) -> str:
    return f"{symbol}{amount:,.2f}"


def _wrap_text(c: rl_canvas.Canvas, text: str, x: float, y: float,
               max_width: float, font: str, size: float, line_height: float) -> float:
    """Draw wrapped text, return new y after last line."""
    c.setFont(font, size)
    words = text.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= line_height
            line = word
    if line:
        c.drawString(x, y, line)
        y -= line_height
    return y


def _draw_table_row(c: rl_canvas.Canvas, row: List[str], col_x: List[float],
                    col_w: List[float], y: float, row_h: float,
                    font: str, size: float, bg: Optional[colors.Color] = None,
                    borders: bool = True, align: Optional[List[str]] = None) -> float:
    if bg:
        c.setFillColor(bg)
        c.rect(col_x[0], y - row_h + 4, sum(col_w), row_h, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(font, size)
    for i, (text, cx, cw) in enumerate(zip(row, col_x, col_w)):
        a = (align[i] if align else "L")
        if a == "R":
            c.drawRightString(cx + cw - 2, y, str(text))
        else:
            c.drawString(cx + 2, y, str(text))
    if borders:
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.setLineWidth(0.4)
        c.line(col_x[0], y - row_h + 4, col_x[0] + sum(col_w), y - row_h + 4)
    return y - row_h


def _draw_totals_block(c: rl_canvas.Canvas, inv: Dict[str, Any],
                       x: float, y: float, w: float) -> float:
    sym = inv["currency_symbol"]
    rows: List = [("Subtotal", _fmt(inv["subtotal"], sym))]

    # If tax_breakdown is populated, render one row per component
    # (CGST/SGST/Cess/IGST). Otherwise render the single Tax line.
    breakdown = inv.get("tax_breakdown") or []
    if breakdown:
        for component in breakdown:
            label = f"{component['label']} ({component['rate']*100:.1f}%)"
            rows.append((label, _fmt(component["amount"], sym)))
    else:
        rows.append((f"Tax ({inv['tax_rate']*100:.1f}%)", _fmt(inv["tax_amount"], sym)))

    rows.append(
        (f"Discount ({inv['discount_rate']*100:.1f}%)", f"-{_fmt(inv['discount_amount'], sym)}")
    )

    for label, val in rows:
        c.setFont("Helvetica", 9)
        c.drawString(x, y, label)
        c.drawRightString(x + w, y, val)
        y -= 14
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.line(x, y + 2, x + w, y + 2)
    y -= 4
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Total")
    c.drawRightString(x + w, y, _fmt(inv["total_amount"], sym))
    return y - 20


# ── Template A: Professional Classic (dark header, full-border table) ─────────

def draw_template_a(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    BLUE = HexColor("#1A3C5E")
    LIGHT = HexColor("#EAF0F6")
    sym = inv["currency_symbol"]
    y = y_start

    # Header bar
    c.setFillColor(BLUE)
    c.rect(0, y - 60, PAGE_W, 60, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(15*mm, y - 38, inv["seller"]["name"])
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, y - 50, inv["seller"]["address"])
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(PAGE_W - 15*mm, y - 35, "INVOICE")
    y -= 65

    # Invoice meta
    c.setFillColor(LIGHT)
    c.rect(PAGE_W/2, y - 50, PAGE_W/2, 50, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    meta = [
        ("Invoice No:", inv["invoice_number"] or "N/A"),
        ("Issue Date:", inv["issue_date"]),
        ("Due Date:", inv["due_date"]),
        ("Currency:", inv["currency"]),
    ]
    mx, my = PAGE_W/2 + 10, y - 14
    for label, val in meta:
        c.drawString(mx, my, label)
        c.setFont("Helvetica", 9)
        c.drawString(mx + 55, my, str(val))
        c.setFont("Helvetica-Bold", 9)
        my -= 11
    y -= 55

    # Bill To / From
    c.setFont("Helvetica-Bold", 9)
    c.drawString(15*mm, y, "FROM")
    c.drawString(PAGE_W/2, y, "BILL TO")
    y -= 5
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    c.line(15*mm, y, 80*mm, y)
    c.line(PAGE_W/2, y, PAGE_W - 15*mm, y)
    y -= 14
    c.setFont("Helvetica", 9)
    for line in [inv["seller"]["address"], inv["seller"]["city"], inv["seller"]["email"]]:
        c.drawString(15*mm, y, line)
        y_b = y
        c.drawString(PAGE_W/2, y_b, line.replace(inv["seller"]["address"],
                     inv["buyer"]["address"]).replace(inv["seller"]["city"],
                     inv["buyer"]["city"]).replace(inv["seller"]["email"], inv["buyer"]["email"]))
        y -= 11
    y -= 10

    # Table header
    col_x = [15*mm, 90*mm, 120*mm, 148*mm, 172*mm, 193*mm]
    col_w = [75*mm, 30*mm, 28*mm, 24*mm, 21*mm, 32*mm]
    headers = ["Description", "Qty", "Unit Price", "Tax", "Discount", "Total"]
    align = ["L", "R", "R", "R", "R", "R"]
    y = _draw_table_row(c, headers, col_x, col_w, y, 18, "Helvetica-Bold", 8,
                        bg=BLUE and colors.white.__class__(0.1, 0.24, 0.37), borders=True, align=align)
    c.setFillColor(colors.black)

    # Table rows
    for idx, item in enumerate(inv["line_items"]):
        bg = LIGHT if idx % 2 == 0 else None
        row = [
            item["description"][:45],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(item["tax_amount"], sym),
            _fmt(item["discount_amount"], sym),
            _fmt(item["line_total"], sym),
        ]
        y = _draw_table_row(c, row, col_x, col_w, y, 14, "Helvetica", 8, bg=bg, align=align)
        if y < 80:
            c.showPage()
            y = PAGE_H - 20

    y -= 10
    _draw_totals_block(c, inv, PAGE_W - 85*mm, y, 70*mm)
    y -= 55

    if inv.get("notes"):
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(15*mm, y, f"Notes: {inv['notes']}")
        y -= 12

    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#888888"))
    c.drawString(15*mm, y, f"Payment Terms: Net {inv['payment_terms_days']} days")
    return y - 20


# ── Template B: Minimal Borderless ───────────────────────────────────────────

def draw_template_b(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    sym = inv["currency_symbol"]
    y = y_start

    c.setFont("Helvetica-Bold", 14)
    c.drawString(15*mm, y, inv["seller"]["name"])
    c.setFont("Helvetica", 8)
    c.drawString(15*mm, y - 12, inv["seller"]["address"])
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(PAGE_W - 15*mm, y, "INVOICE")
    y -= 28

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 14

    # Invoice meta right-aligned
    meta = [
        f"Invoice #: {inv['invoice_number'] or 'N/A'}",
        f"Date: {inv['issue_date']}",
        f"Due: {inv['due_date']}",
    ]
    c.setFont("Helvetica", 9)
    for m in meta:
        c.drawRightString(PAGE_W - 15*mm, y, m)
        y -= 11

    # Bill To
    c.setFont("Helvetica-Bold", 9)
    c.drawString(15*mm, y + 33, "Bill To:")
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, y + 22, inv["buyer"]["name"])
    c.drawString(15*mm, y + 11, inv["buyer"]["address"])
    y -= 10

    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 14

    # Borderless table - whitespace aligned
    col_x = [15*mm, 100*mm, 128*mm, 158*mm, 180*mm]
    col_w = [85*mm, 28*mm, 30*mm, 22*mm, 30*mm]
    headers = ["Item Description", "Qty", "Unit Price", "Tax", "Line Total"]
    align = ["L", "R", "R", "R", "R"]

    c.setFont("Helvetica-Bold", 9)
    for h, cx, cw, a in zip(headers, col_x, col_w, align):
        if a == "R":
            c.drawRightString(cx + cw, y, h)
        else:
            c.drawString(cx, y, h)
    y -= 4
    c.setLineWidth(0.5)
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 12

    c.setFont("Helvetica", 8)
    for item in inv["line_items"]:
        row = [
            item["description"][:50],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(item["tax_amount"], sym),
            _fmt(item["line_total"], sym),
        ]
        for text, cx, cw, a in zip(row, col_x, col_w, align):
            if a == "R":
                c.drawRightString(cx + cw, y, str(text))
            else:
                c.drawString(cx, y, str(text))
        y -= 11
        if y < 80:
            c.showPage()
            y = PAGE_H - 20

    y -= 6
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 8
    _draw_totals_block(c, inv, PAGE_W - 80*mm, y, 65*mm)
    y -= 50

    c.setFont("Helvetica", 8)
    c.drawString(15*mm, y, f"Payment Terms: Net {inv['payment_terms_days']} days  |  Currency: {inv['currency']}")
    return y - 20


# ── Template C: Modern Two-Column ────────────────────────────────────────────

def draw_template_c(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    TEAL = HexColor("#00897B")
    LTEAL = HexColor("#E0F2F1")
    sym = inv["currency_symbol"]
    y = y_start

    # Accent left bar
    c.setFillColor(TEAL)
    c.rect(0, y - PAGE_H, 8*mm, PAGE_H, fill=1, stroke=0)

    # Header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, y, inv["seller"]["name"])
    c.setFont("Helvetica", 8)
    c.drawString(15*mm, y - 12, f"{inv['seller']['address']} | {inv['seller']['email']}")
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(TEAL)
    c.drawRightString(PAGE_W - 15*mm, y, "INVOICE")
    c.setFillColor(colors.black)
    y -= 30

    # Two-column info strip
    c.setFillColor(LTEAL)
    c.rect(12*mm, y - 40, PAGE_W - 24*mm, 40, fill=1, stroke=0)
    c.setFillColor(colors.black)
    left_info = [
        ("Invoice #", inv["invoice_number"] or "N/A"),
        ("Date", inv["issue_date"]),
    ]
    right_info = [
        ("Bill To", inv["buyer"]["name"]),
        ("Due Date", inv["due_date"]),
    ]
    lx, rx, iy = 15*mm, PAGE_W/2 + 5*mm, y - 14
    for (ll, lv), (rl, rv) in zip(left_info, right_info):
        c.setFont("Helvetica-Bold", 8)
        c.drawString(lx, iy, f"{ll}:"); c.setFont("Helvetica", 8); c.drawString(lx + 28, iy, str(lv))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(rx, iy, f"{rl}:"); c.setFont("Helvetica", 8); c.drawString(rx + 30, iy, str(rv))
        iy -= 12
    y -= 48

    # Table with header-only border
    col_x = [15*mm, 95*mm, 123*mm, 150*mm, 172*mm, 193*mm]
    col_w = [80*mm, 28*mm, 27*mm, 22*mm, 21*mm, 27*mm]
    headers = ["Description", "Qty", "Unit Price", "Tax", "Disc", "Total"]
    align = ["L", "R", "R", "R", "R", "R"]

    c.setFillColor(TEAL)
    c.rect(col_x[0], y - 16, sum(col_w), 18, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    hy = y - 4
    for h, cx, cw, a in zip(headers, col_x, col_w, align):
        if a == "R": c.drawRightString(cx + cw - 2, hy, h)
        else: c.drawString(cx + 2, hy, h)
    y -= 20

    c.setFillColor(colors.black)
    for idx, item in enumerate(inv["line_items"]):
        if idx % 2 == 0:
            c.setFillColor(LTEAL)
            c.rect(col_x[0], y - 10, sum(col_w), 14, fill=1, stroke=0)
            c.setFillColor(colors.black)
        row = [
            item["description"][:48],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(item["tax_amount"], sym),
            _fmt(item["discount_amount"], sym),
            _fmt(item["line_total"], sym),
        ]
        c.setFont("Helvetica", 8)
        for text, cx, cw, a in zip(row, col_x, col_w, align):
            if a == "R": c.drawRightString(cx + cw - 2, y, str(text))
            else: c.drawString(cx + 2, y, str(text))
        y -= 14
        if y < 80:
            c.showPage()
            y = PAGE_H - 20

    y -= 8
    _draw_totals_block(c, inv, PAGE_W - 80*mm, y, 65*mm)
    y -= 55
    c.setFont("Helvetica", 8)
    c.drawString(15*mm, y, f"Net {inv['payment_terms_days']} Days  ·  {inv['currency']}")
    return y - 20


# ── Template D: Dense Compact (many items, small font) ───────────────────────

def draw_template_d(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    GRAY = HexColor("#444444")
    sym = inv["currency_symbol"]
    y = y_start

    c.setFont("Helvetica-Bold", 12)
    c.drawString(15*mm, y, "INVOICE")
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - 15*mm, y, f"#{inv['invoice_number'] or 'N/A'}  |  {inv['issue_date']}")
    y -= 10
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.5)
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 10

    # Compact seller/buyer
    c.setFont("Helvetica-Bold", 8)
    c.drawString(15*mm, y, "From:"); c.drawString(PAGE_W/2, y, "To:")
    c.setFont("Helvetica", 8)
    y -= 10
    c.drawString(15*mm, y, inv["seller"]["name"])
    c.drawString(PAGE_W/2, y, inv["buyer"]["name"])
    y -= 10
    c.drawString(15*mm, y, inv["seller"]["address"][:40])
    c.drawString(PAGE_W/2, y, inv["buyer"]["address"][:40])
    y -= 16

    # Table - small, dense, full borders
    col_x = [15*mm, 90*mm, 115*mm, 140*mm, 162*mm, 184*mm, 200*mm]
    col_w = [75*mm, 25*mm, 25*mm, 22*mm, 22*mm, 16*mm, 25*mm]
    headers = ["Description", "Qty", "Unit Price", "Tax", "Discount", "Rate", "Total"]
    align = ["L", "R", "R", "R", "R", "R", "R"]

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(HexColor("#DDDDDD"))
    c.rect(col_x[0], y - 12, sum(col_w), 14, fill=1, stroke=0)
    c.setFillColor(colors.black)
    hy = y - 3
    for h, cx, cw, a in zip(headers, col_x, col_w, align):
        if a == "R": c.drawRightString(cx + cw - 1, hy, h)
        else: c.drawString(cx + 1, hy, h)
    y -= 14
    c.setLineWidth(0.3)

    for item in inv["line_items"]:
        row = [
            item["description"][:42],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(item["tax_amount"], sym),
            _fmt(item["discount_amount"], sym),
            f"{item.get('_tax_rate', 0)*100:.0f}%",
            _fmt(item["line_total"], sym),
        ]
        c.setFont("Helvetica", 7)
        for text, cx, cw, a in zip(row, col_x, col_w, align):
            if a == "R": c.drawRightString(cx + cw - 1, y, str(text))
            else: c.drawString(cx + 1, y, str(text))
        c.setStrokeColor(HexColor("#EEEEEE"))
        c.line(col_x[0], y - 3, col_x[0] + sum(col_w), y - 3)
        y -= 10
        if y < 70:
            c.showPage()
            y = PAGE_H - 20

    y -= 4
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    y -= 8
    _draw_totals_block(c, inv, PAGE_W - 80*mm, y, 65*mm)
    y -= 55
    c.setFont("Helvetica", 7)
    c.drawString(15*mm, y, f"Terms: Net {inv['payment_terms_days']} days | {inv['currency']}")
    return y - 15


# ── Template E: Informal / Stamp Style ───────────────────────────────────────

def draw_template_e(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    ORANGE = HexColor("#E65100")
    sym = inv["currency_symbol"]
    y = y_start

    # Centered header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(ORANGE)
    w = c.stringWidth(inv["seller"]["name"], "Helvetica-Bold", 18)
    c.drawString((PAGE_W - w) / 2, y, inv["seller"]["name"])
    c.setFillColor(colors.black)
    y -= 14
    c.setFont("Helvetica", 8)
    addr_w = c.stringWidth(inv["seller"]["address"], "Helvetica", 8)
    c.drawString((PAGE_W - addr_w) / 2, y, inv["seller"]["address"])
    y -= 20

    # Dashed border around invoice block
    c.setDash(4, 2)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1)
    c.rect(12*mm, y - 25, PAGE_W - 24*mm, 28, stroke=1, fill=0)
    c.setDash()

    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, y - 8, f"Invoice: {inv['invoice_number'] or 'N/A'}")
    c.drawString(PAGE_W/2, y - 8, f"Date: {inv['issue_date']}")
    c.drawString(15*mm, y - 18, f"Bill To: {inv['buyer']['name']}")
    c.drawString(PAGE_W/2, y - 18, f"Due: {inv['due_date']}")
    y -= 35

    # Table with dashed row separators
    col_x = [15*mm, 95*mm, 128*mm, 158*mm, 183*mm]
    col_w = [80*mm, 33*mm, 30*mm, 25*mm, 32*mm]
    headers = ["Item", "Qty", "Unit Price", "Tax", "Total"]
    align = ["L", "R", "R", "R", "R"]

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(ORANGE)
    for h, cx, cw, a in zip(headers, col_x, col_w, align):
        if a == "R": c.drawRightString(cx + cw, y, h)
        else: c.drawString(cx, y, h)
    c.setFillColor(colors.black)
    y -= 4
    c.setDash(3, 3)
    c.setLineWidth(0.5)
    c.line(15*mm, y, PAGE_W - 15*mm, y)
    c.setDash()
    y -= 10

    for item in inv["line_items"]:
        row = [
            item["description"][:48],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(item["tax_amount"], sym),
            _fmt(item["line_total"], sym),
        ]
        c.setFont("Helvetica", 8)
        for text, cx, cw, a in zip(row, col_x, col_w, align):
            if a == "R": c.drawRightString(cx + cw, y, str(text))
            else: c.drawString(cx, y, str(text))
        c.setDash(2, 4)
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.line(15*mm, y - 3, PAGE_W - 15*mm, y - 3)
        c.setDash()
        c.setStrokeColor(colors.black)
        y -= 11
        if y < 80:
            c.showPage()
            y = PAGE_H - 20

    y -= 8
    _draw_totals_block(c, inv, PAGE_W - 80*mm, y, 65*mm)
    y -= 55

    if inv.get("notes"):
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(HexColor("#666666"))
        c.drawString(15*mm, y, f"Note: {inv['notes']}")
        c.setFillColor(colors.black)
        y -= 12

    c.setFont("Helvetica", 8)
    c.drawString(15*mm, y, f"Payment: Net {inv['payment_terms_days']} days | {inv['currency']}")
    return y - 20


# ── Template F: Merged / multi-row group headers (GST-style) ─────────────────

def draw_template_f(c: rl_canvas.Canvas, inv: Dict[str, Any], y_start: float) -> float:
    """
    Indian-style GST invoice with a two-row table header:

        |                  |     |       |      Tax        | Discount |       |
        | Description      | Qty | Price | CGST  |  SGST  |          | Total |

    Drawn with explicit horizontal + vertical ruling so pdfplumber detects
    the two-row header and the merged 'Tax' cell.
    """
    NAVY = HexColor("#2C3E50")
    PALE = HexColor("#ECF0F1")
    sym = inv["currency_symbol"]
    y = y_start

    # Header band
    c.setFillColor(NAVY)
    c.rect(0, y - 48, PAGE_W, 48, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15 * mm, y - 22, inv["seller"]["name"])
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, y - 36, f"GSTIN: {inv['seller']['tax_id']}")
    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(PAGE_W - 15 * mm, y - 24, "TAX INVOICE")
    c.setFillColor(colors.black)
    y -= 60

    # Invoice meta strip
    c.setFont("Helvetica-Bold", 9)
    c.drawString(15 * mm, y, f"Invoice No: {inv['invoice_number'] or 'N/A'}")
    c.drawString(80 * mm, y, f"Date: {inv['issue_date']}")
    c.drawRightString(PAGE_W - 15 * mm, y, f"Currency: {inv['currency']}")
    y -= 18

    # Bill To / From
    c.setFont("Helvetica-Bold", 8)
    c.drawString(15 * mm, y, "FROM")
    c.drawString(PAGE_W / 2, y, "BILL TO")
    y -= 10
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, y, inv["seller"]["address"][:50])
    c.drawString(PAGE_W / 2, y, inv["buyer"]["name"])
    y -= 10
    c.drawString(15 * mm, y, inv["seller"]["city"])
    c.drawString(PAGE_W / 2, y, inv["buyer"]["address"][:50])
    y -= 18

    # Table columns
    # Layout: Description | Qty | Unit Price | CGST | SGST | Discount | Total
    col_x = [15 * mm, 78 * mm, 95 * mm, 118 * mm, 142 * mm, 162 * mm, 182 * mm]
    col_w = [63 * mm, 17 * mm, 23 * mm, 24 * mm, 20 * mm, 20 * mm, 28 * mm]
    table_left = col_x[0]
    table_right = col_x[-1] + col_w[-1]

    # === Two-row header ===
    # Row 1 (group): blank | blank | blank | <----- Tax -----> | blank | blank
    # Row 2 (sub):   Description | Qty | Unit Price | CGST | SGST | Discount | Total
    GROUP_H = 14
    SUB_H = 14
    header_top = y
    header_mid = y - GROUP_H
    header_bot = y - GROUP_H - SUB_H

    # Backgrounds
    c.setFillColor(PALE)
    c.rect(table_left, header_bot, table_right - table_left, GROUP_H + SUB_H, fill=1, stroke=0)
    c.setFillColor(colors.black)

    # Group cell: "Tax" spanning CGST + SGST columns (cols 3 and 4)
    tax_group_left = col_x[3]
    tax_group_right = col_x[4] + col_w[4]
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString((tax_group_left + tax_group_right) / 2, header_top - 10, "Tax")

    # Ruling: outer box
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.7)
    c.rect(table_left, header_bot, table_right - table_left, GROUP_H + SUB_H, fill=0, stroke=1)

    # Horizontal line between group and sub headers, but only across the
    # Tax-group span (so the merged cell visually spans both columns above).
    c.line(tax_group_left, header_mid, tax_group_right, header_mid)

    # Full horizontal line under the sub-header row
    c.line(table_left, header_bot, table_right, header_bot)

    # Vertical separators between all columns of the sub-header row
    for i in range(1, len(col_x)):
        x_sep = col_x[i]
        # Skip the divider INSIDE the tax-group span at the GROUP level only;
        # always draw it at the SUB level.
        if x_sep == col_x[4]:  # divider between CGST and SGST
            c.line(x_sep, header_bot, x_sep, header_mid)  # only sub-header part
        else:
            c.line(x_sep, header_bot, x_sep, header_top)

    # Sub-header labels
    sub_headers = ["Description", "Qty", "Unit Price", "CGST", "SGST", "Discount", "Total"]
    align = ["L", "R", "R", "R", "R", "R", "R"]
    sub_y = header_bot + 4
    for h, cx, cw, a in zip(sub_headers, col_x, col_w, align):
        if a == "R":
            c.drawRightString(cx + cw - 2, sub_y, h)
        else:
            c.drawString(cx + 2, sub_y, h)

    y = header_bot - 2

    # Data rows. For each item, split tax 50/50 into CGST + SGST so the
    # columns are non-zero and the math still totals to item.tax_amount.
    c.setFont("Helvetica", 8)
    for item in inv["line_items"]:
        cgst = round(item["tax_amount"] / 2, 2)
        sgst = round(item["tax_amount"] - cgst, 2)
        row = [
            item["description"][:42],
            f"{item['quantity']:.2f}",
            _fmt(item["unit_price"], sym),
            _fmt(cgst, sym),
            _fmt(sgst, sym),
            _fmt(item["discount_amount"], sym),
            _fmt(item["line_total"], sym),
        ]
        row_h = 12
        # Light ruling per row so pdfplumber sees discrete rows
        c.setStrokeColor(HexColor("#D5D8DC"))
        c.setLineWidth(0.3)
        c.line(table_left, y - row_h + 4, table_right, y - row_h + 4)
        c.setFillColor(colors.black)
        for text, cx, cw, a in zip(row, col_x, col_w, align):
            if a == "R":
                c.drawRightString(cx + cw - 2, y, str(text))
            else:
                c.drawString(cx + 2, y, str(text))
        # Vertical separators for the data row
        c.setLineWidth(0.3)
        for i in range(1, len(col_x)):
            c.line(col_x[i], y - row_h + 4, col_x[i], y + 4)
        # Outer left + right rules
        c.line(table_left, y - row_h + 4, table_left, y + 4)
        c.line(table_right, y - row_h + 4, table_right, y + 4)
        y -= row_h
        if y < 80:
            c.showPage()
            y = PAGE_H - 20

    y -= 8
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.line(table_left, y, table_right, y)
    y -= 6
    _draw_totals_block(c, inv, PAGE_W - 80 * mm, y, 65 * mm)
    y -= 60
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, y, f"Payment Terms: Net {inv['payment_terms_days']} days")
    return y - 18


TEMPLATES = [
    draw_template_a, draw_template_b, draw_template_c,
    draw_template_d, draw_template_e, draw_template_f,
]


def pick_template():
    return random.choice(TEMPLATES)


# ── Non-invoice page: Terms & Conditions ─────────────────────────────────────

def draw_terms_page(c: rl_canvas.Canvas) -> None:
    y = PAGE_H - 30*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_W / 2, y, "Terms and Conditions")
    y -= 20
    c.setFont("Helvetica", 9)
    lorem = (
        "1. Payment is due within the stated payment terms from the invoice date. "
        "Late payments may incur a penalty of 1.5% per month on outstanding amounts. "
        "2. All prices are exclusive of applicable taxes unless stated otherwise. "
        "3. Disputes must be raised within 7 days of receipt of this invoice. "
        "4. This invoice is governed by the laws of the issuing country. "
        "5. The buyer agrees to the seller's standard terms of service. "
        "6. Partial payments will be applied to the oldest outstanding balance first. "
        "7. In case of non-payment, the seller reserves the right to suspend services. "
        "8. All intellectual property created under this engagement remains with the seller "
        "until full payment is received."
    )
    words = lorem.split()
    line, lines = "", []
    for w in words:
        test = f"{line} {w}".strip()
        if c.stringWidth(test, "Helvetica", 9) < PAGE_W - 30*mm:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    for l in lines:
        c.drawString(15*mm, y, l)
        y -= 12
