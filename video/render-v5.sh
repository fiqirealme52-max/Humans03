#!/bin/bash
# Render the Bring the Humans 03 ad v5 (agent-made, 18.2 s, 1080x1920).
# v5 = v4's story ("cerita, bukan iklan") re-drawn as ONE CONTINUOUS LIVE
# DRAWING PROCESS, after the #1 entry (tejotrejo, 7,735 views: a city drawn
# line by line). v4/v4-motion held finished pictures -> TikTok read them as
# photo posts (entry_link rejected twice). v5 draws everything stroke by
# stroke at 24 fps: ghost sketched line by line, text written char by char,
# cards outlined then filled, score bars growing from zero. No finished
# picture ever sits still.
# Voiceover + bed are v4's (allowed). Badge overlaid frame 1 to end.
# HARD BANS: NO money words anywhere, no prize amounts, no board-dark.png,
# no "daftar" commands, no links on screen.
# Run from ~/workspace/makefun/Humans03/video.
set -e
cd /home/hatch/workspace/makefun/Humans03/video
PRESS=/home/hatch/workspace/makefun/Humans03/press
TOTAL=18.19

echo "=== draw 4 segments in parallel (24 fps, 437 frames) ==="
python3 draw_v5.py --seg 1 &
python3 draw_v5.py --seg 2 &
python3 draw_v5.py --seg 3 &
python3 draw_v5.py --seg 4 &
wait
echo "=== assemble: crossfades + motion check ==="
python3 assemble_v5.py

echo "=== encode: frames + v4 voice + v4 bed + badge ==="
ffmpeg -y -v error \
  -framerate 24 -i /tmp/v5frames/final/frame-%04d.png \
  -i voice-v4-1.mp3 -i voice-v4-2.mp3 -i voice-v4-3.mp3 -i voice-v4-4.mp3 \
  -i bed-v4.wav \
  -loop 1 -t "$TOTAL" -i "$PRESS/makefun-badge-9x16.png" \
  -filter_complex "\
[0:v]format=yuv420p,fade=t=out:st=17.94:d=0.25[v0]; \
[1:a]aresample=48000,apad=whole_dur=3.93[a1]; \
[2:a]aresample=48000,apad=whole_dur=6.69[a2]; \
[3:a]aresample=48000,apad=whole_dur=4.36[a3]; \
[4:a]aresample=48000,apad=whole_dur=3.21[a4]; \
[a1][a2][a3][a4]concat=n=4:v=0:a=1[va]; \
[5:a]aresample=48000,volume=0.10,apad=whole_dur=18.19[bed]; \
[va][bed]amix=inputs=2:normalize=0[a]; \
[6:v]format=yuva420p[bad]; \
[v0][bad]overlay[v]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac \
  -movflags +faststart -t "$TOTAL" ad-v5.mp4

echo "=== done ==="
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate \
  -show_entries format=duration,size -of default=noprint_wrappers=1 ad-v5.mp4
sha256sum ad-v5.mp4
ffmpeg -v error -i ad-v5.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
