"""NTT DATA PPTX — Primitives, brand colours, template positions, shared helpers."""
import io, base64
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

try:
    from backend.logo_b64 import LOGO_BLUE_B64, LOGO_WHITE_B64
    _LB = base64.b64decode(LOGO_BLUE_B64)
    _LW = base64.b64decode(LOGO_WHITE_B64)
except Exception:
    _LB = _LW = None

# ── Brand palette ───────────────────────────────────────────────────────────
C_NAVY   = RGBColor(0x00,0x18,0x6A)
C_BLUE   = RGBColor(0x00,0x30,0x87)
C_DKBG   = RGBColor(0x00,0x10,0x3A)
C_MID    = RGBColor(0x00,0x50,0xB3)
C_ACCENT = RGBColor(0x00,0xB4,0xD8)
C_WHITE  = RGBColor(0xFF,0xFF,0xFF)
C_LGRAY  = RGBColor(0xF5,0xF7,0xFA)
C_MGRAY  = RGBColor(0xCC,0xD8,0xEA)
C_MUTED  = RGBColor(0x5A,0x6A,0x8A)
C_TEXT   = RGBColor(0x0D,0x1B,0x3E)
C_TEAL   = RGBColor(0x00,0x7A,0x8A)
C_GREEN  = RGBColor(0x0A,0x7C,0x3E)
C_ORANGE = RGBColor(0xE8,0x6A,0x10)
C_RED    = RGBColor(0xC0,0x20,0x20)
C_PURPLE = RGBColor(0x5A,0x20,0x8A)
C_DKTEXT = RGBColor(0xBB,0xCC,0xEE)  # body text on dark bg

COLORS = {
    "blue":C_BLUE,"navy":C_NAVY,"mid":C_MID,"dark":C_DKBG,
    "teal":C_TEAL,"accent":C_ACCENT,"green":C_GREEN,
    "gray":C_MUTED,"orange":C_ORANGE,"red":C_RED,"purple":C_PURPLE,
}

# ── Slide canvas ────────────────────────────────────────────────────────────
SW = Inches(13.333)
SH = Inches(7.5)

# ── Template-exact positions (from NTT DATA pptx XML analysis) ──────────────
CVR_LOGO_L = Inches(0.406);  CVR_LOGO_T = Inches(0.350)
CVR_LOGO_W = Inches(2.143);  CVR_LOGO_H = Inches(0.438)
CVR_TTL_L  = Inches(0.416);  CVR_TTL_T  = Inches(2.667)
CVR_TTL_W  = Inches(5.243);  CVR_TTL_H  = Inches(1.500)
CVR_SUB_L  = Inches(0.416);  CVR_SUB_T  = Inches(4.167)
CVR_SUB_W  = Inches(5.243);  CVR_SUB_H  = Inches(0.800)
CVR_CURVE_L = Inches(5.868)

CT_TTL_L = Inches(0.406);  CT_TTL_T = Inches(0.365)
CT_TTL_W = Inches(12.521); CT_TTL_H = Inches(0.866)
CA_L     = Inches(0.406);  CA_T     = Inches(1.545)
CA_W     = Inches(12.521); CA_H     = Inches(5.276)

FT_T      = Inches(7.178)
FT_LOGO_L = Inches(11.517); FT_LOGO_T = Inches(7.054)
FT_LOGO_W = Inches(1.410);  FT_LOGO_H = Inches(0.287)
FT_NUM_L  = Inches(6.5);    FT_NUM_T  = Inches(7.178)
FT_NUM_W  = Inches(0.6);    FT_NUM_H  = Inches(0.32)

CL_LOGO_L = Inches(3.722); CL_LOGO_T = Inches(3.150)
CL_LOGO_W = Inches(5.890); CL_LOGO_H = Inches(1.201)

TC_LEFT_L  = Inches(0.406); TC_LEFT_W  = Inches(6.023)
TC_RIGHT_L = Inches(6.902); TC_RIGHT_W = Inches(6.023)
TC_AREA_T  = Inches(1.545); TC_AREA_H  = Inches(5.276)

DIVIDER_Y = Inches(1.38)


# ── Primitives ──────────────────────────────────────────────────────────────
def _rect(sl, l, t, w, h, fill, lc=None, lpt=0):
    s = sl.shapes.add_shape(1, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if lc and lpt: s.line.color.rgb = lc; s.line.width = Pt(lpt)
    else: s.line.fill.background()
    return s

def _rrect(sl, l, t, w, h, fill, lc=None, lpt=0, rad=0.12):
    s = sl.shapes.add_shape(5, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if lc and lpt: s.line.color.rgb = lc; s.line.width = Pt(lpt)
    else: s.line.fill.background()
    try:
        if len(s.adjustments) > 0: s.adjustments[0] = rad
    except Exception: pass
    return s

def _oval(sl, l, t, w, h, fill=None, lc=None, lpt=0):
    s = sl.shapes.add_shape(9, l, t, w, h)
    if fill: s.fill.solid(); s.fill.fore_color.rgb = fill
    else: s.fill.background()
    if lc and lpt: s.line.color.rgb = lc; s.line.width = Pt(lpt)
    else: s.line.fill.background()
    return s

def _txt(sl, text, l, t, w, h, font="Calibri", size=12, bold=False,
         color=None, align=PP_ALIGN.LEFT, italic=False, wrap=True):
    if color is None: color = C_TEXT
    tb = sl.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.name = font; r.font.size = Pt(size)
    r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = color
    return tb

def _bullets(sl, items, l, t, w, h, theme, size=13):
    if not items: return
    tc = C_TEXT if theme == "light" else C_WHITE
    tb = sl.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for b in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_before = Pt(7); p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = "\u25b8  " + b
        r.font.name = "Calibri"; r.font.size = Pt(size); r.font.color.rgb = tc

def _arrow(sl, x1, y1, x2, y2, color=None, w=1.5):
    if color is None: color = C_ACCENT
    c = sl.shapes.add_connector(2, x1, y1, x2, y2)
    c.line.color.rgb = color; c.line.width = Pt(w)

def _col(name):
    return COLORS.get(str(name).lower(), C_MID)

def _logo(sl, theme, l, t, w, h):
    byt = _LW if theme == "dark" else _LB
    if byt is None: return
    try: sl.shapes.add_picture(io.BytesIO(byt), l, t, width=w, height=h)
    except Exception: pass


# ── Shared structural helpers ───────────────────────────────────────────────
def footer(sl, theme, num=None, total=None):
    """Footer: copyright left, slide number centre, logo right."""
    cc = C_MUTED if theme == "light" else RGBColor(0x88, 0x9A, 0xB8)
    _txt(sl, "\u00a9 2026 NTT DATA Business Solutions",
         Inches(0.406), FT_T + Inches(0.04), Inches(5.5), Inches(0.28),
         size=8, color=cc)
    if num is not None and total is not None:
        nc = C_MUTED if theme == "light" else RGBColor(0x77, 0x88, 0xAA)
        _txt(sl, f"{num} / {total}", FT_NUM_L, FT_NUM_T, FT_NUM_W, FT_NUM_H,
             size=8, color=nc, align=PP_ALIGN.CENTER)
    _logo(sl, theme, FT_LOGO_L, FT_LOGO_T, FT_LOGO_W, FT_LOGO_H)

def divider(sl, y, theme):
    col = C_MGRAY if theme == "light" else RGBColor(0x33, 0x4A, 0x6E)
    _rect(sl, Inches(0.406), y, SW - Inches(0.812), Pt(1), col)

def pill(sl, label, theme, y=None):
    if not label: return
    if y is None: y = Inches(1.24)
    pw = max(Inches(1.4), len(label) * Inches(0.105) + Inches(0.5))
    _rrect(sl, Inches(0.406), y, pw, Inches(0.26), C_BLUE, rad=0.5)
    _txt(sl, label.upper(), Inches(0.46), y + Inches(0.03),
         pw - Inches(0.1), Inches(0.2),
         size=8, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

def slide_title(sl, title, theme, size=None):
    tc = C_TEXT if theme == "light" else C_WHITE
    if size is None:
        size = 26 if len(title) > 55 else (28 if len(title) > 40 else 30)
    _txt(sl, title, CT_TTL_L, CT_TTL_T, CT_TTL_W, CT_TTL_H,
         font="Calibri", size=size, bold=True, color=tc)

def innovation_curve(sl):
    """Draw NTT DATA innovation curve circle arcs (cover right side)."""
    cr = Inches(8.0)
    _oval(sl, CVR_CURVE_L - Inches(1.5), -int(cr * 0.05),
          cr, cr, lc=RGBColor(0x00, 0x60, 0xB0), lpt=1.2)
    cr2 = Inches(5.5)
    _oval(sl, CVR_CURVE_L - Inches(0.5), Inches(0.8),
          cr2, cr2, lc=C_ACCENT, lpt=0.8)
    cr3 = Inches(3.0)
    _oval(sl, SW - Inches(3.8), Inches(0.5),
          cr3, cr3, lc=RGBColor(0x00, 0x80, 0xCC), lpt=0.6)

def notes(slide, text):
    if text:
        try: slide.notes_slide.notes_text_frame.text = text
        except Exception: pass
