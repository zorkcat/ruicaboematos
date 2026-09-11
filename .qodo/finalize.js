const fs = require("fs");
const path = "c:\\Users\\User\\Desktop\\website real\\index.html";
let html = fs.readFileSync(path, "utf8");
const before = html;
html = html.replace(/loading="eager"/g, "");
if (html === before) console.log("nada que cambiar");
fs.writeFileSync(path, html, "utf8");

// CSS brace balance
const cssPath = "c:\\Users\\User\\Desktop\\website real\\style.css";
const css = fs.readFileSync(cssPath, "utf8");
let depth = 0, line = 1, problem = -1;
for (const ch of css) {
  if (ch === "\n") line++;
  if (ch === "{") depth++;
  if (ch === "}") { depth--; if (depth < 0 && problem === -1) problem = line; }
}
console.log("CSS depth final: " + depth + " | problema linha: " + problem);
// comentarios non pechados
const openComms = (css.match(/\/\*/g) || []).length;
const closeComms = (css.match(/\*\//g) || []).length;
console.log("comentários CSS abertos: " + openComms + " | pechados: " + closeComms);