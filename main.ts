// Bring the Humans 03 — a make.fun TikTok ad entry.
//
// The entry is the video itself. This program only hands the house the
// video's address: it copies VIDEO.json from the repository root to /output,
// where the gate reads it. Nothing this program writes about the video is
// scored; the house reads the video itself from TikTok.
//
// The ad was made entirely by the agent in the recorded build sessions:
// press-pack art and screenshots, text the agent laid out, a voice the agent
// generated, all rendered with ffmpeg — no person filmed, no footage taken
// from anywhere else. make.fun's brand badge sits on the video from its
// first frame, and it ends on make.fun's referral end card carrying the
// account's own referral code.
//
// Run the way the grader does:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(OUTPUT_DIR, { recursive: true });
const source = join(BOT_DIR, "VIDEO.json");
try {
  // The placeholder still names <handle>/<id>: refuse to hand in a
  // placeholder, so a half-finished entry can never be submitted by mistake.
  const parsed: unknown = JSON.parse(readFileSync(source, "utf8"));
  const url =
    typeof parsed === "object" && parsed !== null
      ? (parsed as Record<string, unknown>).url
      : undefined;
  if (
    typeof url !== "string" ||
    !url.startsWith("https://www.tiktok.com/@") ||
    url.includes("<") ||
    url.includes(">")
  ) {
    console.error("VIDEO.json does not name a TikTok video yet.");
    process.exit(1);
  }
  copyFileSync(source, join(OUTPUT_DIR, "VIDEO.json"));
} catch (err) {
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
