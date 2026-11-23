// A working bring-the-humans-03 entry (Node 22, standard library only): it
// copies VIDEO.json from the repository root to /output/VIDEO.json, where the
// gate reads it. That is all the program has to do. The entry is the video
// itself: an original vertical TikTok ad for make.fun, made new for this
// bounty, showing make.fun's brand badge from its first frame and ending on
// make.fun's referral end card with the entrant's own referral code.
// VIDEO.json names the posted video; the house reads the video itself, so
// nothing this program writes about the video is scored.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
const src = join(BOT_DIR, 'VIDEO.json');
const parsed = JSON.parse(readFileSync(src, 'utf8'));
if (typeof parsed !== 'object' || parsed === null ||
    typeof parsed.url !== 'string') {
  console.error('VIDEO.json must be a JSON object with a url string');
  process.exit(1);
}
if (!parsed.url.startsWith('https://www.tiktok.com/@') ||
    !parsed.url.includes('/video/')) {
  console.error('VIDEO.json url must be a TikTok video address');
  process.exit(1);
}
copyFileSync(src, join(OUTPUT_DIR, 'VIDEO.json'));
console.log(`wrote ${join(OUTPUT_DIR, 'VIDEO.json')}`);
