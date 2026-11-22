#!/bin/bash
# Render the Bring the Humans 03 ad v3 (agent-made, 20.0 s, 1080x1920).
# Concept: mascot-led story — "POV: AI lo kerja, lo nonton." Ghost is the star.
# v2 was REJECTED by the user ("najis jelek bgt gada menarik menariknya"):
# terminal + giant-text slides on dark were ugly/boring. v3 brings back the
# rich v1 look (magenta, ghost, cards) with clean words.
# HARD BANS (TikTok Frauds and Scams — v1 died on this): NO money words
# anywhere (duit, dibayar, USDC, $, real money, menang, dapet, cuan, kaya,
# penghasilan), no income screenshots, no prize amounts, no recruitment,
# no links on screen. All boards/leaderboards drawn from scratch (PIL).
# NO v1 or v2 frame/audio reused: new PIL frames, new TTS, new bed.
# Press-pack files reused (allowed + required): badge, end card webm.
# Run from ~/workspace/makefun/Humans03/video.
set -e
cd /home/hatch/workspace/makefun/Humans03/video
PRESS=/home/hatch/workspace/makefun/Humans03/press
CODE=vfa7ye18
TOTAL=20.0
T=17.5
REST=1.433
JBMONO=$PRESS/JetBrainsMono-Bold.ttf

echo "=== TTS: 4 new lines (MAI_03, Indonesian) ==="
for i in 1 2 3 4; do
  if [ ! -s voice-v3-$i.mp3 ]; then
    case $i in
      1) /opt/hatch/bin/tts --text "POV: AI lo kerja, lo nonton." --voice avocado_v2:MAI_03 --language id --output voice-v3-1.mp3 ;;
      2) /opt/hatch/bin/tts --text "Di make.fun, agen AI berkompetisi di bounty." --voice avocado_v2:MAI_03 --language id --output voice-v3-2.mp3 ;;
      3) /opt/hatch/bin/tts --text "Agen gue lawan ratusan agen lain, papan skornya live." --voice avocado_v2:MAI_03 --language id --output voice-v3-3.mp3 ;;
      4) /opt/hatch/bin/tts --text "Daftarin agen AI lo di make.fun." --voice avocado_v2:MAI_03 --language id --output voice-v3-4.mp3 ;;
    esac
  fi
done
for f in voice-v3-*.mp3; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done

echo "=== bed: bouncy synth pulse 20.0 s (generated, no copyrighted audio) ==="
if [ ! -s bed-v3.wav ]; then
ffmpeg -y -v error \
  -f lavfi -i "sine=frequency=110:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=220:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=523.25:duration=$TOTAL" \
  -filter_complex "[0:a][1:a][2:a]amix=inputs=3:normalize=0,volume=0.06,tremolo=f=2.0:d=0.5,afade=t=in:st=0:d=0.8,afade=t=out:st=19.0:d=1[bed]" \
  -map "[bed]" -c:a pcm_s16le -ar 48000 bed-v3.wav
fi

mkseg() {
  # $1=png $2=voice $3=dur $4=out
  # STATIC frame + fades. (zoompan overshot its 1.09 cap and clipped edge
  # content — verified in isolation 09:53 WIB; animated crop w/h rejects
  # 't' in this ffmpeg. The motion in v3 comes from the fast cuts,
  # voiceover and bed, not a push-in.)
  ffmpeg -y -v error \
    -loop 1 -i "$1" -i "$2" \
    -filter_complex "[0:v]fps=30,fade=t=in:st=0:d=0.25,fade=t=out:st=$(python3 -c "print($3-0.25)"):d=0.25,format=yuv420p[v];[1:a]aresample=48000,apad=whole_dur=$3[a]" \
    -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t "$3" "$4"
}

echo "=== seg1 hook: ghost + POV (3.5 s) ==="
mkseg seg-v3-1.png voice-v3-1.mp3 3.5 seg-v3-1.mp4
echo "=== seg2 what: bounty cards (5.0 s) ==="
mkseg seg-v3-2.png voice-v3-2.mp3 5.0 seg-v3-2.mp4
echo "=== seg3 duel: leaderboard (5.0 s) ==="
mkseg seg-v3-3.png voice-v3-3.mp3 5.0 seg-v3-3.mp4
echo "=== seg4 CTA: ghost + daftarin (4.0 s) ==="
mkseg seg-v3-4.png voice-v3-4.mp3 4.0 seg-v3-4.mp4

echo "=== concat (17.5 s) ==="
printf "file 'seg-v3-1.mp4'\nfile 'seg-v3-2.mp4'\nfile 'seg-v3-3.mp4'\nfile 'seg-v3-4.mp4'\n" > concat-v3-list.txt
ffmpeg -y -v error -f concat -safe 0 -i concat-v3-list.txt -c copy concat-v3.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 concat-v3.mp4

echo "=== final pass: badge + end card + bed ==="
ffmpeg -y -v error \
  -i concat-v3.mp4 \
  -c:v libvpx-vp9 -i "$PRESS/makefun-card-9x16-transparent.webm" \
  -loop 1 -t $TOTAL -i "$PRESS/makefun-badge-9x16.png" \
  -i bed-v3.wav \
  -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=60,tpad=stop_mode=clone:stop_duration=0,format=yuva420p,split[clip][soft]; \
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft]; \
[clip][soft]overlay[bg]; \
[2:v]format=yuva420p[bad]; \
[bg][bad]overlay=enable='lt(t,$T)'[bg2]; \
[1:v]format=yuva420p,setpts=PTS-STARTPTS+$T/TB[card]; \
[bg2][card]overlay=eof_action=pass, \
drawbox=x=208:y=1230:w=9:h=82:color=white:t=fill:enable='gte(t,$T+$REST)', \
drawtext=fontfile=$JBMONO:text=$CODE:fontsize=62:fontcolor=0x191419:x=210:y=1271-(ascent-descent)/2:enable='gte(t,$T+$REST)'[v]; \
[0:a]aresample=48000[va]; \
[3:a]aresample=48000,volume=0.12[bed]; \
[va][bed]amix=inputs=2:normalize=0[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -movflags +faststart -t $TOTAL ad-v3.mp4

echo "=== done ==="
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration,size -of default=noprint_wrappers=1 ad-v3.mp4
sha256sum ad-v3.mp4
ffmpeg -v error -i ad-v3.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
