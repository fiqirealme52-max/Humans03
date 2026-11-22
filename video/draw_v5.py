#!/usr/bin/env python3
"""Draw v5: CONTINUOUS LIVE DRAWING for the Bring the Humans 03 TikTok ad.

v5 concept (user: "isi vidio lu cuma foto" + "liat contoh top 1 tuh"):
the #1 entry (tejotrejo, 7,735 views) is ONE continuous line-art animation —
a city DRAWN line by line over 18 s. No finished picture is ever held still.
v4/v4-motion failed that test: finished pictures + a slow zoom = still a
finished picture, and TikTok's classifier read it as a photo post (twice).

v5 keeps v4's approved story ("cerita, bukan iklan": 4 beats, cream paper,
same TTS voiceover, same badge from frame 1, same tiny last-frame line) but
re-draws EVERYTHING live, stroke by stroke, at 24 fps:
  - ghost disc: circle sweeps in, fill fades, ghost body sketched line by line
  - text: written character by character, as if by hand
  - cards: outline sweeps around the perimeter, fill fades in
  - score bars: GROW from zero; AGEN GUE's bar fills last
  - a small ink pen-tip dot rides the active stroke
At NO point does a finished picture sit still: every 1-second window has
visible creation (new strokes, growing bars, written text).

NO finished seg-v4-*.png rasters are reused as the picture (that was the
v4-motion mistake). Visuals are re-drawn from the v4 layout blueprint only.
Voiceover + bed are v4's (allowed). Badge is the press-pack pill, overlaid
in the final ffmpeg pass (frame 1 to end), as in v4.

HARD BANS (TikTok Frauds and Scams — v1 died on this): NO money words
anywhere: duit, dibayar, USDC, $, menang, dapet, cuan, kaya, penghasilan.
No prize amounts, no board-dark.png, no "daftar" commands, no links on
screen. All lists drawn from scratch.

Usage: python3 draw_v5.py --seg N   (N = 1..4)
Renders segment N's frames to /tmp/v5frames/segN/frame-%04d.png plus
segN-final.png (the fully-drawn end state, used for crossfades).
"""
import argparse
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 24
OUT = "/tmp/v5frames"
PRESS = "/home/hatch/workspace/makefun/Humans03/press"

CREAM = (245, 239, 230)
CREAM_DK = (236, 226, 210)
SAGE = (222, 232, 220)
INK = (34, 32, 28)
GREY = (120, 115, 105)
TEAL = (46, 125, 107)
TEAL_LT = (214, 233, 228)
TERRA = (196, 110, 80)
GREEN_DOT = (52, 168, 83)
CARD = (255, 255, 255)
CARD_LINE = (210, 200, 185)
NAVY = (32, 28, 38)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (254, 189, 46)
MAGENTA = (205, 32, 105)

DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
JBMONO = f"{PRESS}/JetBrainsMono-Bold.ttf"

# segment durations (seconds) — identical to v4 (voice + 1.0 s breathing room)
DURS = {1: 3.93, 2: 6.69, 3: 4.36, 4: 3.21}


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_w, min_size=40):
    size = start_size
    while size > min_size:
        fnt = ImageFont.truetype(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return ImageFont.truetype(path, min_size)


def clamp01(x):
    return 0.0 if x <= 0 else 1.0 if x >= 1 else x


def prog(t, t0, t1):
    """Linear 0..1 progress of time t inside window [t0, t1]."""
    return clamp01((t - t0) / (t1 - t0)) if t1 > t0 else (1.0 if t >= t0 else 0.0)


def smooth(p):
    return p * p * (3 - 2 * p)


def star4(draw, cx, cy, r, fill):
    k = 0.28
    pts = [
        (cx, cy - r), (cx + r * k, cy - r * k), (cx + r, cy),
        (cx + r * k, cy + r * k), (cx, cy + r), (cx - r * k, cy + r * k),
        (cx - r, cy), (cx - r * k, cy - r * k),
    ]
    draw.polygon(pts, fill=fill)


def partial_polyline(draw, pts, progress, fill, width):
    """Draw the first `progress` fraction of a polyline. Returns end point."""
    if progress <= 0 or len(pts) < 2:
        return None
    segs = []
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append(L)
        total += L
    if total <= 0:
        return pts[0]
    target = total * progress
    acc = 0.0
    drawn = [pts[0]]
    end = pts[-1]
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if acc + L >= target:
            f = (target - acc) / L if L > 0 else 0
            end = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            drawn.append(end)
            break
        drawn.append(b)
        acc += L
    draw.line(drawn, fill=fill, width=width, joint="curve")
    return end


def arc_sweep(draw, cx, cy, r, progress, fill, width):
    """Sweep a circle outline clockwise from the top. Returns pen position."""
    if progress <= 0:
        return None
    start, sweep = -90.0, 360.0 * progress
    draw.arc([cx - r, cy - r, cx + r, cy + r], start, start + sweep,
             fill=fill, width=width)
    a = math.radians(start + sweep)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def pen_tip(draw, xy, r=9, fill=INK):
    if xy is None:
        return
    x, y = xy
    draw.ellipse([x - r, y - r, x + r, y + r], fill=fill + (255,))


def write_text(draw, xy, text, fnt, fill, progress, anchor="la"):
    """Reveal text character by character. Returns chars shown."""
    if progress <= 0:
        return 0
    n = min(len(text), int(progress * len(text)) + 1)
    draw.text(xy, text[:n], font=fnt, fill=fill, anchor=anchor)
    return n


def composite_layer(base, draw_fn, alpha):
    """Draw draw_fn onto a transparent layer, composite at alpha."""
    if alpha <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, layer)
    if alpha < 1.0:
        a = layer.split()[3].point(lambda v: int(v * alpha))
        layer.putalpha(a)
    base.alpha_composite(layer)


def rrect_perimeter(x0, y0, x1, y1, r):
    """Perimeter points of a rounded rect, clockwise from top-left corner."""
    def arc_pts(cx, cy, a0, a1):
        n = max(2, int(abs(a1 - a0) / 6))
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
                for i in range(n + 1)]
    pts = []
    pts += arc_pts(x0 + r, y0 + r, 180, 270)
    pts += arc_pts(x1 - r, y0 + r, 270, 360)
    pts += arc_pts(x1 - r, y1 - r, 0, 90)
    pts += arc_pts(x0 + r, y1 - r, 90, 180)
    return pts


def ghost_points(cx, cy, s):
    """Hand-sketched ghost outline: dome + sides + wavy bottom. Closed path."""
    rx, ry = 150 * s, 150 * s
    dome_cy = cy - 40 * s
    pts = []
    for a in range(180, 361, 6):
        rad = math.radians(a)
        pts.append((cx + rx * math.cos(rad), dome_cy + ry * math.sin(rad)))
    pts.append((cx + rx, cy + 140 * s))
    for bx, by in [(90, 138), (60, 110), (30, 138), (0, 110),
                   (-30, 138), (-60, 110), (-90, 138), (-120, 110)]:
        pts.append((cx + bx * s, cy + by * s))
    pts.append((cx - rx, dome_cy))
    return pts


def draw_ghost(d, base, cx, cy, s, t, t_outline0, t_outline1,
               t_fill0, t_fill1, t_eyes, t_star0, t_star1, outline=INK):
    """Sketch a ghost: outline -> white fill -> sparkle eyes -> hand star.
    `outline` is the stroke color: WHITE when the ghost sits on the dark
    disc (ink-on-navy is invisible), INK on plain cream."""
    pts = ghost_points(cx, cy, s)
    w = max(4, int(10 * s))
    p = smooth(prog(t, t_outline0, t_outline1))
    end = partial_polyline(d, pts + [pts[0]], p, outline + (255,), w)
    if 0 < p < 1:
        pen_tip(d, end, fill=outline)
    composite_layer(base,
                    lambda ld, _: ld.polygon(pts, fill=WHITE + (255,)),
                    prog(t, t_fill0, t_fill1))
    # eyes (two dark sparkles) pop in, staggered
    for i, ex in enumerate((cx - 55 * s, cx + 55 * s)):
        if t >= t_eyes + i * 0.10:
            star4(d, ex, cy - 20 * s, 20 * s, NAVY + (255,))
    # small star held in hand: circle sweep + magenta star
    if t >= t_star0:
        scx, scy, sr = cx + 150 * s, cy + 60 * s, 36 * s
        sp = smooth(prog(t, t_star0, t_star1))
        arc_sweep(d, scx, scy, sr, sp, MAGENTA + (255,), max(3, int(5 * s)))
        if t >= t_star1:
            star4(d, scx, scy, 20 * s, MAGENTA + (255,))


def draw_disc_ghost(d, base, cx, cy, r, s, t, t_disc0, t_disc1,
                    t_dfill0, t_dfill1, t_g0, t_g1, t_gfill0, t_gfill1,
                    t_eyes, t_star0, t_star1):
    """Dark disc (sweep + fill) with a sketched ghost inside."""
    p = smooth(prog(t, t_disc0, t_disc1))
    end = arc_sweep(d, cx, cy, r, p, NAVY + (255,), 10)
    if 0 < p < 1:
        pen_tip(d, end)
    composite_layer(base,
                    lambda ld, _: ld.ellipse([cx - r, cy - r, cx + r, cy + r],
                                             fill=NAVY + (255,)),
                    prog(t, t_dfill0, t_dfill1))
    draw_ghost(d, base, cx, cy + 10 * s, s, t, t_g0, t_g1,
               t_gfill0, t_gfill1, t_eyes, t_star0, t_star1, outline=WHITE)


def base_frame():
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(base)
    d.ellipse([140 - 200, 240 - 200, 140 + 200, 240 + 200], fill=CREAM_DK + (255,))
    d.ellipse([960 - 260, 1700 - 260, 960 + 260, 1700 + 260], fill=SAGE + (255,))
    d.ellipse([980 - 130, 420 - 130, 980 + 130, 420 + 130], fill=SAGE + (255,))
    return base, d


# ---------------------------------------------------------------- seg 1: HOOK
def seg1(base, d, t):
    draw_disc_ghost(d, base, 540, 720, 260, 1.0, t,
                    0.00, 0.70, 0.70, 1.05,      # disc sweep / fill
                    1.05, 2.05, 2.05, 2.35,      # ghost outline / fill
                    2.35, 2.55, 2.80)            # eyes / hand star
    f1 = fit_font(d, "AI gue hari ini sibuk banget.", DEJAVU_B, 72, 940)
    write_text(d, (540, 1150), "AI gue hari ini", f1, INK + (255,),
               prog(t, 0.50, 1.90), anchor="ma")
    write_text(d, (540, 1260), "sibuk banget.", f1, INK + (255,),
               prog(t, 1.90, 3.00), anchor="ma")
    squig = [(380, 1390), (470, 1400), (560, 1388), (650, 1400), (700, 1392)]
    p = smooth(prog(t, 3.00, 3.30))
    end = partial_polyline(d, squig, p, TERRA + (255,), 8)
    if 0 < p < 1:
        pen_tip(d, end)
    for i, (sx, sy, sr, col) in enumerate(
            [(170, 900, 26, TERRA), (920, 1020, 20, TEAL), (880, 1480, 18, TERRA)]):
        if t >= 3.30 + i * 0.10:
            star4(d, sx, sy, sr, col + (255,))


# ---------------------------------------------------------------- seg 2: WHAT
def seg2(base, d, t):
    f_t = fit_font(d, "Dia ikut kompetisi", DEJAVU_B, 66, 900)
    write_text(d, (90, 480), "Dia ikut kompetisi", f_t, INK + (255,),
               prog(t, 0.0, 1.1))
    write_text(d, (90, 570), "di make.fun.", f_t, INK + (255,),
               prog(t, 1.1, 1.8))
    card = rrect_perimeter(70, 720, 1010, 1320, 28)
    p = smooth(prog(t, 1.5, 2.5))
    end = partial_polyline(d, card + [card[0]], p, CARD_LINE + (255,), 5)
    if 0 < p < 1:
        pen_tip(d, end)
    composite_layer(base,
                    lambda ld, _: ld.rounded_rectangle(
                        [70, 720, 1010, 1320], radius=28, fill=CARD + (255,)),
                    prog(t, 2.5, 2.8))
    # Each item: dot drawn as a circle sweep -> bold text written ->
    # underline swept under the text. Three visible strokes per item, so
    # no 1-second window is ever just a few thin characters.
    items = [
        ("bikin game GTA 6", TEAL, 2.80, 2.92, 3.67, 3.92),
        ("bikin radar token", TERRA, 3.92, 4.04, 4.79, 5.04),
        ("bikin chart Roblox", (196, 150, 40), 5.04, 5.16, 5.91, 6.16),
    ]
    f_c = font(DEJAVU_B, 50)
    y = 790
    for text, dot, t_dot0, t_dot1, t_w1, t_u1 in items:
        dp = smooth(prog(t, t_dot0, t_dot1))
        arc_sweep(d, 136, y + 30, 16, dp, dot + (255,), 5)
        if t >= t_dot1:
            d.ellipse([120, y + 14, 152, y + 46], fill=dot + (255,))
        wp = prog(t, t_dot1, t_w1)
        tw = d.textlength(text, font=f_c)
        if wp > 0:
            # highlight band sweeps under the text as it is written
            bx1 = 180 + tw * wp
            if bx1 - 180 >= 28:
                d.rounded_rectangle([180, y - 4, bx1, y + 56],
                                    radius=12, fill=TEAL_LT + (255,))
            else:
                d.rectangle([180, y - 4, bx1, y + 56], fill=TEAL_LT + (255,))
        write_text(d, (180, y), text, f_c, INK + (255,), wp)
        up = smooth(prog(t, t_w1, t_u1))
        u_pts = [(180, y + 62), (180 + tw * 0.5, y + 66), (180 + tw, y + 62)]
        end = partial_polyline(d, u_pts, up, dot + (255,), 5)
        if 0 < up < 1:
            pen_tip(d, end)
        y += 150
    # small ghost peeking bottom-right, sketched (bigger than v4's)
    draw_ghost(d, base, 920, 1500, 0.58, t, 6.16, 6.45, 6.45, 6.58,
               6.58, 6.58, 6.68)


# ---------------------------------------------------------------- seg 3: LIVE
def seg3(base, d, t):
    f_t = fit_font(d, "Papan skornya live,", DEJAVU_B, 66, 900)
    write_text(d, (90, 480), "Papan skornya live,", f_t, INK + (255,),
               prog(t, 0.0, 1.0))
    write_text(d, (90, 570), "agen lain juga main.", f_t, INK + (255,),
               prog(t, 1.0, 1.8))
    card = rrect_perimeter(70, 700, 1010, 1440, 28)
    p = smooth(prog(t, 1.5, 2.2))
    end = partial_polyline(d, card + [card[0]], p, CARD_LINE + (255,), 5)
    if 0 < p < 1:
        pen_tip(d, end)
    composite_layer(base,
                    lambda ld, _: ld.rounded_rectangle(
                        [70, 700, 1010, 1440], radius=28, fill=CARD + (255,)),
                    prog(t, 2.2, 2.4))
    if t >= 2.40:
        d.ellipse([120, 758, 148, 786], fill=GREEN_DOT + (255,))
    write_text(d, (168, 744), "live", font(DEJAVU, 42), GREY + (255,),
               prog(t, 2.45, 2.60))
    write_text(d, (820, 744), "skor", font(DEJAVU, 42), GREY + (255,),
               prog(t, 2.60, 2.75))
    f_m = font(JBMONO, 46)
    rows = [
        ("1", "AGEN #03", 620, (200, 196, 188), False),
        ("2", "AGEN GUE", 500, TEAL, True),
        ("3", "AGEN #18", 420, (200, 196, 188), False),
        ("4", "AGEN #27", 320, (200, 196, 188), False),
        ("5", "AGEN #41", 230, (200, 196, 188), False),
    ]
    y = 850
    for i, (rank, name, bar_w, color, hot) in enumerate(rows):
        t0 = 2.80 + i * 0.28
        write_text(d, (115, y), rank, f_m, INK + (255,), prog(t, t0, t0 + 0.10))
        write_text(d, (190, y), name, f_m, INK + (255,), prog(t, t0, t0 + 0.12))
        bw = bar_w * smooth(prog(t, t0 + 0.08, t0 + 0.28))
        if bw >= 2:
            if bw >= 12:
                d.rounded_rectangle([190, y + 62, 190 + bw, y + 92], radius=15,
                                    fill=color + (255,))
            else:
                # too narrow for a rounded rect (PIL needs x1-r-1 >= x0+r+1)
                d.rectangle([190, y + 62, 190 + bw, y + 92], fill=color + (255,))
            if bw < bar_w:
                pen_tip(d, (190 + bw, y + 77), r=8)
        if hot and t >= t0 + 0.24:
            star4(d, 660, y + 24, 26, YELLOW + (255,))
        y += 112


# ---------------------------------------------------------------- seg 4: CLOSE
def seg4(base, d, t):
    draw_disc_ghost(d, base, 540, 820, 240, 0.92, t,
                    0.00, 0.60, 0.60, 0.90,      # disc sweep / fill
                    0.90, 1.70, 1.70, 1.95,      # ghost outline / fill
                    1.95, 2.10, 2.30)            # eyes / hand star
    f_c = fit_font(d, "Gue mah cuma nontonin aja.", DEJAVU_B, 72, 940)
    write_text(d, (540, 1230), "Gue mah cuma", f_c, INK + (255,),
               prog(t, 0.40, 1.50), anchor="ma")
    write_text(d, (540, 1340), "nontonin aja.", f_c, INK + (255,),
               prog(t, 1.50, 2.40), anchor="ma")
    for i, (sx, sy, sr, col) in enumerate(
            [(160, 620, 24, TERRA), (930, 660, 20, TEAL),
             (150, 1560, 20, TEAL), (940, 1620, 24, TERRA)]):
        if t >= 2.40 + i * 0.10:
            star4(d, sx, sy, sr, col + (255,))
    composite_layer(
        base,
        lambda ld, _: ld.text((540, 1700), "make.fun · kode: vfa7ye18",
                              font=font(DEJAVU, 30), fill=GREY + (255,),
                              anchor="ma"),
        prog(t, 2.60, 2.95))


SEG_FNS = {1: seg1, 2: seg2, 3: seg3, 4: seg4}


def render_segment(seg):
    dur = DURS[seg]
    nframes = int(round(dur * FPS))
    outdir = f"{OUT}/seg{seg}"
    os.makedirs(outdir, exist_ok=True)
    fn = SEG_FNS[seg]
    for i in range(nframes):
        t = i / FPS
        base, d = base_frame()
        fn(base, d, t)
        base.convert("RGB").save(f"{outdir}/frame-{i:04d}.png")
    # fully-drawn end state (for crossfades)
    base, d = base_frame()
    fn(base, d, dur + 1.0)
    base.convert("RGB").save(f"{OUT}/seg{seg}-final.png")
    print(f"seg{seg}: {nframes} frames + final")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg", type=int, required=True, choices=[1, 2, 3, 4])
    args = ap.parse_args()
    render_segment(args.seg)
