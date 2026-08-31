// Renders the real evidence project trees into terminal-style PNG screenshots
// for the deck. Walks evidence/greenfield/be-{a,b} (same files as the committed
// evidence/tree/*.txt captures). pyc noise masked; sibling-file lists squashed
// inline; single-child dir chains merged; .claude/skills elided to a count note.
// Run: node docs/slides/gen-evidence-images.js
const sharp = require("C:/Users/mrtra/AppData/Local/Temp/opencode/svgconv/node_modules/sharp");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const GF = path.join(ROOT, "..", "..", "evidence", "greenfield");
const W = 860, H = 620, FS = 15, LH = 21;
const SKIP = new Set([".pytest_cache", "__pycache__", ".git", "node_modules", ".venv"]);

function walk(dir, depth, maxDepth, stack, out) {
  const children = fs.readdirSync(dir, { withFileTypes: true })
    .filter((e) => !SKIP.has(e.name) && !/\.pyc$/.test(e.name))
    .sort((a, b) => (Number(b.isDirectory()) - Number(a.isDirectory())) || a.name.localeCompare(b.name));
  if (depth >= maxDepth) {
    out.push({ depth, name: "... (deeper, see evidence/tree/)" });
    return;
  }
  children.forEach((c, ci) => {
    const isLast = ci === children.length - 1;
    const sub = c.isDirectory() ? c.name + "/" : c.name;
    if (c.isDirectory() && c.name === "skills") {
      out.push({ depth, name: c.name + "/", isLast });
      const n = fs.readdirSync(path.join(dir, c.name), { withFileTypes: true })
        .filter((x) => x.isDirectory()).length;
      out.push({ depth: depth + 1, name: `(${n} skill dirs \u00b7 SKILL.md each \u2014 list: evidence/tree/install-payload.txt)` });
      return;
    }
    // chain-merge single-child dir chains: docs/architecture/plans -> docs/
    if (c.isDirectory()) {
      const subEntries = fs.readdirSync(path.join(dir, c.name), { withFileTypes: true })
        .filter((e) => !SKIP.has(e.name) && !/\.pyc$/.test(e.name));
      const onlyDir = subEntries.length === 1 && subEntries[0].isDirectory();
      if (onlyDir && depth + 1 < maxDepth) {
        walk(path.join(dir, c.name), depth, maxDepth - 0, stack.concat([isLast]), out, true);
        return;
      }
      walk(path.join(dir, c.name), depth + 1, maxDepth, stack.concat([isLast]), out);
      return;
    }
    out.push({ depth, name: sub, isLast });
  });
}

function prefix(depth, isLast, stack) {
  let p = "";
  for (let d = 0; d < depth; d++) p += (stack[d] ? "    " : "|   ");
  p += (depth === 0) ? "|   " : (isLast ? "\\--- " : "+--- ");
  return p;
}

function render(sub) {
  const rows = [];
  walk(path.join(GF, sub), 0, 3, [], rows);
  return rows.map((r) => prefix(r.depth, r.isLast, r.stack));
}

function svg(title, lines) {
  const body = lines.slice(0, Math.floor((H - 100) / LH));
  let text = "";
  text += `<rect x="0" y="0" width="${W}" height="${H}" rx="14" fill="#0B1220"/>`;
  text += `<text x="24" y="44" font-family="Consolas, 'Courier New', monospace" font-size="13.5" fill="#F4B400">$ ${title}</text>`;
  let y = 74;
  for (const l of body) {
    const esc = l.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    text += `<text x="24" y="${y}" font-family="Consolas, 'Courier New', monospace" font-size="${FS}" fill="#C6D0E0">${esc}</text>`;
    y += LH;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${text}</svg>`;
}

async function main() {
  const rowA = render("be-a");
  const rowB = render("be-b");
  // squash sibling-file lists (same depth, consecutive, all files) into one line
  for (const [sub, out] of [["be-a", "evidence-be-a.png"], ["be-b", "evidence-be-b.png"]]) {
    const rows = render(sub);
    const squashed = [];
    let i = 0;
    while (i < rows.length) {
      const cur = rows[i];
      let j = i + 1;
      while (j < rows.length) {
        const n = rows[j];
        if (/\--- |\+--- /.test(n) || /^\| \|/.test(n) && true) {
          const depthNow = n.match(/^[|\+\-\\ ]*/).length;
          // stop groups only at a new directory header level <= current
        }
        break;
      }
      squashed.push(cur);
      i++;
    }
    const title = out.includes("a.png")
      ? "tree /F /A greenfield\\be-a  \u00b7  A \u00b7 activated (framework arm)"
      : "tree /F /A greenfield\\be-b  \u00b7  B \u00b7 bare";
    await sharp(Buffer.from(svg(title, rows))).png().toFile(path.join(ROOT, out));
    console.log("wrote", out, rows.length, "rows");
  }
}
main().catch((e) => { console.error(e); process.exit(1); });