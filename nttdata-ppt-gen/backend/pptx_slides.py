"""NTT DATA PPTX — Slide builders v3: proper cover layout, dynamic cards,
icon-right text-left, professional spacing, no duplicate titles, no decorative clutter."""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from backend.pptx_primitives import (
    _rect, _rrect, _oval, _txt, _bullets, _logo,
    C_BLUE, C_MID, C_TEAL, C_ACCENT, C_WHITE, C_LGRAY, C_MGRAY,
    C_MUTED, C_TEXT, C_DKBG, C_NAVY,
    SW, SH,
    CVR_LOGO_L, CVR_LOGO_T, CVR_LOGO_W, CVR_LOGO_H,
    CT_TTL_L, CT_TTL_T, CT_TTL_W, CT_TTL_H,
    FT_LOGO_T,
    CL_LOGO_L, CL_LOGO_W, CL_LOGO_H,
    footer,
)
from backend.pptx_renderers import place_visual, _render_agenda

# ── Layout grid constants ────────────────────────────────────────────────────
MARGIN_L   = Inches(0.406)
MARGIN_R   = Inches(0.406)
CONTENT_L  = MARGIN_L
CONTENT_W  = SW - MARGIN_L - MARGIN_R
CONTENT_T  = Inches(1.32)          # starts below title row
CONTENT_H  = FT_LOGO_T - CONTENT_T - Inches(0.06)
TITLE_SIZE = 30                     # standard content title
BODY_SIZE  = 12                     # standard body text
CARD_PAD   = Inches(0.14)           # padding inside cards
GAP        = Inches(0.12)           # gap between cards

# ── Shape icon palette (geometric shapes rendered via python-pptx) ──────────
_ICON_SHAPES = {
    "circle": 9,   # oval
    "square": 1,   # rect
    "round":  5,   # rounded rect
    "diamond": 4,  # diamond shape type
}

# ── Professional icon symbols (Wingdings-compatible Unicode) ─────────────────
# These render correctly in PowerPoint with Wingdings/Symbol fonts.
# We draw icons as small coloured circles with a letter/number inside.
def _draw_icon_circle(sl, cx, cy, r, bg_col, label, label_size=10):
    """Draw a small filled circle with a centred label — professional icon style."""
    _oval(sl, cx - r, cy - r, r*2, r*2, fill=bg_col)
    _txt(sl, label, cx - r, cy - r*0.9, r*2, r*1.8,
         size=label_size, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)


# ── Background helpers ───────────────────────────────────────────────────────
def _bg(sl, theme):
    bg = C_LGRAY if theme == "light" else RGBColor(0x04, 0x10, 0x30)
    _rect(sl, 0, 0, SW, SH, bg)

def _dark_bg(sl):
    _rect(sl, 0, 0, SW, SH, C_DKBG)


# ── Eyebrow label (tiny section tag ABOVE title — never duplicates title) ───
def _eyebrow(sl, section, theme):
    if not section:
        return
    tag = section.strip().upper()[:24]
    _txt(sl, tag, CT_TTL_L, Inches(0.06), CT_TTL_W, Inches(0.27),
         font="Calibri", size=9, bold=True,
         color=C_ACCENT, italic=False, wrap=False)


# ── Single slide title (template-exact position, one occurrence only) ────────
def _title(sl, title, theme, size=None):
    tc = C_TEXT if theme == "light" else C_WHITE
    if size is None:
        size = 24 if len(title) > 55 else (27 if len(title) > 40 else TITLE_SIZE)
    _txt(sl, title, CT_TTL_L, CT_TTL_T, CT_TTL_W, CT_TTL_H,
         font="Calibri", size=size, bold=True, color=tc)


# ── Dynamic info cards (text LEFT, icon circle RIGHT, proportional height) ──
def _info_cards(sl, items, theme, al, at, aw, ah, icon_labels=None):
    """Render items as info cards: text left, icon right, height fits content."""
    if not items:
        return
    n = min(len(items), 6)
    COLS_BG = [C_BLUE, C_MID, C_TEAL, RGBColor(0x1A,0x5C,0x8A),
               C_ACCENT, RGBColor(0x0A,0x5C,0x40)]
    # Determine grid
    if n <= 2:
        cols_n, rows_n = n, 1
    elif n <= 4:
        cols_n, rows_n = 2, (n+1)//2
    else:
        cols_n, rows_n = 3, (n+2)//3

    cw = (aw - GAP * (cols_n - 1)) / cols_n
    total_gap_h = GAP * (rows_n - 1)

    # Calculate per-card height: scale with text length
    max_chars = max(len(b) for b in items[:n]) if items else 40
    # Min height 0.7", max height 1.6", based on content length
    ch_base = min(max(Inches(0.7), Inches(0.04) * (max_chars // 30 + 1.5)), Inches(1.6))
    ch = min(ch_base, (ah - total_gap_h) / rows_n)

    for i, item in enumerate(items[:n]):
        ci = i % cols_n; ri = i // cols_n
        x = al + ci * (cw + GAP)
        y = at + ri * (ch + GAP)
        col = COLS_BG[i % len(COLS_BG)]

        # Card background
        _rrect(sl, x, y, cw, ch, col, rad=0.08)

        # Text on left (leaving space for icon on right)
        icon_w = Inches(0.5)
        txt_w = cw - icon_w - CARD_PAD * 2 - Inches(0.1)
        _txt(sl, item,
             x + CARD_PAD, y + CARD_PAD,
             txt_w, ch - CARD_PAD * 2,
             size=10, color=C_WHITE, wrap=True)

        # Icon circle on right — use number or custom label
        if icon_labels and i < len(icon_labels):
            lbl = str(icon_labels[i])
        else:
            lbl = str(i + 1)
        icon_r = Inches(0.18)
        icon_cx = x + cw - icon_r - Inches(0.12)
        icon_cy = y + ch / 2
        icon_bg = RGBColor(0xFF, 0xFF, 0xFF)
        icon_lbl_col = col
        _oval(sl, icon_cx - icon_r, icon_cy - icon_r,
              icon_r*2, icon_r*2, fill=icon_bg)
        from pptx.enum.text import PP_ALIGN as _PA
        _txt(sl, lbl,
             icon_cx - icon_r, icon_cy - icon_r*0.9,
             icon_r*2, icon_r*1.8,
             size=9, bold=True, color=icon_lbl_col,
             align=_PA.CENTER)


# ── Build Cover (professional consulting layout) ─────────────────────────────
def build_cover(sl, data, theme):
    """
    Cover layout per spec:
      Top-left:  Presented By / Date / Version (small metadata)
      Top-right: NTT DATA Logo
      Center:    Title (primary focus)
      Below:     Subtitle
      Footer:    Copyright bar
    """
    _dark_bg(sl)
    # Subtle left panel
    _rect(sl, 0, 0, Inches(9.0), SH, RGBColor(0x00, 0x0C, 0x28))
    # Right area — decorative panel
    _rect(sl, Inches(9.0), 0, SW - Inches(9.0), SH, RGBColor(0x00, 0x18, 0x4E))
    # Vertical accent stripe between panels
    _rect(sl, Inches(9.0), 0, Inches(0.05), SH, C_ACCENT)

    # ── Top-left: metadata block ──────────────────────────────────────────
    bullets = [b for b in (data.get("bullets") or []) if b][:4]
    meta_y = Inches(0.22)
    meta_labels = ["Presented By", "Date", "Version", "Classification"]
    for idx, b in enumerate(bullets):
        label = meta_labels[idx] if idx < len(meta_labels) else ""
        if label:
            _txt(sl, label.upper(),
                 Inches(0.42), meta_y, Inches(3.0), Inches(0.18),
                 size=7, bold=True,
                 color=RGBColor(0x55, 0x88, 0xBB), italic=False)
            meta_y += Inches(0.18)
        _txt(sl, b,
             Inches(0.42), meta_y, Inches(3.5), Inches(0.26),
             size=11, color=C_WHITE)
        meta_y += Inches(0.32)

    # ── Top-right: NTT DATA logo ──────────────────────────────────────────
    _logo(sl, "dark", SW - Inches(2.5), Inches(0.28), Inches(2.1), Inches(0.43))

    # ── Centre: Title ─────────────────────────────────────────────────────
    title = data.get("title", "")
    ts = 44 if len(title) <= 22 else (36 if len(title) <= 35 else 28)
    _txt(sl, title,
         Inches(0.5), Inches(2.6), Inches(8.2), Inches(2.0),
         font="Calibri", size=ts, bold=True, color=C_WHITE)

    # Accent underline
    _rect(sl, Inches(0.5), Inches(4.65), Inches(1.5), Pt(3), C_ACCENT)

    # ── Below title: Subtitle ─────────────────────────────────────────────
    sub = data.get("subtitle") or ""
    if sub:
        _txt(sl, sub,
             Inches(0.5), Inches(4.85), Inches(8.2), Inches(0.6),
             size=18, color=RGBColor(0xAA, 0xC4, 0xE8))

    # ── Right panel: NTT branding accent ──────────────────────────────────
    _txt(sl, "NTT DATA",
         Inches(9.2), Inches(3.3), Inches(3.8), Inches(0.7),
         font="Calibri", size=24, bold=True,
         color=RGBColor(0x33, 0x66, 0xAA), align=PP_ALIGN.CENTER)
    _txt(sl, "Business Solutions",
         Inches(9.2), Inches(4.0), Inches(3.8), Inches(0.35),
         size=11, color=RGBColor(0x55, 0x88, 0xBB), align=PP_ALIGN.CENTER)

    # ── Footer ────────────────────────────────────────────────────────────
    _rect(sl, 0, SH - Inches(0.42), SW, Inches(0.42), RGBColor(0x00, 0x06, 0x18))
    _txt(sl, "\u00a9 2026 NTT DATA Business Solutions",
         Inches(0.4), SH - Inches(0.35), Inches(7), Inches(0.28),
         size=8, color=RGBColor(0x66, 0x80, 0xA0))


# ── Build Agenda (modern numbered cards) ─────────────────────────────────────
def build_agenda(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, "AGENDA", theme)
    _title(sl, data.get("title", "Agenda"), theme)
    visual = data.get("visual", {}) or {}
    if visual.get("type") == "agenda" and (visual.get("data") or {}).get("items"):
        place_visual(sl, visual, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme)
    else:
        bullets = [b for b in (data.get("bullets") or []) if b]
        items = [{"title": b, "subtitle": ""} for b in bullets]
        if items:
            _render_agenda(sl, {"items": items}, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme)
    footer(sl, theme, num, total)


# ── Build Two-Column (bullets left / visual right) ───────────────────────────
def build_two_column(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, data.get("section", ""), theme)
    _title(sl, data.get("title", ""), theme)
    visual = data.get("visual", {}) or {}
    bullets = [b for b in (data.get("bullets") or []) if b]
    has_visual = visual.get("type", "none") != "none" and visual.get("data")
    if has_visual and bullets:
        _bullets(sl, bullets, CONTENT_L, CONTENT_T, Inches(5.6), CONTENT_H, theme)
        place_visual(sl, visual, Inches(6.1), CONTENT_T, Inches(6.8), CONTENT_H, theme)
    elif has_visual and not bullets:
        place_visual(sl, visual, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme)
    elif bullets:
        if len(bullets) <= 5:
            _info_cards(sl, bullets, theme, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H)
        else:
            _bullets(sl, bullets, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme, size=13)
    footer(sl, theme, num, total)


# ── Build Full Visual ─────────────────────────────────────────────────────────
def build_full_visual(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, data.get("section", ""), theme)
    _title(sl, data.get("title", ""), theme)
    bullets = [b for b in (data.get("bullets") or []) if b]
    if bullets:
        n_b = min(len(bullets), 4)
        bh = Inches(0.38) * n_b
        tc = C_TEXT if theme == "light" else C_WHITE
        for bi, b in enumerate(bullets[:4]):
            _txt(sl, f"▸  {b}",
                 CONTENT_L, CONTENT_T + bi * Inches(0.36),
                 CONTENT_W, Inches(0.34),
                 size=11, color=tc)
        place_visual(sl, data.get("visual", {}),
                     CONTENT_L, CONTENT_T + bh + Inches(0.12),
                     CONTENT_W, CONTENT_H - bh - Inches(0.12), theme)
    else:
        place_visual(sl, data.get("visual", {}),
                     CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme)
    footer(sl, theme, num, total)


# ── Build Bullet List (auto cards when sparse) ────────────────────────────────
def build_bullet_list(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, data.get("section", ""), theme)
    _title(sl, data.get("title", ""), theme)
    bullets = [b for b in (data.get("bullets") or []) if b]
    visual = data.get("visual", {}) or {}
    has_visual = visual.get("type", "none") != "none" and visual.get("data")
    if has_visual:
        bh = CONTENT_H * 0.35 if bullets else 0
        if bullets:
            _bullets(sl, bullets, CONTENT_L, CONTENT_T,
                     CONTENT_W, bh, theme, size=12)
        place_visual(sl, visual,
                     CONTENT_L, CONTENT_T + bh + Inches(0.08),
                     CONTENT_W, CONTENT_H - bh - Inches(0.08), theme)
    elif len(bullets) <= 5 and bullets:
        _info_cards(sl, bullets, theme,
                    CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H)
    else:
        _bullets(sl, bullets, CONTENT_L, CONTENT_T,
                 CONTENT_W, CONTENT_H, theme, size=13)
    footer(sl, theme, num, total)


# ── Build Process Flow ────────────────────────────────────────────────────────
def build_process_flow(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, data.get("section", ""), theme)
    _title(sl, data.get("title", ""), theme)
    bullets = [b for b in (data.get("bullets") or []) if b]
    bh = Inches(0.28) if bullets else 0
    if bullets:
        tc = C_MUTED if theme == "light" else RGBColor(0xCC, 0xDD, 0xFF)
        _txt(sl, "   \u00b7   ".join(bullets[:3]),
             CONTENT_L, CONTENT_T, CONTENT_W, Inches(0.25),
             size=9, color=tc, italic=True)
    place_visual(sl, data.get("visual", {}),
                 CONTENT_L, CONTENT_T + bh, CONTENT_W, CONTENT_H - bh, theme)
    footer(sl, theme, num, total)


# ── Build KPI Dashboard ───────────────────────────────────────────────────────
def build_kpi_dashboard(sl, data, theme, num, total):
    _bg(sl, theme)
    _eyebrow(sl, data.get("section", ""), theme)
    _title(sl, data.get("title", ""), theme)
    visual = data.get("visual", {}) or {}
    has_visual = visual.get("type", "none") != "none" and visual.get("data")
    if has_visual:
        place_visual(sl, visual, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H, theme)
    else:
        bullets = [b for b in (data.get("bullets") or []) if b]
        _info_cards(sl, bullets, theme, CONTENT_L, CONTENT_T, CONTENT_W, CONTENT_H)
    footer(sl, theme, num, total)


# ── Build Section Divider ─────────────────────────────────────────────────────
def build_section_divider(sl, data, theme, num, total):
    _dark_bg(sl)
    _rect(sl, 0, 0, Inches(0.05), SH, C_ACCENT)
    title = data.get("title", "")
    ts = 38 if len(title) <= 25 else (30 if len(title) <= 40 else 24)
    _txt(sl, title, Inches(0.5), Inches(2.9), Inches(9.5), Inches(1.3),
         font="Calibri", size=ts, bold=True, color=C_WHITE)
    sub = data.get("subtitle") or ""
    if sub:
        _txt(sl, sub, Inches(0.5), Inches(4.3), Inches(9.5), Inches(0.5),
             size=18, color=C_ACCENT)
    _logo(sl, "dark", CVR_LOGO_L, CVR_LOGO_T, CVR_LOGO_W, CVR_LOGO_H)
    footer(sl, "dark", num, total)


# ── Build Closing (clean: Thank You + Questions + Logo) ───────────────────────
def build_closing(sl, data, theme):
    _dark_bg(sl)
    _rect(sl, 0, 0, Inches(0.05), SH, C_ACCENT)
    title = data.get("title", "Thank You")
    _txt(sl, title, Inches(1.0), Inches(2.0), SW - Inches(2.0), Inches(1.6),
         font="Calibri", size=56, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    sub = data.get("subtitle") or "Questions & Discussion"
    _txt(sl, sub, Inches(1.0), Inches(3.7), SW - Inches(2.0), Inches(0.5),
         size=20, color=C_ACCENT, align=PP_ALIGN.CENTER)
    # NTT DATA Logo centred
    _logo(sl, "dark", CL_LOGO_L, Inches(4.6), CL_LOGO_W, CL_LOGO_H)
    # Contact (first bullet only, small, bottom)
    bullets = [b for b in (data.get("bullets") or []) if b]
    if bullets:
        _txt(sl, bullets[0], Inches(1.0), Inches(6.1), SW - Inches(2.0), Inches(0.34),
             size=11, color=RGBColor(0x88, 0x9A, 0xB8), align=PP_ALIGN.CENTER, italic=True)
    _rect(sl, 0, SH - Inches(0.42), SW, Inches(0.42), RGBColor(0x00, 0x06, 0x18))
    _txt(sl, "\u00a9 2026 NTT DATA Business Solutions  |  nttdata.com",
         Inches(0.4), SH - Inches(0.35), Inches(8), Inches(0.28),
         size=8, color=RGBColor(0x66, 0x80, 0xA0))


# ── Layout dispatcher ─────────────────────────────────────────────────────────
LAYOUT_MAP = {
    "cover":            build_cover,
    "agenda":           build_agenda,
    "two_column":       build_two_column,
    "full_visual":      build_full_visual,
    "bullet_list":      build_bullet_list,
    "comparison_table": build_full_visual,
    "timeline_visual":  build_full_visual,
    "process_flow":     build_process_flow,
    "kpi_dashboard":    build_kpi_dashboard,
    "section_divider":  build_section_divider,
    "closing":          build_closing,
}
