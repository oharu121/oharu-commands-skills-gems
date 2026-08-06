#!/usr/bin/env node
/*
 * Build a browsable contact sheet from a directory of candidate SVGs, and serve
 * it.
 *
 * Used by the `/logo` skill between rounds. It exists because judging a mark
 * from its markup does not work: the decisions that actually matter — does the
 * counter close up, does the silhouette survive a browser tab, do these eight
 * concepts differ or are they one concept in eight hats — are only visible
 * rendered, side by side, at the sizes the mark will really be used at.
 *
 * Each concept is shown large, at 32px, and at 16px. The 16px column is the
 * point. It is the size that eliminates candidates, and it is the one nobody
 * looks at until the favicon ships.
 *
 * Usage:
 *   node scripts/brand/gallery.mjs <dir> [--port 4599] [--title "Round 2"]
 *
 * <dir> holds `*.svg` plus an optional `concepts.json`:
 *
 *   [{ "id": "c01", "name": "Aperture", "note": "Ring with a gap",
 *      "group": "Icon-only", "fixedColour": false }]
 *
 * Anything without an entry still renders, keyed on its filename. `group` binds
 * concepts into sections; `fixedColour` marks a concept whose palette is baked
 * in rather than inheriting `currentColor`.
 */

import { createServer } from 'node:http';
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { basename, extname, join, resolve, sep } from 'node:path';

const args = process.argv.slice(2);
const dir = resolve(args.find((a) => !a.startsWith('--')) ?? '.');
const flag = (name, fallback) => {
	const i = args.indexOf(`--${name}`);
	return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};
const port = Number(flag('port', 4599));
const title = flag('title', basename(dir));
const noServe = args.includes('--no-serve');

if (!existsSync(dir)) {
	console.error(`No such directory: ${dir}`);
	process.exit(1);
}

const svgs = readdirSync(dir)
	.filter((f) => extname(f) === '.svg')
	.sort();

if (svgs.length === 0) {
	console.error(`No .svg files in ${dir}`);
	process.exit(1);
}

const metaPath = join(dir, 'concepts.json');
const metaList = existsSync(metaPath) ? JSON.parse(readFileSync(metaPath, 'utf8')) : [];
const meta = Object.fromEntries(metaList.map((c) => [c.id, c]));

const concepts = svgs.map((file) => {
	const id = basename(file, '.svg');
	const m = meta[id] ?? {};
	return {
		id,
		name: m.name ?? '',
		note: m.note ?? '',
		group: m.group ?? 'Concepts',
		fixedColour: Boolean(m.fixedColour),
		markup: readFileSync(join(dir, file), 'utf8').trim(),
	};
});

/*
 * Sections follow the order groups first appear in concepts.json, so the author
 * controls how the sheet reads. Groups only present on disk fall in after, in
 * filename order — sorting sections alphabetically would scatter a deliberate
 * narrative, and sorting by file order makes it depend on how you named things.
 */
const declared = [...new Set(metaList.map((c) => c.group).filter(Boolean))];
const found = [...new Set(concepts.map((c) => c.group))];
const groups = [...declared.filter((g) => found.includes(g)), ...found.filter((g) => !declared.includes(g))];
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const card = (c) => `
  <figure class="card" data-id="${esc(c.id)}">
    <div class="big">${c.markup}</div>
    <div class="row">
      <span class="chip"><i>32</i>${c.markup}</span>
      <span class="chip"><i>16</i>${c.markup}</span>
      <span class="tag">${c.fixedColour ? 'fixed colour' : 'themeable'}</span>
    </div>
    <figcaption><b>${esc(c.name ? `${c.id} · ${c.name}` : c.id)}</b><span>${esc(c.note)}</span></figcaption>
  </figure>`;

const html = `<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<style>
 :root{--bg-1:#fff;--bg-2:#f8fafc;--text-1:#0f172a;--text-2:#475569;--border:#e2e8f0;--accent:#1d4ed8}
 [data-theme=dark]{--bg-1:#0b1120;--bg-2:#111827;--text-1:#e2e8f0;--text-2:#94a3b8;--border:#1f2937;--accent:#60a5fa}
 *{box-sizing:border-box}
 body{margin:0;padding:2rem 1.5rem 5rem;background:var(--bg-1);color:var(--text-1);
      font:15px/1.6 ui-sans-serif,system-ui,-apple-system,sans-serif}
 header{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap}
 h1{font-size:1.25rem;margin:0}
 p.lede{color:var(--text-2);margin:.5rem 0 1.5rem;max-width:62ch}
 button{font:inherit;padding:.45rem .9rem;border-radius:8px;cursor:pointer;
        border:1px solid var(--border);background:var(--bg-2);color:var(--text-1)}
 h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-2);
    margin:2.5rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}
 .grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(18rem,1fr))}
 .card{margin:0;border:1px solid var(--border);border-radius:12px;background:var(--bg-2);
       padding:1rem;display:flex;flex-direction:column;gap:.85rem;cursor:pointer}
 .card.pick{outline:2px solid var(--accent);outline-offset:2px}
 .big{display:grid;place-items:center;min-height:9rem;padding:1rem;background:var(--bg-1);
      border-radius:8px;color:var(--accent)}
 .big svg{max-width:100%;max-height:7rem;height:auto;width:auto}
 .row{display:flex;gap:1.1rem;align-items:center;color:var(--accent)}
 .chip{display:flex;align-items:center;gap:.35rem}
 .chip i{font-style:normal;font-size:.65rem;color:var(--text-2)}
 .chip:nth-of-type(1) svg{height:32px;width:auto}
 .chip:nth-of-type(2) svg{height:16px;width:auto}
 .tag{margin-left:auto;font-size:.65rem;padding:.15rem .45rem;border-radius:4px;
      background:var(--bg-1);border:1px solid var(--border);color:var(--text-2)}
 figcaption{display:flex;flex-direction:column;gap:.15rem;font-size:.8rem}
 figcaption span{color:var(--text-2)}
 #picked{position:fixed;left:0;right:0;bottom:0;padding:.6rem 1.5rem;background:var(--bg-2);
         border-top:1px solid var(--border);font-size:.8rem;color:var(--text-2)}
</style>
</head>
<body>
<header><h1>${esc(title)}</h1><button id="t">Toggle theme</button></header>
<p class="lede">Each concept large, at 32px, and at 16px. <b>The 16px column decides things</b> —
it is the size a favicon actually renders at. Click a card to flag it; the selection is listed
at the bottom of the page.</p>
${groups.map((g) => `<h2>${esc(g)}</h2><div class="grid">${concepts.filter((c) => c.group === g).map(card).join('')}</div>`).join('\n')}
<div id="picked">picked: (none)</div>
<script>
 document.getElementById('t').onclick = () => {
   const r = document.documentElement;
   r.dataset.theme = r.dataset.theme === 'dark' ? 'light' : 'dark';
 };
 const out = document.getElementById('picked');
 document.querySelectorAll('.card').forEach((c) => c.addEventListener('click', () => {
   c.classList.toggle('pick');
   const ids = [...document.querySelectorAll('.card.pick')].map((n) => n.dataset.id);
   out.textContent = 'picked: ' + (ids.join(', ') || '(none)');
   console.log('picked:', ids.join(', ') || '(none)');
 }));
</script>
</body>
</html>
`;

const out = join(dir, 'index.html');
writeFileSync(out, html);
console.log(`${concepts.length} concept(s) in ${groups.length} group(s) -> ${out}`);

if (noServe) process.exit(0);

/*
 * Served rather than opened as a file:// URL. Headless browsers block that
 * scheme, so a static server is the only way an agent can screenshot the sheet
 * it just built — and reviewing the sheet is the entire point.
 */
const TYPES = { '.html': 'text/html', '.svg': 'image/svg+xml', '.json': 'application/json' };

/*
 * Compared with a trailing separator. A bare `startsWith(dir)` also matches any
 * sibling whose name merely begins with the same string — with `dir` at
 * `/tmp/logo`, a request for `../logo-private/secret` resolves to
 * `/tmp/logo-private/secret` and passes. The separator makes the check mean
 * "inside this directory" rather than "starts with these characters".
 */
const root = dir.endsWith(sep) ? dir : dir + sep;

createServer((req, res) => {
	const rel = req.url === '/' ? 'index.html' : decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
	const file = resolve(dir, rel);
	if (file !== dir && !file.startsWith(root)) {
		res.writeHead(403);
		res.end('forbidden');
		return;
	}
	let body;
	try {
		body = readFileSync(file);
	} catch {
		res.writeHead(404);
		res.end('not found');
		return;
	}
	res.writeHead(200, { 'Content-Type': TYPES[extname(file)] ?? 'application/octet-stream' });
	res.end(body);
	// Loopback only. This serves a scratch directory to whoever is designing the
	// mark; there is no reason for it to be reachable from the rest of the network.
}).listen(port, '127.0.0.1', () => console.log(`http://localhost:${port}/`));
