import { readFile, writeFile, unlink } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const dir = path.dirname(fileURLToPath(import.meta.url));
const cli = path.join(dir, 'node_modules/@marp-team/marp-cli/marp-cli.js');
const pdfOnly = process.argv.includes('--pdf-only');
const withPdf = pdfOnly || process.argv.includes('--pdf');
const normalize = text => text.trim().toLowerCase().replace(/[–—]/g, '-').replace(/\s+/g, ' ');
for (const deck of ['ThunderServe', 'Hetis']) {
  const source = `2026-10-21-${deck}.md`;
  const markdown = await readFile(path.join(dir, source), 'utf8');
  if (!pdfOnly) {
    let notes = '';
    for (const candidate of [`../${deck}_scripts.md`, `${deck}_scripts.md`]) {
      try { notes = await readFile(path.join(dir, candidate), 'utf8'); break; }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    const byTitle = new Map();
    for (const match of notes.matchAll(/^## 第 \d+ 頁｜([^\n]+)\n([\s\S]*?)(?=^## 第 |$(?![\s\S]))/gm)) {
      byTitle.set(normalize(match[1]), match[2].trim());
    }
    let count = 0, matched = 0;
    const annotated = markdown.replace(/<!-- SLIDE (\d+) -->([\s\S]*?)(?=\n---\n|$(?![\s\S]))/g, (all, n, body) => {
      count++;
      let title = body.match(/^# (.+)$/m)?.[1] ?? '';
      if (Number(n) === 1) title = 'Title';
      if (title === 'Questions & Discussion') title = 'Q&A';
      const text = byTitle.get(normalize(title));
      if (!text) return all;
      matched++;
      return `<!-- SLIDE ${n} -->${body}\n\n<!--\n${text.replaceAll('-->', '→')}\n-->\n`;
    });
    const temp = path.join(dir, `.${deck}-with-notes.md`);
    const output = path.join(dir, `${deck}.html`);
    try {
      await writeFile(temp, annotated);
      execFileSync(process.execPath, [cli, temp, '--html', '-o', output], {cwd: dir, stdio: 'inherit'});
      let html = await readFile(output, 'utf8');
      const images = [...new Set([...html.matchAll(/src="(assets\/[^"<>]+)"/g)].map(m => m[1]))];
      for (const image of images) {
        const data = await readFile(path.join(dir, image));
        const mime = image.endsWith('.svg') ? 'image/svg+xml' : 'image/png';
        html = html.replaceAll(`src="${image}"`, `src="data:${mime};base64,${data.toString('base64')}"`);
      }
      await writeFile(output, html);
      console.log(`${deck}: ${count} slides; ${matched} notes matched by title; ${images.length} images embedded.`);
    } finally { await unlink(temp).catch(() => {}); }
  }
  if (withPdf) {
    execFileSync(process.execPath, [cli, source, '--html', '--pdf', '--allow-local-files', '-o', `${deck}-marp.pdf`], {cwd: dir, stdio: 'inherit'});
  }
}
