"""crescens.one · the founder's own mark.
Three layers: crescens = Latin "growing"; the root of crescent (a waxing moon);
.one = the one. A moon on its way to full.
Palette and pose are independent of the 物理AI实验场 kit; the generator helpers are shared with brand.py."""
import math
from brand import face, face_file, svg, render, bez

# ---------------------------------------------------------------- palette (two grounds, same mark)
PAL_NIGHT = {  # default: a moon over the night sea
    "bg": "#0F1E33",      # 夜海 navy
    "moon": "#F2E4B8",    # 月光 moonlight
    "gold": "#E6B34A",    # 新月 gold (the dot, the reflection)
    "sea": "#3E97A0",     # 海青 sea teal
    "moss": "#9CCB8F",    # 苔 moss (the sprout)
    "ink": "#F2E4B8",     # text on this ground
    "sub": "#9CCB8F",
}
PAL_DAY = {   # light ground: a moon in a morning sky
    "bg": "#F5F1E8",      # 月白 paper
    "moon": "#E2A93B",    # 新月 gold
    "gold": "#E2A93B",
    "sea": "#2E7C86",     # 海青
    "moss": "#2E6B4F",    # 深林 forest green
    "ink": "#1E3B33",     # 深林 text
    "sub": "#2E7C86",
}


def _circ_x(c1, r1, c2, r2):
    """intersection points of two circles → (top, bottom) as (x, y)."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0))
    xm, ym = c1[0] + a * dx / d, c1[1] + a * dy / d
    p1 = (xm + h * dy / d, ym - h * dx / d); p2 = (xm - h * dy / d, ym + h * dx / d)
    return (p1, p2) if p1[1] < p2[1] else (p2, p1)


def crescent_path(c, R, d, r):
    """waxing crescent: disc (c,R) minus a disc shifted left by d with radius r. Lit side on the right."""
    c2 = (c[0] - d, c[1])
    top, bot = _circ_x(c, R, c2, r)
    # outer limb: the long way round, clockwise through the lit side; terminator: back up the short way
    return (f'M{top[0]:.1f} {top[1]:.1f}A{R:.1f} {R:.1f} 0 1 1 {bot[0]:.1f} {bot[1]:.1f}'
            f'A{r:.1f} {r:.1f} 0 0 0 {top[0]:.1f} {top[1]:.1f}Z')


def leaf(x, y, L, ang, w):
    """a leaf growing from (x,y), length L, pointing at angle ang (deg, 0 = up), half-width w."""
    return (f'<path d="M0 0Q{-w} {-L*0.55} 0 {-L}Q{w} {-L*0.55} 0 0Z" transform="translate({x},{y}) rotate({ang})"/>')


def mark(bg=None, pal=PAL_NIGHT, c=(400, 356), R=222, d=82, r=218, horizon=580, forest=True, sea=True, sprout=True, ring=True, sx=None):
    p = pal
    out = []
    if bg:
        out.append(f'<rect width="800" height="800" fill="{bg}"/>')
    # the moon still to come: a faint full disc (earthshine)
    if ring:
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{R}" fill="{p["moon"]}" fill-opacity="0.06" stroke="{p["moon"]}" stroke-opacity="0.30" stroke-width="5"/>')
    # the lit part: a waxing crescent
    out.append(f'<path d="{crescent_path(c, R, d, r)}" fill="{p["moon"]}"/>')
    # horizon: the sea
    if sea:
        x0, x1 = c[0] - 270, c[0] + 270
        out.append(f'<path d="M{x0} {horizon}H{x1}" stroke="{p["sea"]}" stroke-width="7" stroke-linecap="round"/>')
        # the moon's reflection under the crescent, breaking up on the water
        rx = c[0] + d * 0.55 + 40
        for i, (dy, w) in enumerate(((22, 64), (42, 46), (62, 30), (82, 16))):
            out.append(f'<path d="M{rx - w/2:.0f} {horizon + dy}h{w}" stroke="{p["gold"]}" stroke-width="7" stroke-linecap="round" opacity="{0.85 - i*0.15:.2f}"/>')
        out.append(f'<path d="M{x0 + 10} {horizon + 52}q28 -16 56 0t56 0" fill="none" stroke="{p["sea"]}" stroke-width="6" stroke-linecap="round" opacity="0.7"/>')
        out.append(f'<path d="M{x0 + 70} {horizon + 92}q28 -16 56 0t56 0" fill="none" stroke="{p["sea"]}" stroke-width="6" stroke-linecap="round" opacity="0.45"/>')
    # a pine line on the far shore
    if forest:
        pines = [(c[0] - 232, 30), (c[0] - 206, 46), (c[0] - 178, 38), (c[0] - 154, 56), (c[0] - 128, 34)]
        for x, h in pines:
            w = h * 0.42
            out.append(f'<path d="M{x - w:.0f} {horizon}L{x} {horizon - h}L{x + w:.0f} {horizon}Z" fill="{p["sea"]}" opacity="0.85"/>')
    # the one: a seedling growing inside the moon
    if sprout:
        sx = sx if sx is not None else c[0] - 30
        out.append(f'<g fill="{p["moss"]}" stroke="none">'
                   f'<path d="M{sx} {horizon}C{sx} {horizon-50} {sx-8} {horizon-90} {sx+6} {horizon-150}" fill="none" stroke="{p["moss"]}" stroke-width="11" stroke-linecap="round"/>'
                   f'{leaf(sx-3, horizon-80, 118, -60, 32)}'
                   f'{leaf(sx+4, horizon-120, 100, 50, 27)}'
                   f'<circle cx="{sx+7}" cy="{horizon-156}" r="11"/>'
                   f'</g>')
    return "\n".join(out)


MARK_BBOX = (135, 162, 665, 680)


def wordmark(x, y, size, pal=PAL_NIGHT, moon_o=True):
    """crescens.one — lowercase serif; the o of one is the moon. Returns (svg, bbox)."""
    p = pal
    f = face("serif-semibold")
    parts = []
    d1, b1, adv1 = f.path("crescens", size, x, y)
    parts.append(f'<path d="{d1}" fill="{p["ink"]}"/>')
    cx = x + adv1
    d2, b2, adv2 = f.path(".", size, cx, y)
    parts.append(f'<path d="{d2}" fill="{p["gold"]}"/>')
    cx += adv2
    if moon_o:
        # measure an o to size the moon glyph
        do, bo, advo = f.path("o", size, cx, y)
        ox, oy = (bo[0] + bo[2]) / 2, (bo[1] + bo[3]) / 2
        Ro = (bo[3] - bo[1]) / 2 * 1.04
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{Ro:.1f}" fill="none" stroke="{p["ink"]}" stroke-opacity="0.35" stroke-width="{max(1.5, size*0.022):.1f}"/>')
        parts.append(f'<path d="{crescent_path((ox, oy), Ro, Ro*0.48, Ro*0.98)}" fill="{p["gold"]}"/>')
        cx += advo
        d3, b3, adv3 = f.path("ne", size, cx, y)
        parts.append(f'<path d="{d3}" fill="{p["ink"]}"/>')
        bb = (b1[0], min(b1[1], b3[1]), b3[2], max(b1[3], b3[3]))
    else:
        d3, b3, adv3 = f.path("one", size, cx, y)
        parts.append(f'<path d="{d3}" fill="{p["ink"]}"/>')
        bb = (b1[0], min(b1[1], b3[1]), b3[2], max(b1[3], b3[3]))
    return "".join(parts), bb


TAGLINE = {
    # one idea, two voices: 花未全开月未圆（蔡襄句，曾国藩"求阙"之道取意于此）— the state just before fullness holds the most
    "zh": ("生长 · 新月 · 唯一", "花未全开月未圆"),
    "en": ("growing · crescent · one", "the bud not yet open, the moon not yet full"),
}


def text_block(x, y, wm, sub, tag, pal=PAL_NIGHT, lang="zh", gap1=None, gap2=None):
    """wordmark / three-layer index / the line. lang picks the voice; the wordmark is Latin in both. Returns (svg, bbox)."""
    p = pal
    gap1 = gap1 or wm * 0.34; gap2 = gap2 or wm * 0.30
    sub_txt, tag_txt = TAGLINE[lang]
    out = []
    w, bb = wordmark(x, y, wm, pal=pal)
    out.append(w)
    y2 = y + gap1 + sub
    if lang == "zh":
        d, b2, _ = face("serif-medium").path(sub_txt, sub, x + wm * 0.02, y2, tracking=sub * 0.06)
    else:
        d, b2, _ = face("serif-medium").path(sub_txt, sub, x + wm * 0.02, y2, tracking=sub * 0.10)
    out.append(f'<path d="{d}" fill="{p["sub"]}"/>')
    y3 = y2 + gap2 + tag
    if lang == "zh":
        d, b3, _ = face("serif-regular").path(tag_txt, tag, x + wm * 0.02, y3, tracking=tag * 0.12)
    else:
        d, b3, _ = face("serif-regular").path(tag_txt, tag * 0.92, x + wm * 0.02, y3)
    out.append(f'<path d="{d}" fill="{p["ink"]}" fill-opacity="0.82"/>')
    return "".join(out), (min(bb[0], b2[0], b3[0]), bb[1], max(bb[2], b2[2], b3[2]), b3[3])


def lockup(cx, cy, s, wm, sub, zh, gap, pal=PAL_NIGHT, lang="zh"):
    m = mark(pal=pal)
    bx0, by0, bx1, by1 = MARK_BBOX
    mw, mh = (bx1 - bx0) * s, (by1 - by0) * s
    _, tb = text_block(0, 0, wm, sub, zh, pal=pal, lang=lang)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    total = mw + gap + tw
    mx = cx - total / 2; my = cy - mh / 2
    tx = mx + mw + gap - tb[0]; ty = cy - th / 2 - tb[1]
    g = f'<g transform="translate({mx - bx0*s:.2f},{my - by0*s:.2f}) scale({s})">{m}</g>'
    t, _ = text_block(tx, ty, wm, sub, zh, pal=pal, lang=lang)
    return g + "\n" + t, (mx, my, mx + total, my + max(mh, th)), my + (580 - by0) * s


def sea_band(w, y, pal=PAL_NIGHT, step=48, amp=5, opacity=0.18):
    """a quiet wave line across the full width, standing in for the ruler band."""
    d = [f'M0 {y}']
    x = 0
    while x < w:
        d.append(f'q{step/2} {-amp*2} {step} 0'); x += step
    return f'<path d="{" ".join(d)}" fill="none" stroke="{pal["sea"]}" stroke-width="3" opacity="{opacity}"/>'


def banner_youtube(pal=PAL_NIGHT, lang="zh"):
    W, H = 2560, 1440
    body = [f'<rect width="{W}" height="{H}" fill="{pal["bg"]}"/>']
    lk, bb, fy = lockup(1280, 720, 0.56, 118, 34, 40, 64, pal=pal, lang=lang)
    body.append(sea_band(W, fy, pal)); body.append(lk)
    return svg(W, H, "\n".join(body)), bb


def header_x(pal=PAL_NIGHT, lang="zh"):
    W, H = 1500, 500
    body = [f'<rect width="{W}" height="{H}" fill="{pal["bg"]}"/>']
    lk, bb, fy = lockup(812, 226, 0.36, 76, 22, 26, 42, pal=pal, lang=lang)
    body.append(sea_band(W, fy, pal, step=44, amp=4)); body.append(lk)
    return svg(W, H, "\n".join(body)), bb
