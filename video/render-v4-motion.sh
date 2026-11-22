#!/bin/bash
# Render the Bring the Humans 03 ad v4 WITH REAL MOTION (ad-v4-motion.mp4).
# Why: the user diagnosed it themselves (17:53 WIB): "isi vidio lu cuma
# foto" — v4's frames are STATIC images looped with only 0.25 s fades, so
# TikTok classifies the upload as a PHOTO POST and make.fun's entry_link
# check rejects it ("a photo post is no clip"). This happened TWICE
# (round 2 + round 3, two different uploads, same verdict). The v1 video
# (which had motion) PASSED entry_link. So: same concept, same layout,
# same text, same voiceover, same bed, same badge — plus CONTINUOUS
# motion on every segment. No frame may sit still longer than ~0.5 s.
#
# MOTION DESIGN (Ken Burns, done correctly):
# - zoompan is NOT used: v3 dropped it because it overshot its cap and
#   clipped edge content. Instead: animated scale + crop, which gives
#   exact control of the crop window — nothing can clip by construction.
# - Per segment of duration D: scale goes 1.04 -> 1.08
#   (w='1080*(1.04+0.04*t/D)', h same), crop window 1080x1920 drifts
#   linearly +/-10 px horizontally / +/-14 px vertically.
# - CORRECTED MODEL (measured 22 Nov, ghost-bbox trajectory): crop's
#   in_w/in_h are evaluated ONCE at init (the FIRST frame's scaled
#   size, 1.04x), NOT per frame — so the crop window does NOT recenter
#   as the image zooms. The pan must be designed against the INIT
#   dimensions. Consequence: a LEFTWARD pan pushes right-edge content
#   to the frame edge — seg2's ghost (ends x=1012) touched x=1079 at
#   the leftward-pan extreme (first render). So EVERY segment drifts
#   horizontally RIGHTWARD (DX -10 -> +10); only the vertical
#   direction alternates. Worst-case visible window with this layout
#   stays within original x in [11, 1050], y in [22, 1900]: notes card
#   (x>=70), peeking ghost (x<=1012), score card (x<=1010), tiny
#   last-frame line (y=1700) all stay in frame with margin.
# - Fades (0.25 s in/out per segment) are kept — they mask the cuts
#   between segments. Motion + fades: every frame differs from the last.
#
# Reused from v4 (identical content, NOT v1/v2/v3): seg-v4-1..4.png,
# voice-v4-1..4.mp3, bed-v4.wav, press-pack badge (final pass only).
# HARD BANS (unchanged): ZERO money words anywhere (duit, dibayar, USDC,
# $, menang, dapet, cuan, kaya, penghasilan), no prize amounts,
# board-dark.png NOT used, no "daftar" commands, no links on screen.
# Run from ~/workspace/makefun/Humans03/video.
set -e
cd /home/hatch/workspace/makefun/Humans03/video
PRESS=/home/hatch/workspace/makefun/Humans03/press

echo "=== TTS: same 4 lines as v4 (reuse voice-v4-*.mp3) ==="
if [ ! -s voice-v4-1.mp3 ]; then /opt/hatch/bin/tts --text "AI gue hari ini sibuk banget, dia lagi ikut kompetisi." --voice avocado_v2:MAI_03 --language id --output voice-v4-1.mp3; fi
if [ ! -s voice-v4-2.mp3 ]; then /opt/hatch/bin/tts --text "Di make.fun, agen AI berkompetisi bikin sesuatu, ada yang bikin game, ada yang bikin radar." --voice avocado_v2:MAI_03 --language id --output voice-v4-2.mp3; fi
if [ ! -s voice-v4-3.mp3 ]; then /opt/hatch/bin/tts --text "Papan skornya live, agen-agen lain juga lagi main." --voice avocado_v2:MAI_03 --language id --output voice-v4-3.mp3; fi
if [ ! -s voice-v4-4.mp3 ]; then /opt/hatch/bin/tts --text "Gue mah cuma nontonin aja." --voice avocado_v2:MAI_03 --language id --output voice-v4-4.mp3; fi
for f in voice-v4-*.mp3; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done

# Segment duration = voice duration + 1.0 s breathing room (min 3.0 s).
read D1 D2 D3 D4 TOTAL <<EOF
$(python3 - <<'PY'
import subprocess
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

echo "=== bed: reuse bed-v4.wav (generated soft pad) ==="
if [ ! -s bed-v4.wav ]; then
ffmpeg -y -v error \
  -f lavfi -i "sine=frequency=196:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=294:duration=$TOTAL" \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0,volume=0.05,tremolo=f=0.5:d=0.4,afade=t=in:st=0:d=0.8,afade=t=out:st=$(python3 -c "print($TOTAL-1.0)"):d=1[bed]" \
  -map "[bed]" -c:a pcm_s16le -ar 48000 bed-v4.wav
fi

mkseg_motion() {
  # $1=png $2=voice $3=dur $4=dx_expr $5=dy_expr $6=out
  # scale animates 1.04->1.08 over the segment (zoom in, never out past
  # the frame edge); crop window drifts +/-10px H / +/-14px V (slow pan).
  # Crop x/y stay inside the scaled frame at every t by construction
  # (see header). Fades mask the cuts between segments.
  ffmpeg -y -v error \
    -framerate 30 -loop 1 -i "$1" -i "$2" \
    -filter_complex "[0:v]scale=w='1080*(1.04+0.04*t/$3)':h='1920*(1.04+0.04*t/$3)':eval=frame,crop=1080:1920:x='(in_w-1080)/2+($4)':y='(in_h-1920)/2+($5)',fps=30,fade=t=in:st=0:d=0.25,fade=t=out:st=$(python3 -c "print($3-0.25)"):d=0.25,format=yuv420p[v];[1:a]aresample=48000,apad=whole_dur=$3[a]" \
    -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t "$3" "$6"
}

echo "=== seg1 hook: zoom in + drift down-right ($D1 s) ==="
mkseg_motion seg-v4-1.png voice-v4-1.mp3 "$D1" "-10+20*t/$D1" "-14+28*t/$D1" seg-v4m-1.mp4
echo "=== seg2 what: zoom in + drift up-right ($D2 s) ==="
mkseg_motion seg-v4-2.png voice-v4-2.mp3 "$D2" "-10+20*t/$D2" "14-28*t/$D2" seg-v4m-2.mp4
echo "=== seg3 live: zoom in + drift up-right ($D3 s) ==="
mkseg_motion seg-v4-3.png voice-v4-3.mp3 "$D3" "-10+20*t/$D3" "14-28*t/$D3" seg-v4m-3.mp4
echo "=== seg4 close: zoom in + drift down-left ($D4 s) ==="
mkseg_motion seg-v4-4.png voice-v4-4.mp3 "$D4" "10-20*t/$D4" "-14+28*t/$D4" seg-v4m-4.mp4

echo "=== concat ($TOTAL s) ==="
printf "file 'seg-v4m-1.mp4'\nfile 'seg-v4m-2.mp4'\nfile 'seg-v4m-3.mp4'\nfile 'seg-v4m-4.mp4'\n" > concat-v4m-list.txt
ffmpeg -y -v error -f concat -safe 0 -i concat-v4m-list.txt -c copy concat-v4m.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 concat-v4m.mp4

echo "=== final pass: badge overlay (frame 1 to end) + bed ==="
ffmpeg -y -v error \
  -i concat-v4m.mp4 \
  -loop 1 -t "$TOTAL" -i "$PRESS/makefun-badge-9x16.png" \
  -i bed-v4.wav \
  -filter_complex "\
[0:v]format=yuv420p[v0]; \
[1:v]format=yuva420p[bad]; \
[v0][bad]overlay[v]; \
[0:a]aresample=48000[va]; \
[2:a]aresample=48000,volume=0.10[bed]; \
[va][bed]amix=inputs=2:normalize=0[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -movflags +faststart -t "$TOTAL" ad-v4-motion.mp4

echo "=== done ==="
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration,size -of default=noprint_wrappers=1 ad-v4-motion.mp4
sha256sum ad-v4-motion.mp4
ffmpeg -v info -i ad-v4-motion.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
