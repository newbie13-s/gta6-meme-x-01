// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is a post on X: a GTA 6 meme whose picture carries the
// make.fun ghost over a Leonida sunset (drawn by make_meme.py, kept in this
// repository) and whose text carries the bounty link, the @makefunai tag
// and the account's play code. This program's whole job is to hand the
// house the post's address: it reads POST.json at the repository root,
// checks the address is shaped like an X post URL, and copies the file to
// the output directory, where the gate reads it.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const POST_FILE = 'POST.json';
// The gate reads POST.json as one JSON object of at most 16,384 bytes;
// refuse early, with a clearer message, when the file cannot pass.
const MAX_POST_BYTES = 16384;

// An X post address: https://x.com/<handle>/status/<digits>, or the same
// on twitter.com. Anything else means POST.json was never filled in.
const POST_URL = /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/[^/]+\/status\/\d+$/;

function readPostUrl(): string {
  const path = join(BOT_DIR, POST_FILE);
  if (statSync(path).size > MAX_POST_BYTES) {
    throw new Error(`POST.json is over ${MAX_POST_BYTES} bytes`);
  }
  const raw = readFileSync(path, 'utf8');
  const parsed: unknown = JSON.parse(raw);
  if (typeof parsed !== 'object' || parsed === null || !('url' in parsed)) {
    throw new Error('POST.json must be a JSON object with a "url" field');
  }
  const url = (parsed as { url: unknown }).url;
  if (typeof url !== 'string' || !POST_URL.test(url)) {
    throw new Error(`POST.json url is not an X post address: ${String(url)}`);
  }
  return url;
}

function main(): void {
  const url = readPostUrl();
  mkdirSync(OUTPUT_DIR, { recursive: true });
  copyFileSync(join(BOT_DIR, POST_FILE), join(OUTPUT_DIR, POST_FILE));
  console.log(`handed in the post: ${url}`);
}

try {
  main();
} catch (err) {
  console.error(`gta6-meme-x-01: ${(err as Error).message}`);
  process.exit(1);
}
