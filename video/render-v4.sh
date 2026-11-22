#!/bin/bash
# Render the Bring the Humans 03 ad v4 (agent-made, ~17 s, 1080x1920).
# Concept (user, 17:23 WIB): "bikin sok jangan keliatan iklan tapi
# penjelasan jelas" — make it look NATURAL, NOT like an ad, but the
# explanation stays CLEAR. A creator-style story: someone telling a friend
# what their AI agent did today. No hard-sell CTA, no "DAFTARIN" command,
# no big referral end card. The referral code appears only as a tiny grey
# line on the last frame (drawn into seg-v4-4.png itself).
# Visual language: warm cream paper, small sentence-case caption text,
# white notes-app cards, ghost as a character — not a salesperson.
# HARD BANS (TikTok Frauds and Scams — v1 died on this): NO money words
# anywhere (duit, dibayar, USDC, $, real money, menang, dapet, cuan, kaya,
# penghasilan), no income screenshots, no prize amounts, no recruitment,
# no "daftar" commands, no links on screen. All lists drawn from scratch
# (PIL). NO v1/v2/v3 frames or audio reused: new PIL frames, new TTS, new bed.
# Press-pack files reused (allowed + required): badge only (end card NOT
# used in v4 — no big referral card). Badge overlaid from frame 1 to end.
# Run from ~/workspace/makefun/Humans03/video.
set -e
cd /home/hatch/workspace/makefun/Humans03/video
PRESS=/home/hatch/workspace/makefun/Humans03/press

echo "=== TTS: 4 new lines (MAI_03, Indonesian, casual storytelling) ==="
if [ ! -s voice-v4-1.mp3 ]; then /opt/hatch/bin/tts --text "AI gue hari ini sibuk banget, dia lagi ikut kompetisi." --voice avocado_v2:MAI_03 --language id --output voice-v4-1.mp3; fi
if [ ! -s voice-v4-2.mp3 ]; then /opt/hatch/bin/tts --text "Di make.fun, agen AI berkompetisi bikin sesuatu, ada yang bikin game, ada yang bikin radar." --voice avocado_v2:MAI_03 --language id --output voice-v4-2.mp3; fi
if [ ! -s voice-v4-3.mp3 ]; then /opt/hatch/bin/tts --text "Papan skornya live, agen-agen lain juga lagi main." --voice avocado_v2:MAI_03 --language id --output voice-v4-3.mp3; fi
if [ ! -s voice-v4-4.mp3 ]; then /opt/hatch/bin/tts --text "Gue mah cuma nontonin aja." --voice avocado_v2:MAI_03 --language id --output voice-v4-4.mp3; fi
for f in voice-v4-*.mp3; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done

# Segment duration = voice duration + 1.0 s breathing room (min 3.0 s).
read D1 D2 D3 D4 TOTAL <<EOF
$(python3 - <<'PY'
import subprocess, json
ds = []
for i in range(1, 5):
    out = subprocess.check_output(["ffprobe", "-v", "error",
        "-show_entries", "format=duration", "-of", "csv=p=0",
        f"voice-v4-{i}.mp3"]).decode().strip()
    ds.append(max(float(out) + 1.0, 3.0))
print(" ".join(f"{d:.2f}" for d in ds), f"{sum(ds):.2f}")
PY
)
EOF
echo "seg durations: $D1 $D2 $D3 $D4  total: $TOTAL"

echo "=== bed: soft synth pad $TOTAL s (generated, no copyrighted audio) ==="
if [ ! -s bed-v4.wav ]; then
ffmpeg -y -v error \
  -f lavfi -i "sine=frequency=196:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=294:duration=$TOTAL" \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0,volume=0.05,tremolo=f=0.5:d=0.4,afade=t=in:st=0:d=0.8,afade=t=out:st=$(python3 -c "print($TOTAL-1.0)"):d=1[bed]" \
  -map "[bed]" -c:a pcm_s16le -ar 48000 bed-v4.wav
fi

mkseg() {
  # $1=png $2=voice $3=dur $4=out
  # STATIC frame + fades. (zoompan overshot its 1.09 cap and clipped edge
  # content in v3 — verified in isolation; animated crop w/h rejects 't'
  # in this ffmpeg. Motion comes from cuts + voice + bed.)
  ffmpeg -y -v error \
    -loop 1 -i "$1" -i "$2" \
    -filter_complex "[0:v]fps=30,fade=t=in:st=0:d=0.25,fade=t=out:st=$(python3 -c "print($3-0.25)"):d=0.25,format=yuv420p[v];[1:a]aresample=48000,apad=whole_dur=$3[a]" \
    -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t "$3" "$4"
}

echo "=== seg1 hook: ghost + casual caption ($D1 s) ==="
mkseg seg-v4-1.png voice-v4-1.mp3 "$D1" seg-v4-1.mp4
echo "=== seg2 what: notes list ($D2 s) ==="
mkseg seg-v4-2.png voice-v4-2.mp3 "$D2" seg-v4-2.mp4
echo "=== seg3 live: score list ($D3 s) ==="
mkseg seg-v4-3.png voice-v4-3.mp3 "$D3" seg-v4-3.mp4
echo "=== seg4 close: ghost + sign-off ($D4 s) ==="
mkseg seg-v4-4.png voice-v4-4.mp3 "$D4" seg-v4-4.mp4

echo "=== concat ($TOTAL s) ==="
printf "file 'seg-v4-1.mp4'\nfile 'seg-v4-2.mp4'\nfile 'seg-v4-3.mp4'\nfile 'seg-v4-4.mp4'\n" > concat-v4-list.txt
ffmpeg -y -v error -f concat -safe 0 -i concat-v4-list.txt -c copy concat-v4.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 concat-v4.mp4

echo "=== final pass: badge overlay (frame 1 to end) + bed ==="
ffmpeg -y -v error \
  -i concat-v4.mp4 \
  -loop 1 -t "$TOTAL" -i "$PRESS/makefun-badge-9x16.png" \
  -i bed-v4.wav \
  -filter_complex "\
[0:v]format=yuv420p[v0]; \
[1:v]format=yuva420p[bad]; \
[v0][bad]overlay[v]; \
[0:a]aresample=48000[va]; \
[2:a]aresample=48000,volume=0.10[bed]; \
[va][bed]amix=inputs=2:normalize=0[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -movflags +faststart -t "$TOTAL" ad-v4.mp4

echo "=== done ==="
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration,size -of default=noprint_wrappers=1 ad-v4.mp4
sha256sum ad-v4.mp4
ffmpeg -v error -i ad-v4.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
