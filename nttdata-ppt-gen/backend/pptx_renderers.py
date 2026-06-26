"""NTT DATA PPTX — All visual diagram renderers."""
import math
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from backend.pptx_primitives import (
    _rect, _rrect, _oval, _txt, _arrow, _col,
    C_BLUE, C_MID, C_TEAL, C_ACCENT, C_WHITE, C_MUTED, C_TEXT,
    C_GREEN, C_DKBG, C_MGRAY, C_NAVY, SW,
)


def _render_process_flow(sl, data, al, at, aw, ah, theme):
    steps = data.get("steps", []); n = len(steps)
    if not n: return
    tc = C_TEXT if theme == "light" else C_WHITE
    sub_c = RGBColor(0xCC, 0xDD, 0xFF)
    if data.get("direction", "horizontal") == "horizontal":
        bw = min(Inches(2.3), (aw - Inches(0.18) * (n - 1)) / max(n, 1))
        bh = Inches(1.65); gap = (aw - bw * n) / max(n - 1, 1); by = at + (ah - bh) / 2
        for i, s in enumerate(steps):
            x = al + i * (bw + gap); col = _col(s.get("color", "blue"))
            if i > 0: _arrow(sl, x - gap + Inches(0.05), by + bh / 2, x - Inches(0.05), by + bh / 2)
            _oval(sl, x + bw/2 - Inches(0.24), by - Inches(0.3), Inches(0.48), Inches(0.48), C_ACCENT)
            _txt(sl, str(i+1), x + bw/2 - Inches(0.24), by - Inches(0.26), Inches(0.48), Inches(0.38),
                 size=12, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
            _rrect(sl, x, by, bw, bh, col)
            _txt(sl, s.get("label",""), x, by + Inches(0.1), bw, Inches(0.44),
                 size=11, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
            if s.get("description",""):
                _txt(sl, s["description"], x+Inches(0.07), by+Inches(0.58), bw-Inches(0.14), Inches(0.95),
                     size=9, color=sub_c, align=PP_ALIGN.CENTER, wrap=True)
    else:
        bh = min(Inches(1.0), (ah - Inches(0.12) * (n-1)) / max(n, 1))
        bw = aw - Inches(0.6); xb = al + Inches(0.3)
        gap = (ah - bh * n) / max(n - 1, 1)
        for i, s in enumerate(steps):
            y = at + i * (bh + gap); col = _col(s.get("color","blue"))
            if i > 0: _arrow(sl, xb + bw/2, y - gap + Inches(0.04), xb + bw/2, y - Inches(0.04))
            _rrect(sl, xb, y, bw, bh, col)
            _txt(sl, f"{i+1}.  {s.get('label','')}", xb+Inches(0.1), y+Inches(0.06), bw-Inches(0.2), Inches(0.38),
                 size=12, bold=True, color=C_WHITE)
            if s.get("description",""):
                _txt(sl, s["description"], xb+Inches(0.1), y+Inches(0.46), bw-Inches(0.2), bh-Inches(0.52),
                     size=10, color=sub_c)


def _render_architecture(sl, data, al, at, aw, ah, theme):
    layers = data.get("layers", [])
    if not layers: return
    n = len(layers)
    lh = (ah - Inches(0.06) * (n-1)) / max(n, 1)
    LCOLS = [C_BLUE, C_MID, C_TEAL, RGBColor(0x1A,0x5C,0x8A), C_MUTED]
    for li, layer in enumerate(layers):
        ly = at + li * (lh + Inches(0.06))
        col = _col(layer.get("color","blue")) if layer.get("color") else LCOLS[li % len(LCOLS)]
        bg = RGBColor(230,240,255) if theme=="light" else RGBColor(
            max(0,col[0]-160), max(0,col[1]-130), max(0,col[2]-80))
        _rrect(sl, al, ly, aw, lh, bg, lc=col, lpt=1)
        lw = Inches(1.6)
        _txt(sl, layer.get("name",""), al+Inches(0.06), ly+Inches(0.06), lw-Inches(0.1), lh-Inches(0.12),
             size=9, bold=True, color=col if theme=="light" else C_WHITE)
        comps = layer.get("components", [])
        if not comps: continue
        ca_l = al + lw + Inches(0.1); ca_w = aw - lw - Inches(0.2)
        nc = len(comps)
        cw = min(Inches(2.2), (ca_w - Inches(0.08)*(nc-1)) / max(nc, 1))
        ch = lh - Inches(0.22)
        cgap = (ca_w - cw * nc) / max(nc - 1, 1)
        for ci, comp in enumerate(comps):
            cx = ca_l + ci * (cw + cgap); cy = ly + Inches(0.11)
            rad = 0.40 if comp.get("type")=="cloud" else (0.30 if comp.get("type")=="cylinder" else 0.12)
            _rrect(sl, cx, cy, cw, ch, col, lc=C_ACCENT, lpt=0.75, rad=rad)
            _txt(sl, comp.get("name",""), cx, cy+Inches(0.06), cw, ch-Inches(0.12),
                 size=9, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)


def _render_flowchart(sl, data, al, at, aw, ah, theme):
    nodes = data.get("nodes", []); edges = data.get("edges", [])
    if not nodes: return
    n = len(nodes); cols = min(4, n); rows = math.ceil(n / cols)
    cw = aw / cols; rh = ah / rows; bw = cw * 0.72; bh = rh * 0.58; pos = {}
    for i, node in enumerate(nodes):
        ci = i % cols; ri = i // cols
        x = al + ci * cw + (cw - bw) / 2; y = at + ri * rh + (rh - bh) / 2
        pos[node["id"]] = (x + bw/2, y + bh/2, x, y, bw, bh)
        col = _col(node.get("color","blue")); shape = node.get("shape","rect")
        if shape == "diamond":
            mx = x + bw/2; my = y + bh/2; d = min(bw, bh) * 0.85
            _rrect(sl, mx-d/2, my-d*0.38, d, d*0.75, col, rad=0.06)
        elif shape in ("rounded","oval"):
            _rrect(sl, x, y, bw, bh, col, rad=0.38)
        else:
            _rrect(sl, x, y, bw, bh, col)
        _txt(sl, node.get("label",""), x+Inches(0.05), y+Inches(0.06), bw-Inches(0.1), bh-Inches(0.12),
             size=10, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    for e in edges:
        s = pos.get(e.get("from")); d = pos.get(e.get("to"))
        if s and d:
            if abs(s[0]-d[0]) < Inches(0.5):
                _arrow(sl, s[0], s[1]+s[5]/2, d[0], d[1]-d[5]/2)
            else:
                _arrow(sl, s[0]+s[4]/2, s[1], d[0]-d[4]/2, d[1])
            lbl = e.get("label","")
            if lbl:
                mx = (s[0]+d[0])/2; my = (s[1]+d[1])/2
                _txt(sl, lbl, mx-Inches(0.4), my-Inches(0.18), Inches(0.8), Inches(0.35),
                     size=8, color=C_ACCENT, align=PP_ALIGN.CENTER)


def _render_timeline(sl, data, al, at, aw, ah, theme):
    ms = data.get("milestones", [])
    if not ms: return
    n = len(ms)
    tc = C_TEXT if theme == "light" else C_WHITE
    mc = C_MUTED if theme == "light" else RGBColor(0xCC, 0xDD, 0xFF)
    STATUS = {"done":C_GREEN,"active":C_BLUE,"planned":C_MUTED}
    iw = aw / n; sy = at + ah * 0.42
    _rect(sl, al, sy - Inches(0.03), aw, Inches(0.06), C_ACCENT)
    for i, m in enumerate(ms):
        cx = al + i * iw + iw/2; dr = Inches(0.22)
        col = STATUS.get(m.get("status","planned"), C_BLUE)
        _oval(sl, cx - dr, sy - dr, dr*2, dr*2, col, C_WHITE, 1.5)
        _txt(sl, m.get("phase",""), cx-iw/2+Inches(0.05), at+Inches(0.05), iw-Inches(0.1), Inches(0.38),
             size=11, bold=True, color=tc, align=PP_ALIGN.CENTER)
        _txt(sl, m.get("period",""), cx-iw/2+Inches(0.05), at+Inches(0.46), iw-Inches(0.1), Inches(0.28),
             size=9, color=mc, align=PP_ALIGN.CENTER, italic=True)
        for di, dlv in enumerate(m.get("deliverables",[])[:3]):
            _txt(sl, f"\u25b8 {dlv}", cx-iw/2+Inches(0.05), sy+dr+Inches(0.1)+di*Inches(0.34),
                 iw-Inches(0.1), Inches(0.3), size=9, color=tc)


def _render_comparison_table(sl, data, al, at, aw, ah, theme):
    headers = data.get("headers",[]); rows = data.get("rows",[])
    hi_col = data.get("highlight_col", 1)
    if not headers or not rows: return
    nc = len(headers); nr = len(rows)
    rh = min(Inches(0.54), (ah - Inches(0.54)) / max(nr, 1)); cw = aw / nc
    for ci, h in enumerate(headers):
        hc = C_BLUE if ci==0 else (C_ACCENT if ci==hi_col else C_MID)
        _rect(sl, al+ci*cw, at, cw-Inches(0.03), Inches(0.5), hc)
        _txt(sl, h, al+ci*cw+Inches(0.08), at+Inches(0.07), cw-Inches(0.18), Inches(0.36),
             size=11, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    for ri, row in enumerate(rows):
        y = at + Inches(0.54) + ri * rh
        bg0 = RGBColor(0xEE,0xF4,0xFF) if theme=="light" else RGBColor(0x1A,0x2A,0x50)
        bg1 = RGBColor(0xFF,0xFF,0xFF) if theme=="light" else RGBColor(0x12,0x1E,0x3E)
        rbg = bg0 if ri % 2 == 0 else bg1
        cells = [row.get("aspect","")] + list(row.get("values",[]))
        for ci in range(nc):
            val = cells[ci] if ci < len(cells) else ""
            bg = (RGBColor(0xD8,0xEE,0xFF) if theme=="light" else RGBColor(0x00,0x4E,0x9A)) if ci==hi_col else rbg
            _rect(sl, al+ci*cw, y, cw-Inches(0.03), rh-Inches(0.04), bg)
            fc = C_TEXT if (theme=="light" and ci!=hi_col) else C_WHITE
            _txt(sl, str(val), al+ci*cw+Inches(0.08), y+Inches(0.06), cw-Inches(0.16), rh-Inches(0.12),
                 size=10, color=fc, align=PP_ALIGN.LEFT if ci==0 else PP_ALIGN.CENTER)


def _render_swot(sl, data, al, at, aw, ah, theme):
    qw = aw/2 - Inches(0.06); qh = ah/2 - Inches(0.06)
    quads = [
        (0, 0, C_BLUE, "Strengths", data.get("strengths",[])),
        (aw/2+Inches(0.06), 0, C_TEAL, "Weaknesses", data.get("weaknesses",[])),
        (0, ah/2+Inches(0.06), C_MID, "Opportunities", data.get("opportunities",[])),
        (aw/2+Inches(0.06), ah/2+Inches(0.06), C_MUTED, "Threats", data.get("threats",[])),
    ]
    for dx, dy, col, label, items in quads:
        qx = al+dx; qy = at+dy
        _rrect(sl, qx, qy, qw, qh, col)
        _txt(sl, label, qx+Inches(0.1), qy+Inches(0.07), qw-Inches(0.2), Inches(0.36),
             size=13, bold=True, color=C_WHITE)
        for ii, item in enumerate(items[:4]):
            _txt(sl, f"\u25b8  {item}", qx+Inches(0.12), qy+Inches(0.48)+ii*Inches(0.34),
                 qw-Inches(0.24), Inches(0.3), size=10, color=RGBColor(0xCC,0xEE,0xFF))


def _render_kpi_cards(sl, data, al, at, aw, ah, theme):
    """KPI cards: value (large) + title + label + optional description. Text-right icon."""
    cards = data.get("cards",[]); n = min(len(cards), 5)
    if not n: return
    gap = Inches(0.12); cw = (aw - gap*(n-1)) / n; ch = ah - Inches(0.06)
    for i, card in enumerate(cards[:n]):
        cx = al + i*(cw+gap); col = _col(card.get("color","blue"))
        _rrect(sl, cx, at, cw, ch, col, rad=0.08)
        # Value (large centred)
        val = card.get("value","")
        val_size = 34 if len(val) <= 4 else (28 if len(val) <= 6 else 22)
        _txt(sl, val, cx, at+Inches(0.18), cw, Inches(0.78),
             font="Calibri", size=val_size, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        # Trend arrow (up/down) — top-right accent
        trend = card.get("trend", "")
        if trend in ("up", "down"):
            arrow = "▲" if trend == "up" else "▼"
            arrow_col = RGBColor(0x00,0xDD,0x88) if trend == "up" else RGBColor(0xFF,0x66,0x44)
            _txt(sl, arrow, cx + cw - Inches(0.4), at + Inches(0.1), Inches(0.35), Inches(0.35),
                 size=14, bold=True, color=arrow_col, align=PP_ALIGN.CENTER)
        # Title
        _txt(sl, card.get("title",""), cx, at+Inches(1.0), cw, Inches(0.32),
             size=10, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        # Label / subtitle
        _txt(sl, card.get("label",""), cx, at+Inches(1.34), cw, Inches(0.26),
             size=8, color=RGBColor(0xCC,0xDD,0xFF), align=PP_ALIGN.CENTER)
        # Description (if provided) — small text at bottom
        desc = card.get("description","")
        if desc and ch > Inches(1.8):
            _txt(sl, desc, cx+Inches(0.1), at+Inches(1.62), cw-Inches(0.2),
                 ch-Inches(1.68), size=8, color=RGBColor(0xCC,0xDD,0xFF),
                 wrap=True, align=PP_ALIGN.CENTER)


def _render_two_column_cards(sl, data, al, at, aw, ah, theme):
    left = data.get("left_items",[]); right = data.get("right_items",[])
    lt = data.get("left_title",""); rt = data.get("right_title","")
    cw = aw/2 - Inches(0.12)
    for side, title, items, xoff in [(0,lt,left,al),(1,rt,right,al+aw/2+Inches(0.12))]:
        if title:
            _txt(sl, title, xoff, at, cw, Inches(0.36), size=13, bold=True, color=C_ACCENT)
        ys = at + (Inches(0.42) if title else 0)
        ch = (ah - (Inches(0.42) if title else 0)) / max(len(items),1) - Inches(0.1)
        ch = min(ch, Inches(1.15))
        for ii, item in enumerate(items[:5]):
            iy = ys + ii*(ch+Inches(0.1))
            col = C_MID if side==0 else C_TEAL
            _rrect(sl, xoff, iy, cw, ch, col)
            _txt(sl, f"{item.get('icon','▸')}  {item.get('title','')}",
                 xoff+Inches(0.1), iy+Inches(0.06), cw-Inches(0.2), Inches(0.36),
                 size=11, bold=True, color=C_WHITE)
            body = item.get("body","")
            if body:
                _txt(sl, body, xoff+Inches(0.1), iy+Inches(0.42), cw-Inches(0.2), ch-Inches(0.48),
                     size=9, color=RGBColor(0xCC,0xDD,0xFF), wrap=True)


def _render_agenda(sl, data, al, at, aw, ah, theme):
    """Modern numbered agenda cards — number badge left, title+subtitle right."""
    items = data.get("items",[]); n = len(items)
    if not n: return
    cols = 2; rows = math.ceil(n/cols)
    cw = (aw - Inches(0.2)) / cols; gap_h = Inches(0.1)
    ch_avail = (ah - gap_h * (rows - 1)) / max(rows, 1)
    # Scale height to content
    max_sub = max((len(it.get("subtitle","")) for it in items[:8]), default=0)
    ch = min(max(Inches(0.82), Inches(0.82) + Inches(0.01) * (max_sub // 30)),
             min(ch_avail, Inches(1.2)))
    tc = C_TEXT if theme == "light" else C_WHITE
    sc = C_MUTED if theme == "light" else RGBColor(0xBB, 0xCC, 0xEE)
    bg = C_WHITE if theme == "light" else RGBColor(0x10, 0x20, 0x4A)
    bdr = C_MGRAY if theme == "light" else RGBColor(0x2A, 0x3A, 0x60)
    # Left accent stripe on card
    STRIPE_COLS = [C_BLUE, C_TEAL, C_MID, RGBColor(0x1A,0x5C,0x8A),
                   C_ACCENT, C_BLUE, C_TEAL, C_MID]
    for i, item in enumerate(items[:8]):
        ci = i % cols; ri = i // cols
        x = al + ci * (cw + Inches(0.2))
        y = at + ri * (ch + gap_h)
        # Card bg
        _rrect(sl, x, y, cw, ch, bg, lc=bdr, lpt=0.5)
        # Left color stripe (accent)
        stripe_col = STRIPE_COLS[i % len(STRIPE_COLS)]
        _rrect(sl, x, y, Inches(0.08), ch, stripe_col, rad=0.5)
        # Number badge
        badge_r = Inches(0.22)
        _oval(sl, x + Inches(0.18), y + ch/2 - badge_r, badge_r*2, badge_r*2, stripe_col)
        _txt(sl, str(i+1), x + Inches(0.18), y + ch/2 - badge_r*0.8,
             badge_r*2, badge_r*1.6, size=11, bold=True, color=C_WHITE,
             align=PP_ALIGN.CENTER)
        # Title
        title_y = y + Inches(0.1)
        _txt(sl, item.get("title",""), x + Inches(0.68), title_y,
             cw - Inches(0.78), Inches(0.35),
             size=12, bold=True, color=tc)
        # Subtitle
        sub = item.get("subtitle","")
        if sub:
            _txt(sl, sub, x + Inches(0.68), title_y + Inches(0.36),
                 cw - Inches(0.78), ch - Inches(0.46),
                 size=9, color=sc, wrap=True)


def _render_pyramid(sl, data, al, at, aw, ah, theme):
    levels = data.get("levels",[]); n = len(levels)
    if not n: return
    COLS = [C_ACCENT, C_MID, C_BLUE, C_NAVY, RGBColor(0x00,0x08,0x28)]
    lh = ah / n
    for i, level in enumerate(levels):
        factor = (i+1)/n
        lw = aw * factor; lx = al + (aw-lw)/2; ly = at + i*lh
        col = _col(level.get("color","blue")) if level.get("color") else COLS[i%len(COLS)]
        _rrect(sl, lx, ly, lw, lh-Inches(0.04), col, rad=0.05)
        _txt(sl, level.get("label",""), lx, ly+Inches(0.06), lw, lh-Inches(0.12),
             size=11, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        if level.get("description",""):
            _txt(sl, level["description"], lx, ly+Inches(0.42), lw, lh-Inches(0.48),
                 size=9, color=RGBColor(0xCC,0xDD,0xFF), align=PP_ALIGN.CENTER, wrap=True)


def _render_cycle(sl, data, al, at, aw, ah, theme):
    steps = data.get("steps",[]); n = len(steps)
    if not n: return
    COLS = [C_BLUE, C_MID, C_TEAL, C_ACCENT, RGBColor(0x4A,0x90,0xD9)]
    cx = al + aw/2; cy = at + ah/2
    rx = min(aw*0.35, Inches(2.5)); ry = min(ah*0.38, Inches(1.8))
    bw = Inches(1.5); bh = Inches(0.8)
    for i, step in enumerate(steps):
        angle = (2*math.pi*i/n) - math.pi/2
        sx = cx + rx*math.cos(angle); sy = cy + ry*math.sin(angle)
        col = _col(step.get("color","blue")) if step.get("color") else COLS[i%len(COLS)]
        _rrect(sl, sx-bw/2, sy-bh/2, bw, bh, col, rad=0.3)
        _txt(sl, step.get("label",""), sx-bw/2, sy-bh/2+Inches(0.06), bw, bh-Inches(0.12),
             size=10, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        if i < n-1:
            ni = (i+1)%n; na = (2*math.pi*(i+0.5)/n) - math.pi/2
            tx = cx + rx*math.cos(na); ty = cy + ry*math.sin(na)
            _arrow(sl, sx, sy, tx, ty, color=C_ACCENT, w=1.2)
    _txt(sl, data.get("center_label",""), cx-Inches(0.8), cy-Inches(0.25), Inches(1.6), Inches(0.5),
         size=10, bold=True, color=C_TEXT if theme=="light" else C_WHITE, align=PP_ALIGN.CENTER)



def _render_hierarchy(sl, data, al, at, aw, ah, theme):
    root_label = data.get("root", "")
    nodes = data.get("nodes", [])
    if not root_label and not nodes:
        return
    all_nodes = ([{"label": root_label, "color": "navy"}] if root_label else []) + nodes
    n = len(all_nodes)
    if n == 0:
        return
    cols_n = min(4, n)
    rows_n = math.ceil(n / cols_n)
    COLS = [C_NAVY, C_BLUE, C_MID, C_TEAL, RGBColor(0x1A, 0x5C, 0x8A)]
    cw = (aw - Inches(0.1) * (cols_n - 1)) / max(cols_n, 1)
    ch = min(Inches(0.8), (ah - Inches(0.1) * (rows_n - 1)) / max(rows_n, 1))
    for i, node in enumerate(all_nodes[:12]):
        ci = i % cols_n
        ri = i // cols_n
        x = al + ci * (cw + Inches(0.1))
        y = at + ri * (ch + Inches(0.1))
        col = _col(node.get("color", "blue")) if node.get("color") else COLS[i % len(COLS)]
        _rrect(sl, x, y, cw, ch, col)
        _txt(sl, node.get("label", ""), x + Inches(0.05), y + Inches(0.06),
             cw - Inches(0.1), ch - Inches(0.12),
             size=10, bold=(i == 0), color=C_WHITE, align=PP_ALIGN.CENTER)
        if i > 0 and ri > 0:
            px = al + ci * (cw + Inches(0.1)) + cw / 2
            py = at + (ri - 1) * (ch + Inches(0.1)) + ch
            _arrow(sl, px, py, x + cw / 2, y, color=C_ACCENT, w=0.8)


def _render_roadmap(sl, data, al, at, aw, ah, theme):
    phases = data.get("phases", [])
    if not phases:
        return
    mc = C_MUTED if theme == "light" else RGBColor(0xCC, 0xDD, 0xFF)
    COLS = [C_BLUE, C_MID, C_TEAL, RGBColor(0x1A, 0x5C, 0x8A), C_ACCENT]
    n = len(phases)
    ph = (ah - Inches(0.08) * (n - 1)) / max(n, 1)
    for i, phase in enumerate(phases):
        y = at + i * (ph + Inches(0.08))
        col = COLS[i % len(COLS)]
        label_w = Inches(2.0)
        _rrect(sl, al, y, label_w, ph, col)
        _txt(sl, phase.get("name", ""), al + Inches(0.08), y + Inches(0.06),
             label_w - Inches(0.16), ph - Inches(0.12),
             size=11, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        period = phase.get("period", "")
        if period:
            _txt(sl, period, al + label_w + Inches(0.08), y + Inches(0.06),
                 Inches(1.4), ph - Inches(0.12), size=10, color=mc, italic=True)
        tasks = phase.get("tasks", [])
        if tasks:
            tw = (aw - label_w - Inches(1.6) - Inches(0.06) * (len(tasks) - 1)) / max(len(tasks), 1)
            tw = max(tw, Inches(0.8))
            for ti, task in enumerate(tasks[:6]):
                tx = al + label_w + Inches(1.55) + ti * (tw + Inches(0.06))
                bg = RGBColor(0xD8, 0xEE, 0xFF) if theme == "light" else RGBColor(0x1A, 0x3A, 0x6A)
                _rrect(sl, tx, y + Inches(0.06), tw, ph - Inches(0.12), bg)
                fc = C_TEXT if theme == "light" else C_WHITE
                _txt(sl, task, tx + Inches(0.05), y + Inches(0.1),
                     tw - Inches(0.1), ph - Inches(0.2), size=9, color=fc, wrap=True)


RENDERERS = {
    "process_flow":     _render_process_flow,
    "architecture":     _render_architecture,
    "flowchart":        _render_flowchart,
    "timeline":         _render_timeline,
    "comparison_table": _render_comparison_table,
    "agenda":           _render_agenda,
    "swot":             _render_swot,
    "kpi_cards":        _render_kpi_cards,
    "two_column_cards": _render_two_column_cards,
    "pyramid":          _render_pyramid,
    "cycle":            _render_cycle,
    "hierarchy":        _render_hierarchy,
    "roadmap":          _render_roadmap,
}


def place_visual(sl, visual, al, at, aw, ah, theme):
    if not visual:
        return
    vtype = visual.get("type", "none")
    vdata = visual.get("data", {}) or {}
    if not vtype or vtype == "none" or not vdata:
        return
    fn = RENDERERS.get(vtype)
    if fn:
        try:
            fn(sl, vdata, al, at, aw, ah, theme)
        except Exception:
            _txt(sl, "[ " + vtype.replace("_", " ").title() + " ]",
                 al, at + ah // 2 - 182880, aw, 548640,
                 size=12, color=C_ACCENT, align=PP_ALIGN.CENTER)
