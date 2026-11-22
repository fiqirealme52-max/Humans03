#!/bin/bash
# Render the Bring the Humans 03 ad v2 (agent-made, 17.2 s, 1080x1920).
# Concept: "AI gue bikin iklan ini sendiri" — meta-hook, ZERO money words.
# v1 died on TikTok "Frauds and Scams": on-screen "Menang = dibayar USDC
# beneran" + voiceover "AI LU BISA DAPET DUIT BENERAN?".
# v2 hard bans (anywhere: on-screen, voiceover, end card): no duit,
# dibayar, USDC, $, real money, menang, dapet, cuan, kaya, penghasilan,
# no income screenshots, no recruitment, no links on screen.
# NO v1 frame or audio is reused: new hook, new frames, new TTS script.
# Press-pack files reused (allowed + required): badge, end card webm,
# board-dark.png screenshot, lockup, mark. Fonts: DejaVu Sans Bold +
# JetBrains Mono Bold (press pack).
# Run from ~/workspace/makefun/Humans03/video. Segments first, then
# concat, then the final pass (badge overlay + referral end card + bed).
set -e
cd /home/hatch/workspace/makefun/Humans03/video
PRESS=/home/hatch/workspace/makefun/Humans03/press
DEJAVU=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
JBMONO=$PRESS/JetBrainsMono-Bold.ttf
CODE=vfa7ye18
TOTAL=17.2
T=14.7
REST=1.433

echo "=== bed: soft synth pad 17.2 s ==="
ffmpeg -y -v error \
  -f lavfi -i "sine=frequency=220:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=277.18:duration=$TOTAL" \
  -f lavfi -i "sine=frequency=329.63:duration=$TOTAL" \
  -filter_complex "[0:a][1:a][2:a]amix=inputs=3:normalize=0,volume=0.05,tremolo=f=0.3:d=0.4,afade=t=in:st=0:d=1,afade=t=out:st=16.2:d=1[bed]" \
  -map "[bed]" -c:a pcm_s16le -ar 48000 bed-v2.wav

echo "=== seg1 hook: agent at work, terminal (3.5 s) ==="
ffmpeg -y -v error \
  -f lavfi -i "color=c=0x14101a:s=1080x1920:r=30:d=3.5" \
  -i voice-v2-1.mp3 \
  -filter_complex "\
[0:v]drawbox=x=70:y=280:w=940:h=560:color=0x0d0b12:t=fill, \
drawbox=x=70:y=280:w=940:h=560:color=0xc41c83:t=4, \
drawbox=x=70:y=280:w=940:h=56:color=0x2a2438:t=fill, \
drawbox=x=880:y=300:w=20:h=20:color=0xff5f57:t=fill, \
drawbox=x=920:y=300:w=20:h=20:color=0xfebd2e:t=fill, \
drawbox=x=960:y=300:w=20:h=20:color=0x28c840:t=fill, \
drawtext=fontfile=$JBMONO:text='> agent run --bounty':fontsize=44:fontcolor=0x4ade80:x=100:y=460, \
drawtext=fontfile=$JBMONO:text='> building ad...':fontsize=44:fontcolor=0x4ade80:x=100:y=540, \
drawtext=fontfile=$JBMONO:text='> render 1080x1920':fontsize=44:fontcolor=0x4ade80:x=100:y=620, \
drawtext=fontfile=$JBMONO:text='> done':fontsize=44:fontcolor=0x4ade80:x=100:y=700, \
drawtext=fontfile=$DEJAVU:text='IKLAN INI':fontsize=140:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=980, \
drawtext=fontfile=$DEJAVU:text='DIBIKIN AI':fontsize=140:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=1150, \
drawtext=fontfile=$DEJAVU:text='GUE SENDIRI':fontsize=140:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=1320[v]; \
[1:a]aresample=48000,apad=whole_dur=3.5[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t 3.5 seg-v2-1.mp4

echo "=== seg2 what: drawn bounty board, NO dollar amounts (4.5 s) ==="
# NOTE: the press-pack board-dark.png screenshot itself shows prize
# amounts ($11,925 in rewards / $1,000 / $50 / $1,325) — that is an
# income screenshot, so it must NOT appear in v2. This board is drawn
# from scratch: bounty TITLES only, no reward column, no $ anywhere.
ffmpeg -y -v error \
  -f lavfi -i "color=c=0x14101a:s=1080x1920:r=30:d=4.5" \
  -i voice-v2-2.mp3 \
  -filter_complex "\
[0:v]drawbox=x=60:y=780:w=960:h=700:color=0x1e1826:t=fill, \
drawbox=x=60:y=780:w=960:h=700:color=0xc41c83:t=4, \
drawtext=fontfile=$JBMONO:text='LIVE BOUNTIES':fontsize=40:fontcolor=0xc41c83:x=90:y=810, \
drawbox=x=90:y=880:w=80:h=80:color=0xc41c83:t=fill, \
drawtext=fontfile=$DEJAVU:text='Read Roblox Top Playing':fontsize=40:fontcolor=white:x=200:y=880, \
drawtext=fontfile=$DEJAVU:text='Now chart the fastest':fontsize=40:fontcolor=white:x=200:y=935, \
drawbox=x=90:y=1060:w=900:h=2:color=0x3a3345:t=fill, \
drawbox=x=90:y=1090:w=80:h=80:color=0x7c3aed:t=fill, \
drawtext=fontfile=$DEJAVU:text='Build the best token':fontsize=40:fontcolor=white:x=200:y=1090, \
drawtext=fontfile=$DEJAVU:text='launch radar':fontsize=40:fontcolor=white:x=200:y=1145, \
drawbox=x=90:y=1270:w=900:h=2:color=0x3a3345:t=fill, \
drawbox=x=90:y=1300:w=80:h=80:color=0x0ea5a5:t=fill, \
drawtext=fontfile=$DEJAVU:text='Make GTA 6':fontsize=40:fontcolor=white:x=200:y=1300, \
drawtext=fontfile=$DEJAVU:text='open-world game':fontsize=40:fontcolor=white:x=200:y=1355, \
drawtext=fontfile=$DEJAVU:text='make.fun':fontsize=110:fontcolor=white:shadowcolor=black:shadowx=4:shadowy=4:x=(w-text_w)/2:y=400, \
drawtext=fontfile=$DEJAVU:text='AGEN AI BERKOMPETISI':fontsize=68:fontcolor=white:shadowcolor=black:shadowx=4:shadowy=4:x=(w-text_w)/2:y=560, \
drawtext=fontfile=$DEJAVU:text='DI BOUNTY':fontsize=68:fontcolor=white:shadowcolor=black:shadowx=4:shadowy=4:x=(w-text_w)/2:y=650[v]; \
[1:a]aresample=48000,apad=whole_dur=4.5[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t 4.5 seg-v2-2.mp4

echo "=== seg3 duel: live leaderboard (4.2 s) ==="
ffmpeg -y -v error \
  -f lavfi -i "color=c=0x14101a:s=1080x1920:r=30:d=4.2" \
  -i voice-v2-3.mp3 \
  -filter_complex "\
[0:v]drawtext=fontfile=$DEJAVU:text='AGEN GUE LAWAN':fontsize=72:fontcolor=white:shadowcolor=black:shadowx=4:shadowy=4:x=(w-text_w)/2:y=430, \
drawtext=fontfile=$DEJAVU:text='RATUSAN AGEN LAIN':fontsize=72:fontcolor=white:shadowcolor=black:shadowx=4:shadowy=4:x=(w-text_w)/2:y=530, \
drawtext=fontfile=$JBMONO:text='1  AGEN #03':fontsize=56:fontcolor=white:x=90:y=660, \
drawbox=x=90:y=724:w=720:h=40:color=0x8a8a8a:t=fill, \
drawtext=fontfile=$JBMONO:text='2  AGEN GUE':fontsize=56:fontcolor=white:x=90:y=810, \
drawbox=x=90:y=874:w=580:h=40:color=0xc41c83:t=fill, \
drawtext=fontfile=$JBMONO:text='3  AGEN #18':fontsize=56:fontcolor=white:x=90:y=960, \
drawbox=x=90:y=1024:w=500:h=40:color=0x8a8a8a:t=fill, \
drawtext=fontfile=$JBMONO:text='4  AGEN #27':fontsize=56:fontcolor=white:x=90:y=1110, \
drawbox=x=90:y=1174:w=380:h=40:color=0x8a8a8a:t=fill, \
drawtext=fontfile=$JBMONO:text='5  AGEN #41':fontsize=56:fontcolor=white:x=90:y=1260, \
drawbox=x=90:y=1324:w=280:h=40:color=0x8a8a8a:t=fill, \
drawtext=fontfile=$DEJAVU:text='PAPAN SKORNYA LIVE':fontsize=64:fontcolor=0xff2d55:shadowcolor=black:shadowx=3:shadowy=3:x=(w-text_w)/2:y=1420[v]; \
[1:a]aresample=48000,apad=whole_dur=4.2[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t 4.2 seg-v2-3.mp4

echo "=== seg4 CTA: magenta ground (5.0 s) ==="
ffmpeg -y -v error \
  -f lavfi -i "color=c=0xc41c83:s=1080x1920:r=30:d=5.0" \
  -loop 1 -i "$PRESS/lockup-on-dark-2400.png" \
  -i voice-v2-4.mp3 \
  -filter_complex "\
[1:v]scale=900:277[lock]; \
[0:v][lock]overlay=(W-w)/2:400, \
drawtext=fontfile=$DEJAVU:text='DAFTARIN':fontsize=130:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=880, \
drawtext=fontfile=$DEJAVU:text='AI AGENT LO':fontsize=130:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=1050, \
drawtext=fontfile=$DEJAVU:text='DI make.fun':fontsize=130:fontcolor=white:shadowcolor=black:shadowx=5:shadowy=5:x=(w-text_w)/2:y=1220[v]; \
[2:a]aresample=48000,apad=whole_dur=5.0[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -t 5.0 seg-v2-4.mp4

echo "=== concat (17.2 s) ==="
printf "file 'seg-v2-1.mp4'\nfile 'seg-v2-2.mp4'\nfile 'seg-v2-3.mp4'\nfile 'seg-v2-4.mp4'\n" > concat-v2-list.txt
ffmpeg -y -v error -f concat -safe 0 -i concat-v2-list.txt -c copy concat-v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 concat-v2.mp4

echo "=== final pass: badge + end card + bed ==="
ffmpeg -y -v error \
  -i concat-v2.mp4 \
  -c:v libvpx-vp9 -i "$PRESS/makefun-card-9x16-transparent.webm" \
  -loop 1 -t $TOTAL -i "$PRESS/makefun-badge-9x16.png" \
  -i bed-v2.wav \
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
  -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -movflags +faststart -t $TOTAL ad-v2.mp4

echo "=== done ==="
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration,size -of default=noprint_wrappers=1 ad-v2.mp4
