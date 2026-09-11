const fs = require("fs");
const path = "c:\\Users\\User\\Desktop\\website real\\index.html";
const html = fs.readFileSync(path, "utf8");

const classes = new Set();
for (const m of html.matchAll(/class="([^"]+)"/g)) {
  for (const c of m[1].split(/\s+/)) if (c) classes.add(c);
}
const ids = [...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
const seen = new Set();
const dups = new Set();
for (const id of ids) {
  if (seen.has(id)) dups.add(id);
  seen.add(id);
}
const anchors = [...html.matchAll(/href="#([^"]+)"/g)].map(m => m[1]);
const missing = [...new Set(anchors.filter(a => !seen.has(a)))];

let out = "=== CLASSES (" + classes.size + ") ===\n";
out += [...classes].sort().join("\n") + "\n";
out += "\n=== ID COUNT: " + ids.length + " | DUPS: " + [...dups].join(",") + " ===\n";
out += "=== ANCHORS: " + anchors.length + " | MISSING: " + missing.join(",") + " ===\n";
fs.writeFileSync("c:\\Users\\User\\Desktop\\website real\\.qodo\\audit.txt", out, "utf8");
console.log("OK");