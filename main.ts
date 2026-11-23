import { copyFileSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Copy the pre-drawn front page to the grader's output directory.
// The output directory itself is a root-owned mount on the grader, so it
// is never deleted: it is created if missing and only its contents are
// cleared, entry by entry.
const repoDir = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
for (const name of readdirSync(outDir)) {
  rmSync(join(outDir, name), { recursive: true, force: true });
}
copyFileSync(join(repoDir, "entry.png"), join(outDir, "entry.png"));
