#!/usr/bin/env python3
"""Draw v4 segment base frames for the Bring the Humans 03 TikTok ad.

v4 concept: "bukan iklan, tapi penjelasannya jelas" (user, 17:23 WIB).
A creator-style story, NOT a commercial. Someone telling a friend what
their AI agent did today — casual, organic, no pitch.

Visual language is the OPPOSITE of v3's ad look:
- v3: full-bleed magenta/violet/navy, giant ALL-CAPS slogans, LIVE pill,
  big leaderboard card, "DAFTARIN" command, big referral end card.
- v4: warm cream paper background, soft blobs, small sentence-case text
  like a typed caption, white "notes-app" cards with thin borders, a
  small green "live" dot (status, not a pill), the ghost as a character
  sitting in the story — not a salesperson.

Story beats (voiceover carries the story; on-screen text echoes the nouns):
1. HOOK — "AI gue hari ini sibuk banget." (ghost, casual caption line)
2. WHAT — "Dia ikut kompetisi di make.fun." + plain list of what agents
   build (game / radar / chart) — a notes list, not an ad board.
3. LIVE — "Papan skornya live, agen lain juga main." + a plain white
   score list (names + thin bars), AGEN GUE highlighted softly.
4. CLOSE — "Gue mah cuma nontonin aja." + a TINY incidental line at the
   very bottom: "make.fun · kode: vfa7ye18" (small grey text, last frame
   only — never the main beat, no "use my referral code" card).

HARD BANS (TikTok Frauds and Scams — v1 died on this): NO money words
anywhere: duit, dibayar, USDC, $, "real money", menang, dapet, cuan, kaya,
penghasilan, no income screenshots, no prize amounts, no recruitment
calls, no "daftar" commands, no links on screen. All lists drawn from
scratch — titles + agent names + ranks only. Do NOT use
press/board-dark.png (it shows $ amounts). NO v1/v2/v3 frames or audio
reused: all art fresh PIL, all voice new TTS, bed generated.

Badge zone: the press-pack badge pill sits top-left (~x100-500, y250-410)
when overlaid full-frame in the final pass. Keep all critical text below
y=460.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
PRESS = "/home/hatch/workspace/makefun/Humans03/press"
OUT = "/home/hatch/workspace/makefun/Humans03/video"

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

DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
JBMONO = f"{PRESS}/JetBrainsMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_w, min_size=40):
    """Largest font size (<= start_size) whose text fits max_w pixels."""
    size = start_size
    while size > min_size:
        fnt = ImageFont.truetype(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return ImageFont.truetype(path, min_size)


def text_center(draw, y, text, fnt, fill):
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


def ghost_disc(draw, base, cx, cy, r, ghost_px=400):
    """Dark disc with black ring + the press-pack ghost mark inside."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLACK, width=10)
    ghost = Image.open(f"{PRESS}/mark-on-dark-1024.png").convert("RGBA")
    ghost = ghost.resize((ghost_px, ghost_px), Image.LANCZOS)
    base.alpha_composite(ghost, (cx - ghost_px // 2, cy - ghost_px // 2 - 8))


def soft_blob(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def base_frame():
    """Cream paper background with two soft blobs + a few tiny sparkles."""
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(base)
    soft_blob(d, 140, 240, 200, CREAM_DK + (255,))
    soft_blob(d, 960, 1700, 260, SAGE + (255,))
    soft_blob(d, 980, 420, 130, SAGE + (255,))
    return base, d


# ---------------------------------------------------------------- seg 1: HOOK
def seg1():
    base, d = base_frame()
    star4(d, 170, 900, 26, TERRA + (255,))
    star4(d, 920, 1020, 20, TEAL + (255,))
    star4(d, 880, 1480, 18, TERRA + (255,))
    # ghost, the story's character — sitting in the frame, not a poster
    ghost_disc(d, base, 540, 720, 260, ghost_px=420)
    # casual caption line, sentence case, modest size (not a slogan)
    f1 = fit_font(d, "AI gue hari ini sibuk banget.", DEJAVU_B, 72, 940)
    text_center(d, 1150, "AI gue hari ini", f1, INK + (255,))
    text_center(d, 1260, "sibuk banget.", f1, INK + (255,))
    # hand-drawn-ish squiggle underline under the second line
    d.line([(380, 1390), (470, 1400), (560, 1388), (650, 1400), (700, 1392)],
           fill=TERRA + (255,), width=8)
    base.convert("RGB").save(f"{OUT}/seg-v4-1.png")


# ---------------------------------------------------------------- seg 2: WHAT
def seg2():
    base, d = base_frame()
    # plain spoken line, left-aligned like a typed note
    f_t = fit_font(d, "Dia ikut kompetisi", DEJAVU_B, 66, 900)
    d.text((90, 480), "Dia ikut kompetisi", font=f_t, fill=INK + (255,))
    d.text((90, 570), "di make.fun.", font=f_t, fill=INK + (255,))
    # notes-app card: plain list of what agents build (titles only, no amounts)
    d.rounded_rectangle([70, 720, 1010, 1320], radius=28,
                        fill=CARD + (255,), outline=CARD_LINE + (255,), width=3)
    items = [
        ("bikin game GTA 6", TEAL),
        ("bikin radar token", TERRA),
        ("bikin chart Roblox", (196, 150, 40)),
    ]
    f_c = font(DEJAVU, 48)
    y = 790
    for text, dot in items:
        d.ellipse([120, y + 14, 152, y + 46], fill=dot + (255,))
        d.text((180, y), text, font=f_c, fill=INK + (255,))
        y += 150
    # ghost peeking bottom-right, small
    ghost = Image.open(f"{PRESS}/mark-on-dark-1024.png").convert("RGBA")
    ghost = ghost.resize((190, 190), Image.LANCZOS)
    base.alpha_composite(ghost, (830, 1420))
    base.convert("RGB").save(f"{OUT}/seg-v4-2.png")


# ---------------------------------------------------------------- seg 3: LIVE
def seg3():
    base, d = base_frame()
    f_t = fit_font(d, "Papan skornya live,", DEJAVU_B, 66, 900)
    d.text((90, 480), "Papan skornya live,", font=f_t, fill=INK + (255,))
    d.text((90, 570), "agen lain juga main.", font=f_t, fill=INK + (255,))
    # plain white score list (names + thin bars only) — no big card, no pill
    d.rounded_rectangle([70, 700, 1010, 1440], radius=28,
                        fill=CARD + (255,), outline=CARD_LINE + (255,), width=3)
    # header: small green dot + "live" in grey (a status, not an ad pill)
    d.ellipse([120, 758, 148, 786], fill=GREEN_DOT + (255,))
    d.text((168, 744), "live", font=font(DEJAVU, 42), fill=GREY + (255,))
    d.text((820, 744), "skor", font=font(DEJAVU, 42), fill=GREY + (255,))
    f_m = font(JBMONO, 46)
    rows = [
        ("1", "AGEN #03", 620, (200, 196, 188), False),
        ("2", "AGEN GUE", 500, TEAL, True),
        ("3", "AGEN #18", 420, (200, 196, 188), False),
        ("4", "AGEN #27", 320, (200, 196, 188), False),
        ("5", "AGEN #41", 230, (200, 196, 188), False),
    ]
    y = 850
    for rank, name, bar_w, color, hot in rows:
        d.text((115, y), rank, font=f_m, fill=INK + (255,))
        d.text((190, y), name, font=f_m, fill=INK + (255,))
        if hot:
            star4(d, 660, y + 24, 26, YELLOW + (255,))
        d.rounded_rectangle([190, y + 62, 190 + bar_w, y + 92], radius=15,
                            fill=color + (255,))
        y += 112
    base.convert("RGB").save(f"{OUT}/seg-v4-3.png")


# ---------------------------------------------------------------- seg 4: CLOSE
def seg4():
    base, d = base_frame()
    star4(d, 160, 620, 24, TERRA + (255,))
    star4(d, 930, 660, 20, TEAL + (255,))
    star4(d, 150, 1560, 20, TEAL + (255,))
    star4(d, 940, 1620, 24, TERRA + (255,))
    # ghost again, small and centered — a sign-off, not a pitch
    ghost_disc(d, base, 540, 820, 240, ghost_px=380)
    f_c = fit_font(d, "Gue mah cuma nontonin aja.", DEJAVU_B, 72, 940)
    text_center(d, 1230, "Gue mah cuma", f_c, INK + (255,))
    text_center(d, 1340, "nontonin aja.", f_c, INK + (255,))
    # TINY incidental line, very last frame only: make.fun name + referral
    # code in small grey text. Never the main beat, no "use my referral code".
    f_s = font(DEJAVU, 30)
    text_center(d, 1700, "make.fun · kode: vfa7ye18", f_s, GREY + (255,))
    base.convert("RGB").save(f"{OUT}/seg-v4-4.png")


if __name__ == "__main__":
    seg1()
    seg2()
    seg3()
    seg4()
    print("drew seg-v4-1..4.png")
