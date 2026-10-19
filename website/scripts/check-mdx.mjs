// Compile every docs page with plain MDX + GFM and parse its frontmatter:
// catches syntax errors that break the whole dev server. `npm run check`.
import { compile } from '@mdx-js/mdx';
import remarkGfm from 'remark-gfm';
import { parse } from 'yaml';
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2];
let bad = 0;
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.mdx') ? [path.join(d, e.name)] : []);
for (const f of walk(root)) {
  const src = fs.readFileSync(f, 'utf8');
  const m = src.match(/^---\n([\s\S]*?)\n---\n/);
  try { if (m) parse(m[1]); } catch (e) { bad++; console.log(`${f}: frontmatter: ${e.message.split('\n')[0]}`); }
  try { await compile(m ? src.slice(m[0].length) : src, { remarkPlugins: [remarkGfm] }); }
  catch (e) { bad++; console.log(`${f}: ${e.message.split('\n')[0]}`); }
}
console.log(bad ? `${bad} errors` : 'all ok');
