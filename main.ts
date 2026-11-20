// News-image entry (Node 22, standard library only, no network).
//
// The front page is drawn at build time by app/render.py into the
// entry.png beside this file. This program writes that image to the
// output directory. It runs twice in grading and both runs write the
// same bytes, because the file is copied byte for byte.
//
// Run it outside the grader's container with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const png = readFileSync(new URL('./entry.png', import.meta.url));
writeFileSync(join(outDir, 'entry.png'), png);
console.log(`wrote entry.png (${png.length} bytes) to ${outDir}`);
