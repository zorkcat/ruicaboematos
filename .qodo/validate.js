const fs = require("fs");
const path = "c:\\Users\\User\\Desktop\\website real\\index.html";
const html = fs.readFileSync(path, "utf8");

const out = [];

// 1. Extraer scripts inline e comprobar sintaxis
const scripts = [...html.matchAll(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g)];
scripts.forEach((m, i) => {
  const type = (m[0].match(/type="([^"]+)"/) || [])[1] || "application/javascript";
  if (type.includes("json")) {
    try { JSON.parse(m[1]); out.push("JSON-LD ok"); }
    catch (e) { out.push("JSON-LD ERROR: " + e.message); }
    return;
  }
  try {
    new Function(m[1]);
    out.push("JS script #" + i + " syntax OK (" + m[1].length + " chars)");
  } catch (e) {
    out.push("JS script #" + i + " SYNTAX ERROR: " + e.message);
  }
});

// 2. IDs duplicados e âncoras
const ids = [...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
const seen = new Set(); const dups = new Set();
ids.forEach(id => { if (seen.has(id)) dups.add(id); seen.add(id); });
const anchors = [...html.matchAll(/href="#([^"]+)"/g)].map(m => m[1]);
const missing = [...new Set(anchors.filter(a => !seen.has(a)))];
out.push("IDs: " + ids.length + " | dups: " + [...dups].join(",") + " | âncoras rotas: " + missing.join(","));

// 3. Classes HTML vs CSS
const cssPath = "c:\\Users\\User\\Desktop\\website real\\style.css";
const css = fs.readFileSync(cssPath, "utf8");
const htmlClasses = new Set();
for (const m of html.matchAll(/class="([^"]+)"/g)) {
  m[1].split(/\s+/).forEach(c => { if (c && !c.startsWith("fa-") && c !== "fas" && c !== "fab") htmlClasses.add(c); });
}
// classes adiccionadas por JS
for (const c of ["badge-new","sold-label","new-status","used-status","sold-status","position-center","position-left","position-right","position-left-far","position-right-far","position-hidden","is-visible","mobile-open","scrolled","nav-clicked","is-loading","filter-tag","show","running"]) htmlClasses.add(c);
const missingCss = [...htmlClasses].filter(c => !css.includes("." + c)).sort();
out.push("Classes sen CSS: [" + missingCss.join(", ") + "]");

// 4. Balance básico de tags (non void comúns)
const voidTags = ["area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr","path","circle","rect","iframe"];
const stack = [];
const tagRe = /<\/?([a-zA-Z0-9]+)(?:\s[^>]*?)?\s*\/?>/g;
let m;
const errors = [];
while ((m = tagRe.exec(html))) {
  const full = m[0];
  const tag = m[1].toLowerCase();
  if (voidTags.includes(tag)) continue;
  if (full.startsWith("</")) {
    const top = stack.pop();
    if (top !== tag) errors.push("mismatch: </" + tag + "> quere pechar <" + top + "> preto da posición " + m.index);
  } else if (!full.endsWith("/>")) {
    stack.push(tag);
  }
}
out.push("Tags sen pechar ao final: " + JSON.stringify(stack) + (stack.length ? " | erros: " + errors.slice(0, 5).join(" ; ") : ""));

fs.writeFileSync("c:\\Users\\User\\Desktop\\website real\\.qodo\\validate.txt", out.join("\n"), "utf8");
console.log(out.join("\n"));