const fs = require("fs");
const html = fs.readFileSync("c:\\Users\\User\\Desktop\\website real\\index.html", "utf8");
const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
const refs = new Set([...html.matchAll(/getElementById\(\s*"([^"]+)"/g)].map(m => m[1]));
const queryRefs = new Set([...html.matchAll(/querySelector\(\s*"([^"]+)"/g)].map(m => m[1]));
const missing = [...refs].filter(r => !ids.has(r));
console.log("getElementById refs: " + refs.size + " | faltan: " + missing.join(","));
const missingQ = [...queryRefs].filter(q => {
  const t = q.replace(/^\./, "").replace(/^#/, "");
  return q.startsWith("#") && !ids.has(t);
});
console.log("querySelector # refs sen ID: " + missingQ.join(","));