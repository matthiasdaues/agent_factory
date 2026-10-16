// render.js — print a compiled Quarkdown build to PDF and run the render checks.
//
// What: Serves the HTML over local HTTP, waits for Mermaid and paged.js,
//       checks the live page, prints the PDF and checks it for raster images.
// When: Stages 4 and 5 of `publish-docs pdf`, inside the render image.
// By:   pipeline.sh.
//
// Usage: node render.js <html-dir> <pdf-path> <expected.json>
// Exit 0 when every check passes. Exit 1 with one line per failed check;
// the PDF is then removed.

const { chromium } = require('playwright-core');
const { spawnSync } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');

const [htmlDir, pdfPath, expectedPath] = process.argv.slice(2);
const expected = JSON.parse(fs.readFileSync(expectedPath, 'utf8'));
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2', '.woff': 'font/woff' };
const TIMEOUT_MS = 120000;

function serve(root) {
  const server = http.createServer((req, res) => {
    const file = path.join(root, decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
    fs.readFile(file, (err, data) => {
      if (err) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream' });
      res.end(data);
    });
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

// Wait until every Mermaid block has an SVG and the paged.js page count is
// stable, or a page error has occurred.
async function settle(page, errors) {
  const start = Date.now();
  let last = -1, stableSince = Date.now();
  while (Date.now() - start < TIMEOUT_MS) {
    const s = await page.evaluate(() => ({
      pending: [...document.querySelectorAll('.mermaid')].filter(e => !e.querySelector('svg')).length,
      pages: document.querySelectorAll('.pagedjs_page').length,
    }));
    if (s.pages !== last) { last = s.pages; stableSince = Date.now(); }
    if (errors.length && Date.now() - stableSince > 1000) return true;
    if (s.pending === 0 && s.pages > 0 && Date.now() - stableSince > 2000) return true;
    await page.waitForTimeout(250);
  }
  return false;
}

function rasterImages(pdf) {
  const r = spawnSync('pdfimages', ['-list', pdf], { encoding: 'utf8' });
  if (r.status !== 0) return { error: (r.stderr || '').trim() };
  return { count: r.stdout.split('\n').slice(2).filter(l => l.trim().split(/\s+/)[2] === 'image').length };
}

(async () => {
  const server = await serve(path.resolve(htmlDir));
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message || e).split('\n')[0]));
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, { waitUntil: 'networkidle' });
  const settled = await settle(page, errors);

  const live = await page.evaluate(() => {
    const blocks = [...document.querySelectorAll('.mermaid')];
    const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
    return {
      mermaidSvg: blocks.filter(e => e.querySelector('svg')).length,
      errorSvg: [...document.querySelectorAll('svg')].filter(s => /Syntax error/i.test(s.textContent)).length,
      errorBoxes: [...document.querySelectorAll('.box.error')].map(e => e.textContent.trim().replace(/\s+/g, ' ').slice(0, 160)),
      pages: document.querySelectorAll('.pagedjs_page').length,
      deadAnchors: [...new Set([...document.querySelectorAll('a[href^="#"]')]
        .map(a => decodeURIComponent(a.getAttribute('href').slice(1))).filter(h => h && !ids.has(h)))],
      externalLinks: [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => !h.startsWith('#')))],
      brokenImages: [...document.querySelectorAll('img')].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src')),
    };
  });

  const failures = [];
  if (!settled) failures.push(`render-timeout: page did not settle within ${TIMEOUT_MS / 1000} s`);
  if (live.mermaidSvg !== expected.mermaid) failures.push(`mermaid-count: ${live.mermaidSvg} of ${expected.mermaid} diagrams rendered`);
  if (live.errorSvg) failures.push(`mermaid-error: ${live.errorSvg} diagram(s) show a syntax error`);
  for (const e of errors) failures.push(`page-error: ${e}`);
  if (live.pages === 0) failures.push('paged-js: no pages were laid out');
  for (const b of live.errorBoxes) failures.push(`compile-error: ${b}`);
  for (const a of live.deadAnchors) failures.push(`dead-anchor: #${a}`);
  for (const h of live.externalLinks) failures.push(`external-link: ${h}`);
  for (const i of live.brokenImages) failures.push(`broken-image: ${i}`);

  if (failures.length === 0) {
    await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true });
    const raster = rasterImages(pdfPath);
    if (raster.error !== undefined) failures.push(`raster-check: pdfimages failed: ${raster.error}`);
    else if (raster.count > expected.raster) failures.push(`raster-images: ${raster.count} in the PDF, ${expected.raster} expected from the sources`);
  }

  await browser.close();
  server.close();
  if (failures.length) {
    fs.rmSync(pdfPath, { force: true });
    for (const f of failures) console.error(`FAIL ${f}`);
    process.exit(1);
  }
  console.log(`render: ${live.pages} pages, ${live.mermaidSvg} diagrams, all checks passed`);
})().catch(e => { console.error(`FAIL render-crash: ${e.message}`); process.exit(1); });
