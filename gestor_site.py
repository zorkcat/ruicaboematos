# -*- coding: utf-8 -*-
"""Gestor do site Rui Cabo & Matos — HUD local.

Painel (no browser) para ver, criar e editar veículos/máquinas do stock e
regenerar o site completo num clique.

Como usar:
    python gestor_site.py

Depois abra:  http://127.0.0.1:8500        (site real, para pré-visualizar)
            http://127.0.0.1:8500/admin    (gestor / HUD)

O stock fica em stock.json e o gerador usa esse ficheiro como fonte.
"""
import base64
import io
import json
import mimetypes
import os
import re
import shutil
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import gerar_produtos as GP

PORT = int(os.environ.get("RCM_PORT", "8500"))
HOST = "127.0.0.1"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
STOCK_PATH = os.path.join(BASE, "stock.json")


def _clean_product(p):
    """Copia apenas os campos geridos pelo utilizador para o stock.json."""
    keys = ["id", "category", "brand", "model", "status", "sold", "available",
            "image", "power", "drive", "hours", "year", "fuel", "price",
            "priceLabel", "description", "features", "metaTitle", "metaDesc"]
    out = {}
    for k in keys:
        if k in p:
            v = p[k]
            if isinstance(v, str):
                v = v.strip()
            out[k] = v
    return out


def load_stock():
    """Lista de produtos normalizada (gerar_produtos enriquece os números/derivados)."""
    items = []
    try:
        with open(STOCK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            items = [GP.normalize_product(x) for x in data]
    except (OSError, ValueError):
        items = [GP.normalize_product(p) for p in GP.PRODUTOS]

    seen = set()
    nxt = max([it.get("id") or 0 for it in items] + [0]) + 1
    for it in items:
        pid = it.get("id")
        if not pid or pid in seen:
            it["id"] = nxt
            nxt += 1
        seen.add(it["id"])
    return items


def save_stock(items):
    clean = [_clean_product(it) for it in items]
    with open(STOCK_PATH, "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)


def regenerate(buf):
    items = load_stock()
    old = sys.stdout
    sys.stdout = buf
    try:
        GP.generate(items)
    finally:
        sys.stdout = old
    return items


def rm_product_folder(slug):
    folder = os.path.join(BASE, "trator", slug or "")
    if folder != os.path.join(BASE, "trator") and os.path.isdir(folder):
        shutil.rmtree(folder)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, status, ctype, body):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(status, "application/json; charset=utf-8", body)

    def _read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _serve_file(self, path):
        rel = path.lstrip("/")
        if not rel:
            rel = "index.html"
        full = os.path.abspath(os.path.join(BASE, rel))
        if full != BASE and not full.startswith(BASE + os.sep):
            return self._json({"ok": False, "error": "Acesso negado"}, 403)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not os.path.isfile(full):
            return self._json({"ok": False, "error": "Não encontrado"}, 404)
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            body = f.read()
        self._send(200, ctype, body)

    # -------------------------------------------------- GET
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/admin", "/admin/", "/gestor", "/gestor/"):
            return self._send(200, "text/html; charset=utf-8", ADMIN_PAGE.encode("utf-8"))
        if path == "/api/stock":
            return self._json({"ok": True, "items": load_stock()})
        if path == "/api/images":
            names = sorted(
                f for f in os.listdir(BASE)
                if os.path.isfile(os.path.join(BASE, f))
                and os.path.splitext(f)[1].lower() in IMG_EXT
            )
            return self._json({"ok": True, "images": names})
        return self._serve_file(path)

    # -------------------------------------------------- POST
    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            data = json.loads(self._read_body().decode("utf-8", "replace") or "{}")
        except ValueError:
            return self._json({"ok": False, "error": "JSON inválido"}, 400)

        if path == "/api/save":
            product = GP.normalize_product(data.get("product") or {})
            items = load_stock()
            pid = product.get("id")
            if not pid:
                pid = (max([it.get("id") or 0 for it in items], default=0)) + 1
                product["id"] = pid
            idx = next((i for i, it in enumerate(items) if it.get("id") == pid), None)
            if idx is None:
                items.append(product)
            else:
                items[idx] = product
            save_stock(items)
            buf = io.StringIO()
            regenerate(buf)
            return self._json({
                "ok": True,
                "product": product,
                "log": buf.getvalue().splitlines(),
            })

        if path == "/api/delete":
            pid = data.get("id")
            old_slug = data.get("slug")
            items = [it for it in load_stock() if it.get("id") != pid]
            save_stock(items)
            buf = io.StringIO()
            regenerate(buf)
            rm_product_folder(old_slug)
            return self._json({"ok": True, "log": buf.getvalue().splitlines()})

        if path == "/api/regenerate":
            buf = io.StringIO()
            items = regenerate(buf)
            return self._json({
                "ok": True,
                "count": len(items),
                "log": buf.getvalue().splitlines(),
            })

        if path == "/api/upload":
            name = os.path.basename(data.get("name") or "")
            blob = base64.b64decode(data.get("data") or "")
            if not re.match(r"^[A-Za-z0-9 _\-\(\)]+\.(jpg|jpeg|png|webp|avif|gif)$", name, re.I):
                return self._json({"ok": False, "error": "Nome de ficheiro inválido"})
            with open(os.path.join(BASE, name), "wb") as f:
                f.write(blob)
            return self._json({"ok": True, "name": name})

        return self._json({"ok": False, "error": "Rota inválida"}, 404)


ADMIN_PAGE = r"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gestor · Rui Cabo & Matos</title>
<style>
:root{
  --bg:#0C1A11; --panel:#122415; --panel-2:#182E1C; --line:#28402E;
  --txt:#EAF2EC; --txt-2:#C9D9CD; --txt-3:#98AB9D;
  --brand:#4CBB63; --brand-2:#3D9B4A; --grad-1:#1B5727; --grad-2:#3D9B4A;
  --danger:#E56B5D; --wa:#25D366;
  --r:12px; --r-sm:8px;
  --shadow:0 12px 32px rgba(0,0,0,.4);
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:"Segoe UI",system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--txt);font-size:14px;overflow:hidden}
button{font:inherit;cursor:pointer;border:0;background:none;color:inherit}
input,select,textarea{font:inherit;color:var(--txt);background:var(--bg);border:1px solid var(--line);border-radius:var(--r-sm);padding:9px 11px;width:100%;outline:none;transition:border-color .15s}
input:focus,select:focus,textarea:focus{border-color:var(--brand)}
textarea{resize:vertical;min-height:96px}
label{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--txt-3);margin:14px 0 6px}
.hint{font-size:11.5px;color:var(--txt-3);margin-top:4px;line-height:1.5}

/* ============ LAYOUT ============ */
.app{display:grid;grid-template-columns:236px 1fr;height:100dvh}
.sidebar{background:var(--panel);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:18px 14px;min-height:0}
.brand{display:flex;align-items:center;gap:10px;padding:2px 6px 16px;border-bottom:1px solid var(--line)}
.brand-mark{width:38px;height:38px;display:grid;place-items:center;border-radius:10px;background:linear-gradient(135deg,var(--grad-1),var(--grad-2));color:#fff;font-size:15px;font-weight:800;flex-shrink:0}
.brand-name strong{display:block;font-size:14px;font-weight:800;letter-spacing:.02em}
.brand-name span{display:block;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--brand);font-weight:700}
.side-nav{display:flex;flex-direction:column;gap:4px;padding-top:14px;flex:1}
.side-link{display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:var(--r-sm);color:var(--txt-2);font-weight:600;font-size:13.5px;transition:all .15s}
.side-link:hover{background:var(--panel-2);color:#fff}
.side-link.active{background:var(--panel-2);color:#fff;box-shadow:inset 3px 0 0 var(--brand)}
.side-link i{width:18px;text-align:center;color:var(--txt-3)}
.side-link:hover i,.side-link.active i{color:var(--brand)}
.side-foot{display:flex;flex-direction:column;gap:8px;padding-top:12px;border-top:1px solid var(--line)}
.side-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:42px;border-radius:var(--r-sm);font-weight:700;font-size:13px;transition:all .15s}
.side-btn.outline{background:var(--panel-2);color:var(--txt)}
.side-btn.outline:hover{background:var(--panel);border:1px solid var(--line)}
.side-btn.primary{background:linear-gradient(135deg,var(--grad-1),var(--grad-2));color:#fff}
.side-btn.primary:hover{filter:brightness(1.1)}
.side-btn.danger:hover{background:rgba(229,107,93,.12);color:var(--danger)}
.server-state{font-size:10.5px;color:var(--txt-3);text-align:center}

/* ============ MAIN ============ */
.main{display:flex;flex-direction:column;min-height:0}
.topbar{display:flex;align-items:center;gap:12px;padding:14px 22px;border-bottom:1px solid var(--line);background:var(--panel);flex-wrap:wrap}
.topbar h1{font-size:17px;font-weight:800;margin-right:auto;display:flex;align-items:center;gap:10px}
.topbar h1 .count{font-size:11px;font-weight:700;color:var(--brand);background:rgba(76,187,99,.12);padding:3px 9px;border-radius:999px}
.search{position:relative;width:min(340px,100%)}
.search i{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--txt-3);font-size:12px;pointer-events:none}
.search input{padding-left:33px}
.cats{display:flex;gap:6px;flex-wrap:wrap}
.cat-pill{min-height:34px;padding:0 14px;border-radius:999px;background:var(--panel-2);color:var(--txt-2);font-size:12.5px;font-weight:700;transition:all .15s;border:1px solid transparent}
.cat-pill:hover{color:#fff}
.cat-pill.active{background:linear-gradient(135deg,var(--grad-1),var(--grad-2));color:#fff}
.topbar .btn-new{display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:0 16px;border-radius:var(--r-sm);background:var(--brand);color:#0A1A0E;font-weight:800;font-size:13px;transition:all .15s}
.topbar .btn-new:hover{filter:brightness(1.1)}

/* ============ GRID ============ */
.content{flex:1;overflow-y:auto;padding:22px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;cursor:pointer;transition:all .18s ease;display:flex;flex-direction:column}
.card:hover{transform:translateY(-3px);border-color:var(--brand);box-shadow:var(--shadow)}
.card-img{position:relative;aspect-ratio:4/3;background:#0A120C;overflow:hidden}
.card-img img{width:100%;height:100%;object-fit:cover;transition:opacity .25s}
.card-img .no-img{display:grid;place-items:center;width:100%;height:100%;color:var(--txt-3);font-size:30px}
.card-img .no-img i{opacity:.5}
.badges{position:absolute;top:10px;left:10px;display:flex;gap:6px}
.badge{font-size:9.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#fff;padding:3px 9px;border-radius:999px}
.badge-new{background:linear-gradient(90deg,var(--grad-1),var(--grad-2))}
.badge-used{background:#5A6B5E}
.badge-sold{background:#23342A}
.badge-cat{background:rgba(0,0,0,.45);backdrop-filter:blur(3px)}
.card-body{padding:13px 14px 14px;display:flex;flex-direction:column;gap:7px;flex:1}
.card-title{font-size:14.5px;font-weight:800;line-height:1.25;display:flex;align-items:center;gap:8px;justify-content:space-between}
.card-title small{font-weight:700;color:var(--txt-3);font-size:11px}
.card-spec{display:flex;gap:6px;font-size:11.5px;color:var(--txt-2)}
.card-spec span{display:inline-flex;align-items:center;gap:5px;background:var(--panel-2);padding:3px 8px;border-radius:999px}
.card-spec i{color:var(--brand);font-size:9.5px}
.card-foot{margin-top:auto;display:flex;align-items:center;justify-content:space-between;padding-top:10px;border-top:1px solid var(--line)}
.price{font-weight:800;font-size:14px;color:var(--brand)}
.price small{display:block;font-size:10px;color:var(--txt-3);font-weight:600}
.card-foot .btn-edit{min-height:30px;padding:0 11px;border-radius:var(--r-sm);background:var(--panel-2);color:#fff;font-size:11.5px;font-weight:700}
.card-foot .btn-edit:hover{background:var(--brand);color:#0A1A0E}
.empty{grid-column:1/-1;text-align:center;padding:60px 20px;color:var(--txt-3);border:1px dashed var(--line);border-radius:var(--r)}
.empty i{font-size:34px;opacity:.5;margin-bottom:12px}
.empty strong{display:block;font-size:15px;color:var(--txt-2);margin-bottom:4px}

/* ============ EDITOR (slide-over) ============ */
.overlay{position:fixed;inset:0;background:rgba(4,10,6,.6);backdrop-filter:blur(2px);z-index:50;opacity:0;visibility:hidden;transition:opacity .2s}
.overlay.open{opacity:1;visibility:visible}
.editor{position:fixed;top:0;right:0;bottom:0;width:min(560px,100%);background:var(--panel);border-left:1px solid var(--line);z-index:51;display:flex;flex-direction:column;transform:translateX(105%);transition:transform .28s cubic-bezier(.22,.9,.3,1);box-shadow:-20px 0 50px rgba(0,0,0,.5)}
.editor.open{transform:none}
.editor-head{display:flex;align-items:center;gap:12px;padding:16px 18px;border-bottom:1px solid var(--line);flex-shrink:0}
.editor-head .dot{width:10px;height:10px;border-radius:50%;background:var(--brand);box-shadow:0 0 0 4px rgba(76,187,99,.15)}
.editor-head strong{font-size:15px;font-weight:800}
.editor-head span{display:block;font-size:11px;color:var(--txt-3)}
.editor-head .x{margin-left:auto;width:32px;height:32px;border-radius:50%;background:var(--panel-2);color:var(--txt-2);font-size:14px}
.editor-head .x:hover{color:#fff;background:#2A3A2E}
.editor-body{flex:1;overflow-y:auto;padding:4px 20px 24px}
.field-group{border:1px solid var(--line);border-radius:var(--r);padding:2px 16px 14px;margin-top:16px;background:var(--panel-2)}
.field-group>h3{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--brand);padding-top:12px}
.field-group>h3 i{font-size:11px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.row3-2{display:grid;grid-template-columns:2fr 1fr;gap:10px}

/* estado pills */
.status-pills{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}
.status-pill{min-height:40px;border-radius:var(--r-sm);background:var(--bg);border:1px solid var(--line);font-weight:700;font-size:12.5px;color:var(--txt-2);transition:all .15s}
.status-pill:hover{color:#fff}
.status-pill.active{padding-left:10px;border-color:transparent;color:#fff}
.status-pill[data-st="Novo"].active{background:linear-gradient(135deg,var(--grad-1),var(--grad-2))}
.status-pill[data-st="Usado"].active{background:#5A6B5E}
.status-pill[data-st="Vendido"].active{background:#23342A}

/* imagem */
.img-row{display:grid;grid-template-columns:96px 1fr;gap:12px;align-items:start;margin-top:10px}
.img-preview{width:96px;height:72px;border-radius:var(--r-sm);overflow:hidden;background:#0A120C;display:grid;place-items:center}
.img-preview img{width:100%;height:100%;object-fit:cover}
.img-actions{display:flex;flex-direction:column;gap:8px}
.img-upload{display:flex;gap:8px;align-items:center}
.img-upload label{all:unset;display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:0 13px;border:1px dashed var(--line);border-radius:var(--r-sm);color:var(--txt-2);font-size:12px;font-weight:700;cursor:pointer;flex:1;justify-content:center}
.img-upload label:hover{border-color:var(--brand);color:#fff}
.img-upload input{display:none}

/* features */
.feats-row{display:flex;gap:8px;margin-top:10px}
.feats-row input{flex:1}
.feats-row button{min-height:38px;padding:0 15px;border-radius:var(--r-sm);background:var(--panel);color:var(--brand);font-weight:800;border:1px solid var(--line);flex-shrink:0}
.feats-row button:hover{border-color:var(--brand)}
.chip-list{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}
.chip{display:inline-flex;align-items:center;gap:7px;background:var(--bg);border:1px solid var(--line);color:var(--txt-2);padding:5px 9px 5px 11px;border-radius:999px;font-size:12px;font-weight:600}
.chip b{color:#fff}
.chip button{width:18px;height:18px;border-radius:50%;background:var(--panel-2);color:var(--txt-3);font-size:10px;display:grid;place-items:center}
.chip button:hover{background:var(--danger);color:#fff}

.editor-foot{display:flex;gap:10px;padding:14px 18px 16px;border-top:1px solid var(--line);flex-shrink:0;background:var(--panel);flex-wrap:wrap}
.editor-foot .grow{flex:1}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:44px;padding:0 18px;border-radius:var(--r-sm);font-weight:800;font-size:13.5px;transition:all .15s}
.btn.primary{background:linear-gradient(135deg,var(--grad-1),var(--grad-2));color:#fff;flex:1}
.btn.primary:hover{filter:brightness(1.12)}
.btn.primary:disabled{opacity:.5;cursor:wait}
.btn.ghost{background:var(--panel-2);color:var(--txt)}
.btn.ghost:hover{color:#fff}
.btn.danger{color:var(--danger)}
.btn.danger:hover{background:rgba(229,107,93,.13)}

/* toast */
.toast-wrap{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);z-index:99;display:flex;flex-direction:column;gap:8px;align-items:center;pointer-events:none}
.toast{background:var(--panel-2);border:1px solid var(--line);color:var(--txt);padding:11px 18px;border-radius:10px;font-size:13px;font-weight:600;box-shadow:var(--shadow);display:flex;gap:9px;align-items:center;max-width:min(92vw,520px)}
.toast.ok i{color:var(--brand)}
.toast.err i{color:var(--danger)}
.toast small{display:block;font-weight:400;color:var(--txt-3);font-size:11px;margin-top:2px}

@media(max-width:820px){
  .app{grid-template-columns:1fr}
  .sidebar{display:none}
  .grid{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
}
</style>
</head>
<body>
<div class="app">

  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">RC</div>
      <div class="brand-name">
        <strong>RUI CABO &amp; MATOS</strong>
        <span>Painel de gestão</span>
      </div>
    </div>
    <nav class="side-nav">
      <button class="side-link active" onclick="reloadStock()"><i class="fas fa-box-open"></i> Stock e veículos</button>
      <button class="side-link" onclick="scrollTopAdmin()"><i class="fas fa-gauge-high"></i> Resumo</button>
    </nav>
    <div class="side-foot">
      <a class="side-btn outline" href="/" target="_blank"><i class="fas fa-eye"></i> Abrir o site</a>
      <button class="side-btn primary" onclick="regenSite()" id="regenBtn"><i class="fas fa-wand-magic-sparkles"></i> Regenerar site</button>
      <span class="server-state" id="serverState">A preparar…</span>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <h1>Stock e veículos <span class="count" id="stockCount">0</span></h1>
      <div class="search"><i class="fas fa-magnifying-glass"></i><input id="q" placeholder="Procurar marca ou modelo…" oninput="renderGrid()"></div>
      <button class="cat-pill" data-cat="" onclick="setCat(this)">Todos</button>
      <button class="cat-pill" data-cat="Trator" onclick="setCat(this)">Tratores</button>
      <button class="cat-pill" data-cat="Veículo" onclick="setCat(this)">Veículos</button>
      <button class="btn-new" onclick="openEditor(null)"><i class="fas fa-plus"></i> Novo veículo</button>
    </div>
    <div class="content">
      <div class="grid" id="grid"></div>
    </div>
  </main>
</div>

<!-- EDITOR -->
<div class="overlay" id="overlay" onclick="closeEditor()"></div>
<aside class="editor" id="editor" role="dialog" aria-modal="true" aria-label="Editar veículo">
  <div class="editor-head">
    <div class="dot"></div>
    <div>
      <strong id="editTitle">Novo veículo</strong>
      <span id="editSub">Os campos com * são obrigatórios</span>
    </div>
    <button class="x" onclick="closeEditor()" aria-label="Fechar"><i class="fas fa-times"></i></button>
  </div>
  <div class="editor-body">
    <input type="hidden" id="f_id">

    <div class="field-group">
      <h3><i class="fas fa-image"></i> Fotografia</h3>
      <div class="img-row">
        <div class="img-preview" id="imgPreview"><i class="fas fa-image" style="color:#3a4a3e"></i></div>
        <div class="img-actions">
          <select id="f_image" onchange="previewImage()"></select>
          <div class="img-upload"><label for="filePick"><i class="fas fa-upload"></i> Carregar nova foto…</label><input type="file" id="filePick" accept=".jpg,.jpeg,.png,.webp,.avif,.gif" onchange="handleUpload(this.files[0])"></div>
        </div>
      </div>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-tag"></i> Identificação</h3>
      <label>Categoria *</label>
      <input id="f_category" list="cats" value="Trator" oninput="refreshCats()">
      <datalist id="cats">
        <option value="Trator"><option value="Veículo"><option value="Reboque"><option value="Máquina"><option value="Acessório">
      </datalist>
      <div class="hint" id="catHint"></div>
      <div class="row2">
        <div><label>Marca *</label><input id="f_brand" placeholder="Ex.: Massey Ferguson"></div>
        <div><label>Modelo *</label><input id="f_model" placeholder="Ex.: 5610"></div>
      </div>
      <label>Estado</label>
      <div class="status-pills" id="statusPills">
        <button type="button" class="status-pill" data-st="Novo" onclick="setStatus('Novo')">Novo</button>
        <button type="button" class="status-pill" data-st="Usado" onclick="setStatus('Usado')">Usado</button>
        <button type="button" class="status-pill" data-st="Vendido" onclick="setStatus('Vendido')">Vendido</button>
      </div>
      <div class="hint" id="availHint">Disponível para venda</div>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-sliders"></i> Características principais</h3>
      <div class="row3-2"><div><label>Potência</label><input id="f_power" placeholder="Ex.: 85 CV"></div><div><label>Tração</label><input id="f_drive" placeholder="Ex.: 4WD"></div></div>
      <div class="row3"><div><label>Horas</label><input id="f_hours" placeholder="Ex.: 1.250 h"></div><div><label>Ano</label><input id="f_year" placeholder="Ex.: 2015"></div><div><label>Combustível</label><input id="f_fuel" placeholder="Gasóleo"></div></div>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-euro-sign"></i> Preço</h3>
      <div class="row3-2"><div><label>Valor</label><input id="f_price" placeholder="Ex.: 12.500 €"></div><div><label>Condição</label><select id="f_priceLabel"><option>+ IVA</option><option>Com IVA</option></select></div></div>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-align-left"></i> Descrição</h3>
      <textarea id="f_description" placeholder="Descreva o equipamento: estado, extras, o que inclui…"></textarea>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-tags"></i> Características extra <span style="opacity:.6;font-weight:600">(chips)</span></h3>
      <div class="feats-row"><input id="f_featInput" placeholder="Ex.: Direção assistida" onkeydown="if(event.key==='Enter'){event.preventDefault();addFeat()}"><button onclick="addFeat()">Adicionar</button></div>
      <div class="chip-list" id="featList"></div>
      <div class="hint">A tração e o combustível são adicionados automaticamente.</div>
    </div>

    <div class="field-group">
      <h3><i class="fas fa-magnifying-glass-chart"></i> SEO / Meta</h3>
      <label>Título da página <span style="text-transform:none;color:var(--txt-3)">(opcional)</span></label>
      <input id="f_metaTitle" placeholder="Auto: «Marca Modelo (85 CV) | Rui Cabo & Matos, LDA»">
      <label>Descrição meta <span style="text-transform:none;color:var(--txt-3)">(opcional)</span></label>
      <textarea id="f_metaDesc" placeholder="Auto: gerada a partir das características e do preço"></textarea>
    </div>
  </div>

  <div class="editor-foot">
    <button class="btn ghost" onclick="deleteCurrent()" id="delBtn"><i class="fas fa-trash-can"></i></button>
    <button class="btn ghost" onclick="duplicateCurrent()" id="dupBtn"><i class="fas fa-copy"></i></button>
    <button class="btn danger" onclick="closeEditor()">Cancelar</button>
    <button class="btn primary" onclick="saveProduct()" id="saveBtn"><i class="fas fa-floppy-disk"></i> Guardar &amp; gerar site</button>
  </div>
</aside>

<div class="toast-wrap" id="toasts"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/js/all.min.js"></script>
<script>
var items=[], selectedId=null, selectedStatus="Novo", catFilter="", feats=[];
var $=function(id){return document.getElementById(id);};

function toast(msg,type,extra){
  var t=document.createElement("div");
  t.className="toast "+(type||"ok");
  t.innerHTML='<i class="fas '+(type==="err"?"fa-circle-exclamation":"fa-circle-check")+'"></i><div>'+msg+(extra?'<small>'+extra+'</small>':'')+'</div>';
  $("toasts").appendChild(t);
  setTimeout(function(){t.remove();},6000);
}
function esc(s){if(s===null||s===undefined)return"";return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function priceLabel(l){return (l||"").indexOf("Com IVA")>=0?"Preço com IVA":"Preço sem IVA";}

async function api(url,opts){
  var r=await fetch(url,opts);
  return r.json();
}
async function loadImages(){
  var d=await api("/api/images");
  if(d.ok)renderImageSelect(d.images);
}
function renderImageSelect(list){
  var sel=$("f_image"),cur=sel.value;
  sel.innerHTML='<option value="">Sem foto</option>';
  list.forEach(function(n){
    var o=document.createElement("option");o.value=n;o.textContent=n;
    if(n===cur)o.selected=true;
    sel.appendChild(o);
  });
}
function previewImage(){
  var n=$("f_image").value;
  $("imgPreview").innerHTML=n?'<img src="'+esc(n)+'" alt="">':'<i class="fas fa-image" style="color:#3a4a3e"></i>';
}
async function handleUpload(file){
  if(!file)return;
  var valid=/\.(jpg|jpeg|png|webp|avif|gif)$/i.test(file.name);
  if(!valid)return toast("Formato não suportado","err","Use JPG, PNG, WebP ou AVIF.");
  var reader=new FileReader();
  reader.onload=async function(){
    var b=reader.result.split(",")[1];
    $("saveBtn").disabled=true;
    var d=await api("/api/upload",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:file.name,data:b})});
    $("saveBtn").disabled=false;
    if(d.ok){await loadImages();$("f_image").value=d.name;previewImage();toast("Foto carregada","ok","Guardar para aplicar no site.");}
    else toast(d.error||"Erro no upload","err");
  };
  reader.readAsDataURL(file);
}

function setCat(btn){catFilter=btn.dataset.cat;document.querySelectorAll(".cat-pill").forEach(function(b){b.classList.toggle("active",b===btn)});renderGrid();}
function setStatus(s){selectedStatus=s;document.querySelectorAll(".status-pill").forEach(function(b){b.classList.toggle("active",b.dataset.st===s)});updateAvail();}
function updateAvail(){
  var n=selectedStatus==="Vendido"?"Não disponível — já vendido":"Disponível para venda";
  $("availHint").textContent="Disponibilidade: "+n;
}
function renderGrid(){
  var q=$("q").value.trim().toLowerCase();
  $("stockCount").textContent=items.length;
  var g=$("grid");g.innerHTML="";
  var list=items.filter(function(it){
    var okCat=!catFilter||(it.category||"")===catFilter;
    var hay=(it.brand+" "+it.model+" "+(it.category||"")+" "+it.status).toLowerCase();
    return okCat&&(!q||hay.indexOf(q)>=0);
  });
  if(!list.length){
    g.innerHTML='<div class="empty"><i class="fas fa-box-open"></i><strong>Sem resultados</strong>Procure por marca/modelo ou limpe os filtros.</div>';
    return;
  }
  list.forEach(function(it){
    var img=it.image?'<img src="'+esc(it.image)+'" loading="lazy" onerror="this.outerHTML=\'<div class=no-img><i class=fas fa-tractor></i></div>\'" alt="">':'<div class="no-img"><i class="fas fa-tractor"></i></div>';
    var bCls=it.status==="Novo"?"badge-new":(it.status==="Vendido"?"badge-sold":"badge-used");
    var div=document.createElement("div");
    div.className="card";
    div.innerHTML='<div class="card-img"><div class="badges"><span class="badge '+bCls+'">'+esc(it.status)+'</span><span class="badge badge-cat">'+esc(it.category||"Trator")+'</span></div>'+img+'</div>'+
      '<div class="card-body"><div class="card-title">'+esc(it.brand)+' '+esc(it.model)+' <small>'+esc(it.hours||"—")+'</small></div>'+
      '<div class="card-spec"><span><i class="fas fa-horse"></i>'+esc(it.power||"—")+'</span><span><i class="fas fa-calendar"></i>'+esc(it.year||"—")+'</span><span><i class="fas fa-gas-pump"></i>'+esc(it.fuel||"—")+'</span></div>'+
      '<div class="card-foot"><div class="price">'+esc(it.price==="—"?"—":it.price)+'<small>'+priceLabel(it.priceLabel)+'</small></div><button class="btn-edit" onclick="openEditor('+it.id+')"><i class="fas fa-pen"></i> Editar</button></div></div>';
    div.querySelector(".card-img").addEventListener("click",function(){openEditor(it.id)});
    g.appendChild(div);
  });
}
function reloadStock(){
  api("/api/stock").then(function(d){if(d.ok){items=d.items;renderGrid();}});
}
function refreshCats(){}

function openEditor(id){
  selectedId=id;
  var it=id?items.find(function(x){return x.id===id}):null;
  $("editTitle").textContent=it?(it.brand+" "+it.model):"Novo veículo";
  $("delBtn").style.display=it?"inline-flex":"none";
  $("dupBtn").style.display=it?"inline-flex":"none";
  $("f_id").value=it?it.id:"";
  $("f_category").value=(it&&it.category)||"Trator";
  $("f_brand").value=(it&&it.brand)||"";
  $("f_model").value=(it&&it.model)||"";
  $("f_power").value=(it&&it.power)||"";
  $("f_drive").value=(it&&it.drive)||"";
  $("f_hours").value=(it&&it.hours)||"";
  $("f_year").value=(it&&it.year)||"";
  $("f_fuel").value=(it&&it.fuel)||"Gasóleo";
  $("f_price").value=(it&&it.price)||"";
  $("f_priceLabel").value=(it&&it.priceLabel)||"+ IVA";
  $("f_description").value=(it&&it.description)||"";
  $("f_metaTitle").value=(it&&it.metaTitle)||"";
  $("f_metaDesc").value=(it&&it.metaDesc)||"";
  setStatus(it?it.status:"Novo");
  feats=(it&&it.features||[]).slice();
  renderFeats();
  previewImage();
  $("editor").classList.add("open");
  $("overlay").classList.add("open");
  window.setTimeout(function(){$("f_brand").focus();},150);
}
function closeEditor(){$("editor").classList.remove("open");$("overlay").classList.remove("open");}
function addFeat(){
  var v=$("f_featInput").value.trim();
  if(!v)return;
  if(feats.indexOf(v)<0)feats.push(v);
  $("f_featInput").value="";
  renderFeats();
}
function renderFeats(){
  var el=$("featList");el.innerHTML="";
  feats.forEach(function(f){
    var c=document.createElement("span");
    c.className="chip";
    c.innerHTML='<b>'+esc(f)+'</b><button onclick="removeFeat(this)" aria-label="Remover">×</button>';
    el.appendChild(c);
  });
}
function removeFeat(btn){var chip=btn.parentElement;feats=feats.filter(function(f){return f!==chip.querySelector("b").textContent});renderFeats();}

function collectProduct(){
  var it={};
  it.id=$("f_id").value?parseInt($("f_id").value,10):0;
  it.category=$("f_category").value.trim()||"Trator";
  it.brand=$("f_brand").value.trim();
  it.model=$("f_model").value.trim();
  it.status=selectedStatus;
  it.sold=selectedStatus==="Vendido";
  it.available=selectedStatus!=="Vendido";
  it.image=$("f_image").value;
  it.power=$("f_power").value.trim();
  it.drive=$("f_drive").value.trim();
  it.hours=$("f_hours").value.trim();
  it.year=$("f_year").value.trim();
  it.fuel=$("f_fuel").value.trim();
  it.price=$("f_price").value.trim();
  it.priceLabel=$("f_priceLabel").value;
  it.description=$("f_description").value.trim();
  it.features=feats.slice();
  it.metaTitle=$("f_metaTitle").value.trim()||null;
  it.metaDesc=$("f_metaDesc").value.trim()||null;
  return it;
}
async function saveProduct(){
  var it=collectProduct();
  if(!it.brand||!it.model)return toast("Faltam a marca e o modelo","err");
  $("saveBtn").disabled=true;
  $("saveBtn").innerHTML='<i class="fas fa-spinner fa-spin"></i> A guardar…';
  var d=await api("/api/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({product:it})});
  $("saveBtn").disabled=false;
  $("saveBtn").innerHTML='<i class="fas fa-floppy-disk"></i> Guardar &amp; gerar site';
  if(d.ok){items=null;await reloadStock();closeEditor();toast("Guardado e site gerado","ok",(d.log||[]).slice(0,2).join(" · "));}
  else toast(d.error||"Erro ao guardar","err");
}
function deleteCurrent(){
  if(!selectedId)return;
  var it=items.find(function(x){return x.id===selectedId});
  if(!confirm("Eliminar «"+it.brand+" "+it.model+"» do site?"))return;
  api("/api/delete",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:selectedId,slug:it.slug})}).then(function(d){
    if(d.ok){closeEditor();reloadStock();toast("Veículo eliminado e site gerado","ok");}
    else toast(d.error||"Erro ao eliminar","err");
  });
}
function duplicateCurrent(){
  if(!selectedId)return;
  var it=collectProduct();it.id=0;it.brand=(it.brand||"")+" (cópia)";
  $("saveBtn").disabled=true;
  api("/api/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({product:it})}).then(function(d){
    $("saveBtn").disabled=false;
    if(d.ok){closeEditor();reloadStock();toast("Duplicado criado","ok");}
    else toast(d.error||"Erro","err");
  });
}
async function regenSite(){
  var b=$("regenBtn");b.disabled=true;b.innerHTML='<i class="fas fa-spinner fa-spin"></i> A gerar…';
  var d=await api("/api/regenerate",{method:"POST"});
  b.disabled=false;b.innerHTML='<i class="fas fa-wand-magic-sparkles"></i> Regenerar site';
  if(d.ok)toast("Site regenerado ("+d.count+" veículos)","ok",(d.log||[]).slice(0,3).join(" · "));
  else toast("Erro a gerar","err");
}
function scrollTopAdmin(){document.querySelector(".content").scrollTop=0;}

document.addEventListener("keydown",function(e){if(e.key==="Escape")closeEditor();});
window.addEventListener("load",function(){loading();});
function loading(){
  Promise.all([api("/api/stock"),api("/api/images")]).then(function(r){
    if(r[0].ok){items=r[0].items;renderGrid();}
    if(r[1].ok)renderImageSelect(r[1].images);
    $("serverState").textContent="Servidor local · stock.json";
  });
}
</script>
</body>
</html>
"""


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("=" * 58)
    print("  GESTOR DO SITE — RUI CABO & MATOS")
    print("=" * 58)
    print("  Site (pré-visualização): http://%s:%d" % (HOST, PORT))
    print("  Painel de gestão (HUD):  http://%s:%d/admin" % (HOST, PORT))
    print("  Para terminar: Ctrl+C")
    print("=" * 58)
    threading.Timer(0.7, lambda: webbrowser.open("http://%s:%d/admin" % (HOST, PORT))).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nA terminar…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()