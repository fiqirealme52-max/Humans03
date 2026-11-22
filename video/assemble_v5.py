#!/usr/bin/env python3
"""Assemble v5 frames: crossfade segment boundaries, verify motion.

- Segment frame counts at 24 fps: seg1 94 (0-93), seg2 161 (94-254),
  seg3 105 (255-359), seg4 77 (360-436). Total 437 frames = 18.21 s.
- First 6 frames (0.25 s) of seg2/3/4 crossfade from the previous
  segment's fully-drawn final frame: alpha (i+1)/6.
- Then measures mean absolute pixel diff between frames 1 s apart
  (24 frames) across the whole video — the drawing-process proof.
  A static slideshow scores ~0.0x; v4-motion scored 2.6-10.7.
"""
import os

import numpy as np
from PIL import Image

FR = "/tmp/v5frames"
FPS = 24
COUNTS = {1: 94, 2: 161, 3: 105, 4: 77}
FADE = 6  # frames of crossfade at each segment boundary


def seg_frame(seg, i):
    return Image.open(f"{FR}/seg{seg}/frame-{i:04d}.png").convert("RGB")


def seg_final(seg):
    return Image.open(f"{FR}/seg{seg}-final.png").convert("RGB")


def main():
    final_dir = f"{FR}/final"
    os.makedirs(final_dir, exist_ok=True)
    # Stream the 1-second diffs: keep only the last 24 downscaled frames
    # (loading all 437 full-res float32 frames at once OOM-killed the box).
    from collections import deque
    recent = deque(maxlen=FPS)  # downscaled float32 frames, 1 s of history
    diffs = []
    g = 0
    for seg in (1, 2, 3, 4):
        prev_final = seg_final(seg - 1) if seg > 1 else None
        for i in range(COUNTS[seg]):
            img = seg_frame(seg, i)
            if prev_final is not None and i < FADE:
                a = (i + 1) / FADE
                img = Image.blend(prev_final, img, a)
            img.save(f"{final_dir}/frame-{g:04d}.png")
            small = np.asarray(img.resize((270, 480)), dtype=np.float32)
            if len(recent) == FPS:
                diffs.append(float(np.mean(np.abs(small - recent[0]))))
            recent.append(small)
            g += 1
    print(f"assembled {g} frames")

    print("1-second pair diffs (mean abs pixel, 0-255):")
    for k, d in enumerate(diffs):
        print(f"  t={k:2d}s -> t={k+1:2d}s : {d:6.2f}")
    print(f"  MIN {min(diffs):.2f}  MEAN {sum(diffs)/len(diffs):.2f}  "
          f"pairs below 0.5: {sum(1 for d in diffs if d < 0.5)}")


if __name__ == "__main__":
    main()
