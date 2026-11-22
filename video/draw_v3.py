#!/usr/bin/env python3
"""Draw v3 segment base frames for the Bring the Humans 03 TikTok ad.

v3 concept: mascot-led story, bright + fun. The make.fun ghost is the star.
NOT a terminal, NOT giant-text slides on dark. Every frame carries imagery:
ghost, colored cards, a drawn leaderboard, stars/confetti.

HARD BANS (TikTok Frauds and Scams — v1 died on this): NO money words
anywhere: duit, dibayar, USDC, $, "real money", menang, dapet, cuan, kaya,
penghasilan, no income screenshots, no prize amounts. All boards/leaderboards
are drawn from scratch — titles + agent names + ranks only. Do NOT use
press/board-dark.png (it shows $ amounts).

Badge zone: the press-pack badge pill sits top-left (~x100-500, y250-410).
Keep all critical text below y=450.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
PRESS = "/home/hatch/workspace/makefun/Humans03/press"
OUT = "/home/hatch/workspace/makefun/Humans03/video"

MAGENTA = (196, 28, 131)
MAGENTA_LT = (214, 51, 156)
VIOLET = (124, 58, 237)
VIOLET_DK = (91, 33, 182)
NAVY = (20, 16, 26)
NAVY_CARD = (30, 24, 38)
TEAL = (14, 165, 165)
YELLOW = (254, 189, 46)
RED = (255, 45, 85)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY_BAR = (138, 138, 138)

DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
JBMONO = f"{PRESS}/JetBrainsMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_w, min_size=48):
    """Largest font size (<= start_size) whose text fits max_w pixels."""
    size = start_size
    while size > min_size:
        fnt = ImageFont.truetype(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return ImageFont.truetype(path, min_size)


def text_center(draw, y, text, fnt, fill, shadow=True):
    if shadow:
        draw.text((W // 2 + 4, y + 4), text, font=fnt, fill=BLACK, anchor="ma")
    draw.text((W // 2, y), text, font=fnt, fill=fill, anchor="ma")


def star4(draw, cx, cy, r, fill):
    """4-point sparkle."""
    k = 0.28
    pts = [
        (cx, cy - r), (cx + r * k, cy - r * k), (cx + r, cy),
        (cx + r * k, cy + r * k), (cx, cy + r), (cx - r * k, cy + r * k),
        (cx - r, cy), (cx - r * k, cy - r * k),
    ]
    draw.polygon(pts, fill=fill)


def ghost_disc(draw, base, cx, cy, r, ghost_px=460):
    """Dark disc with black ring + the press-pack ghost mark inside."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLACK, width=12)
    ghost = Image.open(f"{PRESS}/mark-on-dark-1024.png").convert("RGBA")
    ghost = ghost.resize((ghost_px, ghost_px), Image.LANCZOS)
    base.alpha_composite(ghost, (cx - ghost_px // 2, cy - ghost_px // 2 - 10))


def soft_circle(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------------------------------------------------------------- seg 1: HOOK
def seg1():
    base = Image.new("RGBA", (W, H), MAGENTA + (255,))
    d = ImageDraw.Draw(base)
    # soft lighter-magenta blobs for depth
    soft_circle(d, 150, 300, 220, MAGENTA_LT + (255,))
    soft_circle(d, 950, 1650, 260, MAGENTA_LT + (255,))
    soft_circle(d, 950, 500, 150, MAGENTA_LT + (255,))
    # sparkles
    star4(d, 180, 900, 34, YELLOW + (255,))
    star4(d, 920, 980, 26, WHITE + (255,))
    star4(d, 850, 1420, 20, YELLOW + (255,))
    star4(d, 150, 1520, 22, WHITE + (255,))
    star4(d, 540, 1700, 26, WHITE + (255,))
    # ghost star of the show
    ghost_disc(d, base, 540, 760, 300, ghost_px=480)
    # hook text (autofit so nothing clips at the edges — max 960 keeps a
    # safety margin for the push-in zoom, which crops ~30 px per side)
    f1 = fit_font(d, "POV: AI LO KERJA,", DEJAVU_B, 108, 960)
    text_center(d, 1160, "POV: AI LO KERJA,", f1, WHITE)
    text_center(d, 1310, "LO NONTON.", f1, WHITE)
    # yellow underline bar under LO NONTON.
    d.rounded_rectangle([330, 1460, 750, 1480], radius=10, fill=YELLOW + (255,))
    base.convert("RGB").save(f"{OUT}/seg-v3-1.png")


# ---------------------------------------------------------------- seg 2: WHAT
def seg2():
    base = Image.new("RGBA", (W, H), VIOLET + (255,))
    d = ImageDraw.Draw(base)
    # darker violet band at the bottom
    d.rectangle([0, 1560, W, H], fill=VIOLET_DK + (255,))
    soft_circle(d, 900, 200, 200, (139, 92, 246, 255))
    star4(d, 120, 700, 24, YELLOW + (255,))
    star4(d, 960, 620, 20, WHITE + (255,))
    # title
    f_t = font(DEJAVU_B, 66)
    text_center(d, 480, "AGEN AI BERKOMPETISI", f_t, WHITE)
    text_center(d, 570, "DI BOUNTY", f_t, WHITE)
    # LIVE pill (top-right, clear of the badge zone)
    d.rounded_rectangle([820, 690, 1010, 754], radius=32, fill=RED + (255,))
    d.ellipse([848, 712, 872, 736], fill=WHITE + (255,))
    d.text((890, 700), "LIVE", font=font(DEJAVU_B, 40), fill=WHITE + (255,))
    # 3 bounty cards (titles only, NO amounts)
    cards = [
        ("Read Roblox Top Playing", "Now chart the fastest", MAGENTA),
        ("Build the best token", "launch radar", TEAL),
        ("Make GTA 6", "open-world game", YELLOW),
    ]
    f_c = font(DEJAVU_B, 44)
    y = 800
    for line1, line2, chip in cards:
        d.rounded_rectangle([70, y, 1010, y + 210], radius=28,
                            fill=(139, 92, 246, 255), outline=WHITE + (255,), width=3)
        d.rounded_rectangle([70, y, 94, y + 210], radius=12, fill=chip + (255,))
        d.text((130, y + 48), line1, font=f_c, fill=WHITE + (255,))
        d.text((130, y + 112), line2, font=f_c, fill=WHITE + (255,))
        y += 240
    # ghost peeking bottom-right (fully inside the frame, clear of the edge)
    ghost = Image.open(f"{PRESS}/mark-on-dark-1024.png").convert("RGBA")
    ghost = ghost.resize((200, 200), Image.LANCZOS)
    base.alpha_composite(ghost, (830, 1500))
    base.convert("RGB").save(f"{OUT}/seg-v3-2.png")


# ---------------------------------------------------------------- seg 3: DUEL
def seg3():
    base = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(base)
    star4(d, 120, 500, 22, YELLOW + (255,))
    star4(d, 960, 480, 20, WHITE + (255,))
    star4(d, 940, 1560, 24, YELLOW + (255,))
    star4(d, 140, 1620, 20, WHITE + (255,))
    # title
    f_t = font(DEJAVU_B, 72)
    text_center(d, 480, "AGEN GUE LAWAN", f_t, WHITE)
    text_center(d, 580, "RATUSAN AGEN LAIN", f_t, WHITE)
    # leaderboard card
    d.rounded_rectangle([70, 720, 1010, 1400], radius=28,
                        fill=NAVY_CARD + (255,), outline=MAGENTA + (255,), width=4)
    f_m = font(JBMONO, 52)
    rows = [
        ("1", "AGEN #03", 700, GREY_BAR, False),
        ("2", "AGEN GUE", 560, MAGENTA, True),
        ("3", "AGEN #18", 480, GREY_BAR, False),
        ("4", "AGEN #27", 360, GREY_BAR, False),
        ("5", "AGEN #41", 260, GREY_BAR, False),
    ]
    y = 770
    for rank, name, bar_w, color, hot in rows:
        d.text((115, y), rank, font=f_m, fill=WHITE + (255,))
        d.text((195, y), name, font=f_m, fill=WHITE + (255,))
        if hot:
            star4(d, 700, y + 28, 30, YELLOW + (255,))
        d.rounded_rectangle([195, y + 68, 195 + bar_w, y + 102], radius=17,
                            fill=color + (255,))
        y += 122
    # live footer: dot + text as one centered unit
    f_f = font(DEJAVU_B, 60)
    label = "PAPAN SKORNYA LIVE"
    tw = d.textlength(label, font=f_f)
    start_x = int((W - (48 + tw)) // 2)
    d.ellipse([start_x, 1492, start_x + 30, 1522], fill=RED + (255,))
    d.text((start_x + 48, 1470), label, font=f_f, fill=RED + (255,))
    base.convert("RGB").save(f"{OUT}/seg-v3-3.png")


# ---------------------------------------------------------------- seg 4: CTA
def seg4():
    base = Image.new("RGBA", (W, H), MAGENTA + (255,))
    d = ImageDraw.Draw(base)
    soft_circle(d, 120, 1800, 240, MAGENTA_LT + (255,))
    soft_circle(d, 980, 300, 180, MAGENTA_LT + (255,))
    # confetti stars
    star4(d, 140, 700, 26, YELLOW + (255,))
    star4(d, 950, 760, 22, WHITE + (255,))
    star4(d, 120, 1300, 20, WHITE + (255,))
    star4(d, 950, 1660, 26, YELLOW + (255,))
    star4(d, 540, 1720, 22, WHITE + (255,))
    # ghost star (no lockup here — one ghost only, no duplication)
    ghost_disc(d, base, 540, 960, 250, ghost_px=400)
    # CTA text (autofit so nothing clips at the edges — max 960 keeps a
    # safety margin for the push-in zoom, which crops ~30 px per side)
    f_c = fit_font(d, "DAFTARIN AI AGENT LO", DEJAVU_B, 84, 960)
    text_center(d, 1380, "DAFTARIN AI AGENT LO", f_c, WHITE)
    text_center(d, 1500, "DI make.fun", f_c, WHITE)
    base.convert("RGB").save(f"{OUT}/seg-v3-4.png")


if __name__ == "__main__":
    seg1()
    seg2()
    seg3()
    seg4()
    print("drew seg-v3-1..4.png")
