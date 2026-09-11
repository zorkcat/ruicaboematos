# -*- coding: utf-8 -*-
"""Gerador do site Rui Cabo & Matos.

Fonte unica dos dados do stock = lista PRODUTOS abaixo.
Para atualizar o site depois de mudar o stock:
    python gerar_produtos.py

Gera:
  - tractors.js          (dados usados pela pagina principal)
  - trator/<slug>/index.html  (1 pagina SEO por maquina)
  - sitemap.xml
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://ruicaboematos.pt"
SEG = "Seg\u2013S\u00e1b \u00b7 08h30\u201319h00"

PRODUTOS = [
    {
        "id": 1, "brand": "Yanmar", "model": "KE-40", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "yanmar",
        "image": "yanmar.jpg", "power": "14 CV", "powerNumber": 14, "drive": "2WD",
        "hours": "1.983 h", "hoursNumber": 1983, "year": "2023", "yearNumber": 2023,
        "price": "6.500 \u20ac", "priceNumber": 6500, "priceLabel": "+ IVA", "available": True,
        "description": "Minitrator compacto e econ\u00f3mico, reconhecido pela sua fiabilidade e facilidade de utiliza\u00e7\u00e3o. Ideal para trabalhos em pequenas propriedades, vinhas, pomares e quintas.",
        "features": ["14 CV", "2WD", "1.983 h", "2023", "Gas\u00f3leo"],
    },
    {
        "id": 2, "brand": "SAME", "model": "FRUTTETO 75", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "same",
        "image": "SAME_USADO.jpg", "power": "75 CV", "powerNumber": 75, "drive": "2WD",
        "hours": "5.784 h", "hoursNumber": 5784, "year": "1999", "yearNumber": 1999,
        "price": "17.000 \u20ac", "priceNumber": 17000, "priceLabel": "+ IVA", "available": True,
        "description": "Trator agr\u00edcola de 75 CV, robusto e vers\u00e1til, preparado para diferentes trabalhos agr\u00edcolas. Uma op\u00e7\u00e3o pr\u00e1tica para quem procura pot\u00eancia e simplicidade.",
        "features": ["75 CV", "2WD", "5.784 h", "1999", "Gas\u00f3leo"],
    },
    {
        "id": 3, "brand": "SAME", "model": "FRUTTETO 75 CAB.", "fuel": "Gas\u00f3leo",
        "status": "Vendido", "condition": "usados", "brandFilter": "same",
        "image": "SAME_VENDIDO.JPEG", "power": "75 CV", "powerNumber": 75, "drive": "2WD",
        "hours": "5.305 h", "hoursNumber": 5305, "year": "2000", "yearNumber": 2000,
        "price": "21.000 \u20ac", "priceNumber": 21000, "priceLabel": "+ IVA", "available": False,
        "sold": True,
        "description": "Trator agr\u00edcola de 75 CV com cabina, conhecido pela sua robustez e versatilidade. Unidade apresentada como refer\u00eancia do nosso hist\u00f3rico de vendas.",
        "features": ["75 CV", "2WD", "5.305 h", "2000", "Gas\u00f3leo"],
    },
    {
        "id": 4, "brand": "TYM", "model": "T303 \u2014 Carregador Frontal", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "tym",
        "image": "TYM T303 COM CARREGADOR.jpg", "power": "30 CV", "powerNumber": 30, "drive": "2WD",
        "hours": "109,2 h", "hoursNumber": 109.2, "year": "\u2014", "yearNumber": 0,
        "price": "15.000 \u20ac", "priceNumber": 15000, "priceLabel": "+ IVA", "available": True,
        "description": "Trator compacto de 30 CV com carregador frontal e apenas 109,2 horas. Uma solu\u00e7\u00e3o vers\u00e1til para trabalhos agr\u00edcolas, manuten\u00e7\u00e3o de propriedades e movimenta\u00e7\u00e3o de materiais.",
        "features": ["30 CV", "2WD", "109,2 h", "Carregador frontal", "Gas\u00f3leo"],
    },
    {
        "id": 5, "brand": "Solis", "model": "S26+", "fuel": "Gas\u00f3leo",
        "status": "Novo", "condition": "novos", "brandFilter": "solis",
        "image": "solis_novo.jpg", "power": "26 CV", "powerNumber": 26, "drive": "4WD",
        "hours": "0 h", "hoursNumber": 0, "year": "2026", "yearNumber": 2026,
        "price": "10.500 \u20ac", "priceNumber": 10500, "priceLabel": "Com IVA", "available": True,
        "description": "Trator compacto novo de 26 CV, com tra\u00e7\u00e3o 4x4, dire\u00e7\u00e3o assistida e duas sa\u00eddas hidr\u00e1ulicas de duplo efeito. Uma solu\u00e7\u00e3o vers\u00e1til para diferentes trabalhos agr\u00edcolas.",
        "features": ["26 CV", "4WD", "0 h", "Dire\u00e7\u00e3o assistida", "Gas\u00f3leo"],
    },
    {
        "id": 6, "brand": "Kubota", "model": "L2550", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "kubota",
        "image": "kubota_usado.jpg", "power": "30 CV", "powerNumber": 30, "drive": "2WD",
        "hours": "4.274 h", "hoursNumber": 4274, "year": "\u2014", "yearNumber": 0,
        "price": "6.000 \u20ac", "priceNumber": 6000, "priceLabel": "+ IVA", "available": True,
        "description": "Trator compacto de 30 CV, matriculado e em excelente estado mec\u00e2nico. Uma solu\u00e7\u00e3o vers\u00e1til para trabalhos agr\u00edcolas e manuten\u00e7\u00e3o de propriedades.",
        "features": ["30 CV", "2WD", "4.274 h", "Matriculado", "Gas\u00f3leo"],
    },
    {
        "id": 7, "brand": "Husqvarna", "model": "CTH191 19CV", "fuel": "Gasolina",
        "status": "Vendido", "condition": "usados", "brandFilter": "husqvarna",
        "image": "husqvarna_vendido.jpg", "power": "19 CV", "powerNumber": 19, "drive": "2WD",
        "hours": "0 h", "hoursNumber": 0, "year": "2009", "yearNumber": 2009,
        "price": "1.250 \u20ac", "priceNumber": 1250, "priceLabel": "+ IVA", "available": False,
        "sold": True,
        "description": "Husqvarna CTH191, equipada com motor Kohler de 19 CV. M\u00e1quina em bom estado geral, pronta a trabalhar.",
        "features": ["19 CV", "2WD", "Motor Kohler", "2009", "Gasolina"],
    },
    {
        "id": 8, "brand": "Ford", "model": "3910", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "ford",
        "image": "ford_3910.jpg", "power": "50 CV", "powerNumber": 50, "drive": "4WD",
        "hours": "3.191 h", "hoursNumber": 3191, "year": "\u2014", "yearNumber": 0,
        "price": "9.500 \u20ac", "priceNumber": 9500, "priceLabel": "+ IVA", "available": True,
        "description": "Ford 3910 4x4 com 3.191 horas, matriculado e com funcionalidades operacionais. Uma solu\u00e7\u00e3o robusta para diferentes trabalhos agr\u00edcolas.",
        "features": ["50 CV", "4WD", "3.191 h", "Matriculado", "Gas\u00f3leo"],
    },
    {
        "id": 9, "brand": "Kioti", "model": "DK5010N", "fuel": "Gas\u00f3leo",
        "status": "Vendido", "condition": "usados", "brandFilter": "kioti",
        "image": "kioti_vendido.jpg", "power": "50 CV", "powerNumber": 50, "drive": "2WD",
        "hours": "3.300 h", "hoursNumber": 3300, "year": "2019", "yearNumber": 2019,
        "price": "20.750 \u20ac", "priceNumber": 20750, "priceLabel": "+ IVA", "available": False,
        "sold": True,
        "description": "Trator de 50 CV com carregador frontal, apresentado em excelente estado.",
        "features": ["50 CV", "2WD", "3.300 h", "2019", "Gas\u00f3leo"],
    },
    {
        "id": 10, "brand": "UTB", "model": "U-445", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "utb",
        "image": "FIAT.JPG", "power": "45 CV", "powerNumber": 45, "drive": "2WD",
        "hours": "3.663 h", "hoursNumber": 3663, "year": "\u2014", "yearNumber": 0,
        "price": "4.400 \u20ac", "priceNumber": 4400, "priceLabel": "+ IVA", "available": True,
        "description": "Trator UTB / Universal U-445, robusto, econ\u00f3mico e totalmente funcional. Motor de 45 CV com 3 cilindros, mec\u00e2nica sob licen\u00e7a Fiat 450, matriculado e em excelente estado mec\u00e2nico. Pronto a trabalhar.",
        "features": ["45 CV", "2WD", "3.663 h", "Matriculado", "Gas\u00f3leo"],
    },
    {
        "id": 11, "brand": "Landini", "model": "5860 \u2014 Dire\u00e7\u00e3o Assistida", "fuel": "Gas\u00f3leo",
        "status": "Usado", "condition": "usados", "brandFilter": "landini",
        "image": "landini.jpg", "power": "50 CV", "powerNumber": 50, "drive": "2WD",
        "hours": "\u2014", "hoursNumber": 0, "year": "\u2014", "yearNumber": 0,
        "price": "7.000 \u20ac", "priceNumber": 7000, "priceLabel": "+ IVA", "available": True,
        "description": "Vende-se Landini 5860, um trator robusto, econ\u00f3mico e muito fi\u00e1vel, ideal para agricultura, vinhas, pomares, quintas e todo o tipo de trabalhos agr\u00edcolas. Dire\u00e7\u00e3o assistida, sem tra\u00e7\u00e3o dianteira (2WD), com matr\u00edcula e documentos, motor fi\u00e1vel e de manuten\u00e7\u00e3o simples, estrutura de prote\u00e7\u00e3o (arco de seguran\u00e7a). Pronto para trabalhar. Uma excelente escolha para quem procura um trator resistente, confort\u00e1vel de conduzir e com a qualidade reconhecida da Landini.",
        "features": ["50 CV", "2WD", "Dire\u00e7\u00e3o assistida", "Matriculado", "Gas\u00f3leo"],
    },
]

WA_BASE = "https://wa.me/351916389652?text="

STOCK_JSON = os.path.join(BASE, "stock.json")


def _tonum(value):
    """Extrai um numero puro de uma string de exibicao (ex.: '10.500 \u20ac' -> 10500.0, '109,2 h' -> 109.2)."""
    if value is None:
        return 0
    s = str(value).strip()
    for u in ("\u20ac", "\u00a0", "h", "CV", "km", "anos", " "):
        s = s.replace(u, "")
    if not s or s in ("\u2014", "-"):
        return 0
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0


def _plural(cat):
    """Plural amigavel de uma categoria (ex.: 'Trator' -> 'Tratores')."""
    if cat == "Trator":
        return "Tratores"
    if cat == "Ve\u00edculo":
        return "Ve\u00edculos"
    if cat == "Reboque":
        return "Reboques"
    base = cat or ""
    if not base:
        return "Ve\u00edculos"
    if base[-1].lower() in ("a", "e", "o"):
        return base[:-1] + base[-1] + "s"
    return base + "s"


def normalize_product(p):
    """Completa e normaliza um produto (aceita dict proveniente de stock.json ou PRODUTOS)."""
    p = dict(p)
    p["brand"] = (p.get("brand") or "").strip()
    p["model"] = (p.get("model") or "").strip()
    p["brandFilter"] = slugify(p["brand"])
    name = (p["brand"] + " " + p["model"]).strip()
    if not name:
        name = "Produto"
    p["slug"] = slugify(name)
    p["category"] = p.get("category") or "Trator"
    status = p.get("status") or ("Vendido" if p.get("sold") else "Usado")
    p["status"] = status
    sold = bool(p.get("sold")) or status == "Vendido"
    p["sold"] = sold
    p["available"] = bool(p.get("available", not sold)) and not sold
    p["condition"] = "novos" if status == "Novo" else "usados"
    p["fuel"] = p.get("fuel") or "Gas\u00f3leo"
    p["image"] = p.get("image") or ""
    p["power"] = (p.get("power") or "\u2014").strip() or "\u2014"
    p["drive"] = (p.get("drive") or "\u2014").strip() or "\u2014"
    p["hours"] = (p.get("hours") or "\u2014").strip() or "\u2014"
    p["year"] = (p.get("year") or "\u2014").strip() or "\u2014"
    p["price"] = (p.get("price") or "\u2014").strip() or "\u2014"
    p["priceLabel"] = p.get("priceLabel") or "+ IVA"
    p["priceNumber"] = _tonum(p["price"])
    p["powerNumber"] = _tonum(p["power"])
    p["hoursNumber"] = _tonum(p["hours"])
    p["yearNumber"] = int(_tonum(p["year"]))
    p["description"] = (p.get("description") or "").strip()
    feats = [str(f).strip() for f in (p.get("features") or []) if str(f).strip()]
    if p["drive"] not in feats and p["drive"] not in ("\u2014", "-"):
        feats.append(p["drive"])
    if p["fuel"] not in feats:
        feats.append(p["fuel"])
    p["features"] = feats
    p["metaTitle"] = (p.get("metaTitle") or "").strip() or None
    p["metaDesc"] = (p.get("metaDesc") or "").strip() or None
    p["id"] = p.get("id") or 0
    return p


def load_stock():
    """Le o stock a partir de stock.json (fonte usada pelo gestor). None se nao existir."""
    try:
        with open(STOCK_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [normalize_product(x) for x in data]
    except (OSError, ValueError, TypeError):
        pass
    return None


def current_stock():
    """Lista normalizada de produtos: stock.json se existir, senao PRODUTOS embutidos."""
    data = load_stock()
    if data is None:
        data = [normalize_product(p) for p in PRODUTOS]
    return data


def generate(data=None):
    """Regenera o site completo (tractors.js, paginas de produto e sitemap)."""
    if data is None:
        data = current_stock()
    else:
        data = [normalize_product(p) for p in data]
    write_tractors_js(data)
    for p in data:
        write_product(p)
    write_sitemap(data)
    write_robots()
    return data


def slugify(text):
    s = text.lower().strip()
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def wa_text(extra):
    from urllib.parse import quote
    return WA_BASE + quote("Ol\u00e1! Estou a enviar-lhe mensagem pois vi um an\u00fancio no website da Rui Cabo & Matos. " + (extra or ""))


def wa_product(p):
    return wa_text("Ol\u00e1, estou interessado no %s %s que vi no vosso site." % (p["brand"], p["model"]))


def image_url(p):
    from urllib.parse import quote
    return SITE + "/" + quote(p["image"])


for p in PRODUTOS:
    p["slug"] = slugify(p["brand"] + " " + p["model"])


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def to_js_obj(p):
    return json.dumps(p, ensure_ascii=False)


def safe_desc(p):
    d = p.get("description", "")
    return d


def price_label_opt(label):
    if label and "+ IVA" in label:
        return "+ IVA!"
    if label and "Com IVA" in label:
        return "Pre\u00e7o com IVA"
    return label or ""


KEYWORDS = [
    "%s %s" % (p["brand"], p["model"]) for p in PRODUTOS
]

HEADER = """\
<header id="mainHeader">
    <div class="header-wrap">
        <div class="container header-inner">
            <a href="__ROOT__" class="logo" aria-label="Rui Cabo & Matos, LDA">
                <div class="logo-mark">
                    <img src="__ROOT__logotipo2.png" alt="Rui Cabo & Matos, LDA" onerror="this.style.display='none';this.parentElement.classList.add('no-logo');">
                    <span class="logo-icon"><i class="fas fa-tractor"></i></span>
                </div>
                <div class="logo-name">
                    <strong>RUI CABO &amp; MATOS</strong>
                    <small>LDA \u00b7 Oficina e Com\u00e9rcio</small>
                </div>
            </a>
            <nav id="mainNav" aria-label="Navega\u00e7\u00e3o principal">
                <ul>
                    <li><a href="__ROOT__#inicio" class="nav-link">In\u00edcio</a></li>
                    <li><a href="__ROOT__#tratores" class="nav-link active">Tratores</a></li>
                    <li><a href="__ROOT__#empresa" class="nav-link">Empresa</a></li>
                    <li><a href="__ROOT__#servicos" class="nav-link">Servi\u00e7os</a></li>
                    <li><a href="__ROOT__#contactos" class="nav-link">Contactos</a></li>
                </ul>
            </nav>
            <div class="header-actions">
                <a href="tel:+351916389652" class="hdr-phone">
                    <i class="fas fa-phone"></i>
                    <span class="hdr-phone-text">
                        <small>Ligue agora</small>
                        <strong>+351 916 389 652</strong>
                    </span>
                </a>
                <a href="__WA__" target="_blank" rel="noopener noreferrer" class="hdr-wa">
                    <i class="fab fa-whatsapp"></i>
                </a>
                <button class="theme-toggle" id="themeToggle" type="button" aria-label="Alternar tema claro/escuro" aria-pressed="false">
                    <i class="fas fa-moon"></i>
                </button>
                <button class="mobile-menu-btn" id="mobileMenuBtn" type="button" aria-label="Abrir menu" aria-expanded="false">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
        </div>
    </div>
</header>
"""

FOOTER = """\
<footer>
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <div class="footer-logo">
                    <div class="footer-logo-mark">
                        <img src="__ROOT__logotipo.png" alt="Rui Cabo & Matos" onerror="this.style.display='none';this.parentElement.classList.add('no-logo');">
                        <span class="footer-logo-icon"><i class="fas fa-tractor"></i></span>
                    </div>
                    <div>
                        <strong>RUI CABO &amp; MATOS, LDA</strong>
                        <small>Oficina \u00b7 Com\u00e9rcio \u00b7 Assist\u00eancia</small>
                    </div>
                </div>
                <p>Com\u00e9rcio de tratores novos e usados, oficina, assist\u00eancia mec\u00e2nica ao domic\u00edlio, compra, retoma e troca de tratores.</p>
                <div class="footer-socials">
                    <a href="__WA__" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
                    <a href="mailto:geral@ruicaboematos.com?subject=Contacto%20atrav%C3%A9s%20do%20website&body=Ol%C3%A1!%20Estou%20a%20enviar-lhe%20mensagem%20pois%20vi%20um%20an%C3%BAncio%20no%20website%20da%20Rui%20Cabo%20%26%20Matos.%0A%0AGostaria%20de%20entrar%20em%20contacto%20consigo.%0A%0ANome%3A%0ATelem%C3%B3vel%3A%0A%0AMensagem%3A" aria-label="Email"><i class="fas fa-envelope"></i></a>
                    <a href="tel:+351916389652" aria-label="Telefone"><i class="fas fa-phone"></i></a>
                </div>
            </div>
            <div class="footer-col">
                <h5>Navega\u00e7\u00e3o</h5>
                <a href="__ROOT__#inicio">In\u00edcio</a>
                <a href="__ROOT__#tratores">Tratores</a>
                <a href="__ROOT__#empresa">Empresa</a>
                <a href="__ROOT__#servicos">Servi\u00e7os</a>
                <a href="__ROOT__#contactos">Contactos</a>
            </div>
            <div class="footer-col">
                <h5>Servi\u00e7os</h5>
                <a href="__ROOT__#tratores">Tratores novos e usados</a>
                <a href="__ROOT__#servicos">Oficina</a>
                <a href="__ROOT__#servicos">Assist\u00eancia ao domic\u00edlio</a>
                <a href="__ROOT__#servicos">Compra e retoma</a>
            </div>
            <div class="footer-col">
                <h5>Contactos</h5>
                <a href="tel:+351916389652">+351 916 389 652</a>
                <a href="__WA__" target="_blank" rel="noopener noreferrer">WhatsApp</a>
                <a href="mailto:geral@ruicaboematos.com?subject=Contacto%20atrav%C3%A9s%20do%20website&body=Ol%C3%A1!%20Estou%20a%20enviar-lhe%20mensagem%20pois%20vi%20um%20an%C3%BAncio%20no%20website%20da%20Rui%20Cabo%20%26%20Matos.%0A%0AGostaria%20de%20entrar%20em%20contacto%20consigo.%0A%0ANome%3A%0ATelem%C3%B3vel%3A%0A%0AMensagem%3A">geral@ruicaboematos.com</a>
                <span class="footer-addr">Rua das Pedras Bastas 480<br>4780-395 Santo Tirso<br>Burg\u00e3es, Portugal</span>
            </div>
        </div>
    </div>
    <div class="footer-bottom">
        <div class="container footer-bottom-inner">
            <span>&copy; <span id="currentYear"></span> Rui Cabo &amp; Matos, LDA \u00b7 Todos os direitos reservados \u00b7 <a href="__ROOT__privacidade.html">Pol\u00edtica de Privacidade</a></span>
            <span>Santo Tirso \u00b7 Portugal</span>
        </div>
    </div>
</footer>
"""

WA_FLOAT = """\
<a href="__WA__" target="_blank" rel="noopener noreferrer" class="wa-float" aria-label="Falar no WhatsApp">
    <i class="fab fa-whatsapp"></i>
</a>
"""

COOKIE = """\
<div class="cookie-banner" id="cookieBanner" role="dialog" aria-live="polite" aria-label="Consentimento de cookies" hidden>
    <div class="cookie-banner-inner">
        <div class="cookie-banner-head">
            <div class="cookie-banner-icon"><i class="fas fa-cookie-bite"></i></div>
            <div class="cookie-banner-title">
                <strong>Valorizamos a sua privacidade</strong>
            </div>
            <button type="button" class="cookie-close" id="cookieClose" aria-label="Fechar e continuar apenas com o essencial"><i class="fas fa-xmark"></i></button>
        </div>
        <p class="cookie-banner-text">Este website utiliza cookies essenciais e guarda prefer\u00eancias no seu dispositivo (como o tema). As estat\u00edsticas an\u00f3nimas de utiliza\u00e7\u00e3o s\u00f3 s\u00e3o ativadas se autorizar. Saiba mais na nossa <a href="__ROOT__privacidade.html">Pol\u00edtica de Privacidade</a>.</p>
        <div class="cookie-banner-actions">
            <button type="button" class="btn btn-outline btn-sm" id="cookieDecline">S\u00f3 o essencial</button>
            <button type="button" class="btn btn-primary btn-sm" id="cookieAccept">Aceitar tudo</button>
        </div>
    </div>
</div>
"""

BASE_JS = """
(function () {
    "use strict";
    var HEADER = document.getElementById("mainHeader");
    var cookieBanner = document.getElementById("cookieBanner");
    var mobileMenuBtn = document.getElementById("mobileMenuBtn");
    var mainNav = document.getElementById("mainNav");
    var themeToggle = document.getElementById("themeToggle");
    var themeMeta = document.querySelector('meta[name="theme-color"]');
    var scrollTop = document.getElementById("scrollTop");
    var toast = document.getElementById("toast");
    var GA4_ID = "G-7XH3TR4B4Q";

    function getConsent(){var c=null;try{c=localStorage.getItem("rcm-consent-v1");}catch(e){}return c;}
    function setConsent(v){try{localStorage.setItem("rcm-consent-v1",v);}catch(e){}}
    function hideCookieBanner(){if(cookieBanner){cookieBanner.hidden=true;cookieBanner.classList.remove("show");}}
    function showToast(msg){toast.textContent=msg;toast.classList.add("show");setTimeout(function(){toast.classList.remove("show");},4000);}

    function loadAnalytics(){
        if(document.getElementById("gtag-js"))return;
        if(!GA4_ID||GA4_ID.indexOf("G-XXXX")===0)return;
        var s=document.createElement("script");s.id="gtag-js";s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+GA4_ID;
        document.head.appendChild(s);
        window.dataLayer=window.dataLayer||[];
        window.gtag=function(){window.dataLayer.push(arguments);};
        window.gtag("js",new Date());
        window.gtag("config",GA4_ID);
    }
    function trackGA(name,params){
        if(getConsent()!=="all")return;
        loadAnalytics();
        if(window.gtag)window.gtag("event",name,params||{});
    }
    document.addEventListener("click",function(e){
        var a=e.target.closest("a");
        if(!a)return;
        var h=a.getAttribute("href")||"";
        if(h.indexOf("tel:")===0)trackGA("contact_call",{});
        else if(h.indexOf("https://wa.me")===0)trackGA("contact_whatsapp",{});
    });

    function applyTheme(t){
        document.documentElement.setAttribute("data-theme",t);
        try{localStorage.setItem("rcm-theme-v2",t);}catch(e){}
        if(themeMeta)themeMeta.setAttribute("content",t==="dark"?"#0C1A11":"#2E7D32");
        if(themeToggle){var i=themeToggle.querySelector("i");if(i)i.className=t==="dark"?"fas fa-sun":"fas fa-moon";themeToggle.setAttribute("aria-pressed",t==="dark"?"true":"false");}
    }
    var savedTheme=null;try{savedTheme=localStorage.getItem("rcm-theme-v2");}catch(e){}
    applyTheme(savedTheme==="dark"?"dark":"light");
    if(themeToggle)themeToggle.addEventListener("click",function(){applyTheme(document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark");});

    if(cookieBanner&&!getConsent()){
        setTimeout(function(){cookieBanner.hidden=false;requestAnimationFrame(function(){cookieBanner.classList.add("show");});},900);
    }
    var cookieAccept=document.getElementById("cookieAccept"),cookieDecline=document.getElementById("cookieDecline"),cookieClose=document.getElementById("cookieClose");
    function consentAll(){setConsent("all");loadAnalytics();if(window.gtag)window.gtag("consent","update",{analytics_storage:"granted"});trackGA("consent_granted",{});hideCookieBanner();}
    function consentMinimal(){setConsent("minimal");hideCookieBanner();}
    if(cookieAccept)cookieAccept.addEventListener("click",consentAll);
    if(cookieDecline)cookieDecline.addEventListener("click",consentMinimal);
    if(cookieClose)cookieClose.addEventListener("click",consentMinimal);
    if(getConsent()==="all"){loadAnalytics();if(window.gtag)window.gtag("consent","update",{analytics_storage:"granted"});}

    if(mobileMenuBtn&&mainNav)mobileMenuBtn.addEventListener("click",function(){var isOpen=mainNav.classList.toggle("mobile-open");this.setAttribute("aria-expanded",String(isOpen));this.innerHTML=isOpen?'<i class="fas fa-times"></i>':'<i class="fas fa-bars"></i>';});
    if(mainNav)mainNav.querySelectorAll("a").forEach(function(link){link.addEventListener("click",function(){mainNav.classList.remove("mobile-open");if(mobileMenuBtn){mobileMenuBtn.setAttribute("aria-expanded","false");mobileMenuBtn.innerHTML='<i class="fas fa-bars"></i>';}});});

    window.addEventListener("scroll",function(){
        if(HEADER)HEADER.classList.toggle("scrolled",window.scrollY>25);
        if(scrollTop)scrollTop.classList.toggle("visible",window.scrollY>600);
    },{passive:true});
    if(scrollTop)scrollTop.addEventListener("click",function(){window.scrollTo({top:0,behavior:"smooth"});});
    var y=document.getElementById("currentYear");if(y)y.textContent=new Date().getFullYear();
})();
"""

PRODUCT_PAGE = """\
<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>__TITLE__</title>
    <meta name="description" content="__META_DESC__">
    <meta name="robots" content="index, follow">
    <meta name="keywords" content="__KEYWORDS__">
    <meta name="theme-color" content="#2E7D32">
    <meta name="geo.region" content="PT-13">
    <meta name="geo.placename" content="Santo Tirso, Burg\u00e3es">
    <meta name="ICBM" content="41.3529, -8.4541">
    <link rel="icon" type="image/png" href="__ROOT__favicon.png">
    <meta name="google-site-verification" content="zK9IBZV2TPg_5cLbYO3xtSV2w-gO60DWNLj7bAYpCrc">
    <link rel="canonical" href="__CANONICAL__">
    <meta property="og:type" content="product">
    <meta property="og:locale" content="pt_PT">
    <meta property="og:site_name" content="Rui Cabo & Matos, LDA">
    <meta property="og:title" content="__OG_TITLE__">
    <meta property="og:description" content="__OG_DESC__">
    <meta property="og:url" content="__CANONICAL__">
    <meta property="og:image" content="__OG_IMAGE__">
    <meta property="og:image:alt" content="__OG_IMAGE_ALT__">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="__OG_TITLE__">
    <meta name="twitter:description" content="__OG_DESC__">
    <meta name="twitter:image" content="__OG_IMAGE__">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <script>(function(){var t="light";try{var s=localStorage.getItem("rcm-theme-v2");if(s==="dark")t="dark";}catch(e){}document.documentElement.setAttribute("data-theme",t);})();</script>
    <link rel="stylesheet" href="__ROOT__style.css">
    <script type="application/ld+json">
    __PRODUCT_SCHEMA__
    </script>
    <script type="application/ld+json">
    __BREADCRUMB_SCHEMA__
    </script>
</head>
<body>

<a class="skip-link" href="#principal">Saltar para o conteúdo</a>

__HEADER__

<main class="product-page" id="principal">
    <div class="container">
        <nav class="crumbs" aria-label="Localiza\u00e7\u00e3o atual">
            <a href="__ROOT__#inicio">In\u00edcio</a>
            <i class="fas fa-chevron-right"></i>
            <a href="__ROOT__#tratores">__CAT_PLURAL__</a>
            <i class="fas fa-chevron-right"></i>
            <span>__BRAND__ __MODEL__</span>
        </nav>
        <div class="product-layout">
            <div class="product-media">
                <div class="product-img-wrap">
                    __MEDIA_BADGE____IMAGE__
                </div>
                <div class="product-media-caption"><i class="fas fa-camera"></i> Foto real do equipamento \u00b7 pe\u00e7a mais imagens e v\u00eddeos</div>
            </div>
            <div class="product-info">
                <div class="tractor-top">
                    <span class="tractor-brand">__BRAND__</span>
                    <span class="tractor-avail __AVAIL_CLASS__"><i class="fas fa-circle"></i> __AVAIL_TEXT__</span>
                </div>
                <h1>__BRAND__ __MODEL__</h1>
                <p class="product-desc">__DESC__</p>
                <div class="tractor-chips">__CHIPS__</div>
                <div class="product-specs">
                    <div class="modal-spec"><i class="fas fa-horse"></i><div><small>Pot\u00eancia</small><strong>__POWER__</strong></div></div>
                    <div class="modal-spec"><i class="fas fa-cog"></i><div><small>Tra\u00e7\u00e3o</small><strong>__DRIVE__</strong></div></div>
                    <div class="modal-spec"><i class="fas fa-clock"></i><div><small>Horas</small><strong>__HOURS__</strong></div></div>
                    <div class="modal-spec"><i class="fas fa-calendar"></i><div><small>Ano</small><strong>__YEAR__</strong></div></div>
                    <div class="modal-spec"><i class="fas fa-gas-pump"></i><div><small>Combust\u00edvel</small><strong>__FUEL__</strong></div></div>
                </div>
                <div class="modal-price-block">
                    <span>Pre\u00e7o anunciado</span>
                    <div class="modal-price">__PRICE__ <small>__PRICE_LABEL__</small></div>
                </div>
                __ACTIONS__
                <div class="product-trust">
                    <div class="product-trust-item"><i class="fas fa-shield-halved"></i><span><strong>Avalia\u00e7\u00e3o gratuita</strong><small>do seu trator</small></span></div>
                    <div class="product-trust-item"><i class="fas fa-arrows-rotate"></i><span><strong>Retoma e troca</strong><small>com o seu usado</small></span></div>
                    <div class="product-trust-item"><i class="fas fa-truck"></i><span><strong>Entrega e apoio</strong><small>ao domic\u00edlio</small></span></div>
                </div>
                <div class="modal-note">
                    <i class="fas fa-circle-info"></i>
                    <span>Contacte-nos para confirmar disponibilidade, caracter\u00edsticas e restantes condi\u00e7\u00f5es do equipamento.</span>
                </div>
            </div>
        </div>

        <div class="product-cta">
            <div class="product-cta-inner">
                <div class="product-cta-icon"><i class="fas fa-comments"></i></div>
                <div class="product-cta-text">
                    <strong>Precisa de mais informa\u00e7\u00f5es sobre este equipamento?</strong>
                    <p>Fale connosco por WhatsApp ou telefone. Enviamos mais fotos, v\u00eddeos e todos os detalhes que precisar.</p>
                </div>
                <div class="product-cta-actions">
                    <a href="__WA__" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp"><i class="fab fa-whatsapp"></i> Falar por WhatsApp</a>
                    <a href="tel:+351916389652" class="btn btn-primary"><i class="fas fa-phone"></i> Ligar j\u00e1</a>
                </div>
            </div>
        </div>

        <div class="product-related">
            <div class="section-header">
                <span class="section-label">Outros equipamentos</span>
                <h2 class="section-title">Mais __CAT_PLURAL_LOW__ <em>em stock.</em></h2>
                <span class="sec-line"></span>
                <p class="section-subtitle">Veja as restantes m\u00e1quinas dispon\u00edveis na nossa oficina e stand em Santo Tirso.</p>
            </div>
            <div class="tractors-grid" id="relatedGrid"></div>
        </div>
    </div>
</main>

__FOOTER__
__WA_FLOAT__
__COOKIE__
<div class="toast" id="toast" aria-live="polite"></div>

<script src="__ROOT__tractors.js"></script>
<script>
__RELATED_JS__
(function () {
    "use strict";
    var HEADER = document.getElementById("mainHeader");
    var current = window.RCM_CURRENT || null;
    if(current)trackProductView(current);
    function trackProductView(p){__TRACK_VIEW__}
})();
</script>
<script>
__BASE_JS_VALUE__
</script>
<script>if(location.protocol==="file:"){document.addEventListener("DOMContentLoaded",function(){function f(h){if(!h||/^(https?:|mailto:|tel:|javascript:)/i.test(h))return h;if(h.charAt(0)==="#")return"index.html"+h;var i=h.indexOf("#"),x=i>=0?h.slice(i):"",p=i>=0?h.slice(0,i):h;if(!p||p.slice(-1)==="/")p+="index.html";else if(!/(\.\w+)$/.test(p))p+="/index.html";return p+x;}document.querySelectorAll("a[href]").forEach(function(a){var h=a.getAttribute("href");if(h)a.setAttribute("href",f(h));});});}</script>
</body>
</html>
"""

RELATED_JS = """\
(function () {
    "use strict";
    var ROOT = "../../";
    window.RCM_CURRENT = __CURRENT__;
    function escapeHtml(v){if(v===null||v===undefined)return"";return String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");}
    function waUrl(t){return "https://wa.me/351916389652?text="+encodeURIComponent("Ol\u00e1! Estou a enviar-lhe mensagem pois vi um an\u00fancio no website da Rui Cabo & Matos. "+(t||""));}
    function priceLabelOpt(label){var l=String(label||"");if(l.indexOf("+ IVA")>=0)return "+ IVA!";if(l.indexOf("Com IVA")>=0)return "Pre\u00e7o com IVA";return l;}
    var current = window.RCM_CURRENT || {};
    var list=(window.RCM_TRACTORS||[]).filter(function(t){return t.slug!==current.slug;});
    var grid=document.getElementById("relatedGrid");
    if(grid){
        grid.innerHTML="";
        list.slice(0,6).forEach(function(t){
            var card=document.createElement("article");
            card.className="tractor-card"+(t.sold?" sold":"");
            var tAlt="Trator "+t.brand+" "+t.model+(t.sold?" vendido":(t.status?(" "+t.status.toLowerCase()):""));
            card.innerHTML='<div class="tractor-image"><a href="'+ROOT+'trator/'+escapeHtml(t.slug)+'/" aria-label="'+escapeHtml(t.brand+" "+t.model)+'"><img src="'+ROOT+escapeHtml(t.image)+'" alt="'+escapeHtml(tAlt)+'" loading="lazy" decoding="async"></a><div class="card-badges"><span class="badge '+(t.sold?"badge-sold":(t.status==="Novo"?"badge-new":"badge-used"))+'">'+escapeHtml(t.sold?"Vendido":t.status)+'</span></div></div><div class="tractor-info"><div class="tractor-top"><span class="tractor-brand">'+escapeHtml(t.brand)+'</span></div><div class="tractor-model">'+escapeHtml(t.model)+'</div><div class="tractor-specs"><div class="spec"><i class="fas fa-horse-head"></i><div><small>Pot\u00eancia</small><strong>'+escapeHtml(t.power)+'</strong></div></div><div class="spec"><i class="fas fa-clock"></i><div><small>Horas</small><strong>'+escapeHtml(t.hours)+'</strong></div></div><div class="spec"><i class="fas fa-calendar-check"></i><div><small>Ano</small><strong>'+escapeHtml(t.year)+'</strong></div></div></div><div class="tractor-footer"><div class="price-block"><strong class="price-value">'+escapeHtml(t.price)+'</strong><span class="price-label">'+escapeHtml(priceLabelOpt(t.priceLabel))+'</span></div>'+(t.sold?'<span class="btn-sold"><i class="fas fa-check"></i> Vendido</span>':'<a href="'+ROOT+'trator/'+escapeHtml(t.slug)+'/" class="btn btn-outline btn-sm">Ver detalhes <i class="fas fa-arrow-right"></i></a>')+'</div></div>';
            grid.appendChild(card);
        });
    }
})();
"""


def build_media_badge(p):
    if p.get("sold"):
        return '<span class="badge badge-sold">Vendido</span>'
    return '<span class="badge ' + ("badge-new" if p["status"] == "Novo" else "badge-used") + '">' + p["status"] + "</span>"


def alt_text(p):
    st = (p.get("status") or "").strip().lower()
    if p.get("sold"):
        st = "vendido"
    return ("Trator %s %s %s" % (p["brand"], p["model"], st)).rstrip()


def build_image(p):
    cls = ' class="sold-img"' if p.get("sold") else ""
    img = '<img src="__ROOT__%s" alt="%s"%s fetchpriority="high">' % (p["image"], alt_text(p), cls)
    return img


def build_actions(p):
    if p.get("sold"):
        return '<span class="btn btn-sold"><i class="fas fa-check"></i> J\u00e1 vendido</span>'
    wa = wa_product(p)
    return (
        '<div class="product-actions">'
        '<a href="%s" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp"><i class="fab fa-whatsapp"></i> Tenho interesse</a>'
        '<a href="tel:+351916389652" class="btn btn-primary"><i class="fas fa-phone"></i> Ligar</a>'
        "</div>" % wa
    )


def build_chips(p):
    out = []
    for f in p["features"]:
        if f != p["power"] and f != p["hours"] and f != p["year"]:
            out.append('<span class="tractor-chip">%s</span>' % f)
    return "".join(out)


def build_product_schema(p):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["brand"] + " " + p["model"],
        "image": [image_url(p)],
        "description": p["description"],
        "brand": {"@type": "Brand", "name": p["brand"]},
        "itemCondition": "https://schema.org/UsedCondition" if p["condition"] == "usados" else "https://schema.org/NewCondition",
        "offers": {
            "@type": "Offer",
            "url": SITE + "/trator/" + p["slug"] + "/",
            "priceCurrency": "EUR",
            "price": str(p["priceNumber"]),
            "availability": "https://schema.org/InStock" if p["available"] else "https://schema.org/SoldOut",
        },
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Pot\u00eancia", "value": p["power"]},
            {"@type": "PropertyValue", "name": "Tra\u00e7\u00e3o", "value": p["drive"]},
            {"@type": "PropertyValue", "name": "Horas", "value": p["hours"]},
            {"@type": "PropertyValue", "name": "Ano", "value": p["year"]},
            {"@type": "PropertyValue", "name": "Combust\u00edvel", "value": p["fuel"]},
            {"@type": "PropertyValue", "name": "Condi\u00e7\u00e3o", "value": p["status"]},
        ],
    }, ensure_ascii=False, indent=None)


def build_breadcrumb_schema(p):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "In\u00edcio", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Tratores", "item": SITE + "/#tratores"},
            {"@type": "ListItem", "position": 3, "name": p["brand"] + " " + p["model"], "item": SITE + "/trator/" + p["slug"] + "/"},
        ],
    }, ensure_ascii=False)


def write_product(p):
    root = "../../"
    url = SITE + "/trator/" + p["slug"] + "/"
    cat_plural = _plural(p["category"])
    title = p["metaTitle"] or "%s %s (%s) | Rui Cabo & Matos, LDA" % (p["brand"], p["model"], p["power"])
    meta_desc = p["metaDesc"] or "%s %s \u2014 %s, %s, %s. Pre\u00e7o anunciado: %s %s. Visite-nos em Santo Tirso ou fale connosco por WhatsApp." % (
        p["brand"], p["model"], p["power"], p["drive"], p["hours"], p["price"], price_label_opt(p["priceLabel"]))
    og_title = "%s %s \u2014 %s | Rui Cabo & Matos" % (p["brand"], p["model"], p["power"])
    og_desc = (p["metaDesc"] or p["description"] or "")[:160]
    html = PRODUCT_PAGE
    html = html.replace("__TITLE__", title)
    html = html.replace("__META_DESC__", meta_desc)
    html = html.replace("__KEYWORDS__", ", ".join(x for x in [p["brand"] + " " + p["model"], p["brand"] + " " + p["model"] + " " + p["power"], "trator " + p["brand"] + " " + p["model"] + " usado", "venda de tratores usados", p["category"].lower(), "tratores usados a venda Portugal", "oficina de tratores Santo Tirso", "Rui Cabo & Matos"] if x))
    html = html.replace("__CANONICAL__", url)
    html = html.replace("__OG_TITLE__", og_title)
    html = html.replace("__OG_DESC__", og_desc)
    html = html.replace("__OG_IMAGE__", image_url(p))
    html = html.replace("__OG_IMAGE_ALT__", "%s %s" % (p["brand"], p["model"]))
    html = html.replace("__ROOT__", root)
    html = html.replace("__WA__", wa_text(""))
    html = html.replace("__CAT_PLURAL__", cat_plural)
    html = html.replace("__CAT_PLURAL_LOW__", cat_plural.lower())
    html = html.replace("__PRODUCT_SCHEMA__", build_product_schema(p))
    html = html.replace("__BREADCRUMB_SCHEMA__", build_breadcrumb_schema(p))

    header = HEADER.replace("__ROOT__", root).replace("__WA__", wa_text(""))
    footer = FOOTER.replace("__ROOT__", root).replace("__WA__", wa_text(""))
    html = html.replace("__HEADER__", header)
    html = html.replace("__FOOTER__", footer)
    html = html.replace("__WA_FLOAT__", WA_FLOAT.replace("__WA__", wa_text("")))
    html = html.replace("__COOKIE__", COOKIE.replace("__ROOT__", root))

    html = html.replace("__MEDIA_BADGE__", build_media_badge(p))
    html = html.replace("__IMAGE__", build_image(p).replace("__ROOT__", root))
    html = html.replace("__BRAND__", p["brand"])
    html = html.replace("__MODEL__", p["model"])
    html = html.replace("__AVAIL_CLASS__", "available" if p["available"] else "sold")
    html = html.replace("__AVAIL_TEXT__", "Dispon\u00edvel" if p["available"] else "Vendido")
    html = html.replace("__DESC__", p["description"])
    html = html.replace("__CHIPS__", build_chips(p))
    html = html.replace("__POWER__", p["power"])
    html = html.replace("__DRIVE__", p["drive"])
    html = html.replace("__HOURS__", p["hours"])
    html = html.replace("__YEAR__", p["year"])
    html = html.replace("__FUEL__", p["fuel"])
    html = html.replace("__PRICE__", p["price"])
    html = html.replace("__PRICE_LABEL__", price_label_opt(p["priceLabel"]))
    html = html.replace("__ACTIONS__", build_actions(p))
    related_js = RELATED_JS.replace("__CURRENT__", json.dumps(p, ensure_ascii=False))
    html = html.replace("__RELATED_JS__", related_js)

    track_view = (
        "try{var __c=window.localStorage.getItem('rcm-consent-v1');if(__c==='all'){"
        "window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){window.dataLayer.push(arguments);};"
        "window.gtag('event','view_item',{items:[{item_id:p.slug,item_name:p.brand+' '+p.model,price:p.priceNumber,item_brand:p.brand,item_category:p.condition}]});"
        "}}catch(e){}"
    )
    html = html.replace("__TRACK_VIEW__", track_view)
    html = html.replace("__BASE_JS_VALUE__", BASE_JS)

    folder = os.path.join(BASE, "trator", p["slug"])
    ensure_dir(folder)
    path = os.path.join(folder, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK  trator/%s/index.html" % p["slug"])


def write_tractors_js(data=None):
    data = data if data is not None else current_stock()
    js = "window.RCM_TRACTORS=" + json.dumps([dict(p) for p in data], ensure_ascii=False) + ";\n"
    path = os.path.join(BASE, "tractors.js")
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK  tractors.js  (%d produtos)" % len(data))


def write_sitemap(data=None):
    from urllib.parse import quote
    import datetime
    data = data if data is not None else current_stock()
    lastmod = datetime.date.today().isoformat()
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
    lines.append('  <url>')
    lines.append('    <loc>%s/</loc>' % SITE)
    lines.append('    <lastmod>%s</lastmod>' % lastmod)
    lines.append('    <changefreq>weekly</changefreq>')
    lines.append('    <priority>1.0</priority>')
    for p in data:
        img = SITE + "/" + quote(p["image"] or "")
        if not p.get("image"):
            continue
        title = "%s %s %s %s" % (p["category"], p["brand"], p["model"], p["status"].lower())
        lines.append('    <image:image>')
        lines.append('      <image:loc>%s</image:loc>' % img)
        lines.append('      <image:title>%s</image:title>' % title)
        lines.append('    </image:image>')
    lines.append('  </url>')
    lines.append('  <url>')
    lines.append('    <loc>%s/privacidade.html</loc>' % SITE)
    lines.append('    <lastmod>%s</lastmod>' % lastmod)
    lines.append('    <changefreq>yearly</changefreq>')
    lines.append('    <priority>0.3</priority>')
    lines.append('  </url>')
    for p in data:
        url = "%s/trator/%s/" % (SITE, p["slug"])
        lines.append('  <url>')
        lines.append('    <loc>%s</loc>' % url)
        lines.append('    <lastmod>%s</lastmod>' % lastmod)
        lines.append('    <changefreq>weekly</changefreq>')
        lines.append('    <priority>0.8</priority>')
        if p.get("image"):
            lines.append('    <image:image>')
            lines.append('      <image:loc>%s</image:loc>' % (SITE + "/" + quote(p["image"])))
            lines.append('      <image:title>%s %s</image:title>' % (p["brand"], p["model"]))
            lines.append('    </image:image>')
        lines.append('  </url>')
    lines.append('</urlset>')
    path = os.path.join(BASE, "sitemap.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("OK  sitemap.xml")


def write_robots():
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Sitemap: %s/sitemap.xml\n" % SITE
    )
    path = os.path.join(BASE, "robots.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(robots)
    print("OK  robots.txt")


if __name__ == "__main__":
    data = generate()
    print("Conclu\u00eddo \u2014 %d ve\u00edculos em stock, %d p\u00e1ginas." % (
        len([x for x in data if not x.get("sold")]), len(data)))