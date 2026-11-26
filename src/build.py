#!/usr/bin/env python3
"""Builds the static site into the repository root. Run: python3 src/build.py"""
import json, os, re, shutil, subprocess, sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
from config import *          # noqa: F401,F403
from content import *         # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESBUILD = os.environ.get("ESBUILD", "esbuild")
import hashlib as _h
ASSET_V = _h.sha1(b"".join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f), "rb").read()
                          for f in ("css/site.css", "js/theme.js", "js/main.js", "js/ga.js"))).hexdigest()[:8]

def url(path):
    return SITE_URL + path

def project_path(p, lang):
    return PATHS["projects"][lang] + p["slug"][lang] + "/"

def other(lang):
    return "fr" if lang == "en" else "en"

# ---------- security policy (meta, for GitHub Pages; the same values live in _headers) ----------
def csp():
    script = ["'self'"]
    connect = ["'self'"]
    form = ["'self'"]
    img = ["'self'", "data:"]
    if CF_ANALYTICS_TOKEN:
        script.append("https://static.cloudflareinsights.com")
        connect.append("https://cloudflareinsights.com")
    if GA4_ID:
        script.append("https://*.googletagmanager.com")
        connect += ["https://*.google-analytics.com", "https://*.analytics.google.com", "https://*.googletagmanager.com"]
        img += ["https://*.google-analytics.com", "https://*.googletagmanager.com"]
    if WEB3FORMS_KEY:
        connect.append("https://api.web3forms.com")
        form.append("https://api.web3forms.com")
    return ("default-src 'self'; script-src " + " ".join(script) + "; style-src 'self'; img-src " + " ".join(img) + "; "
            "font-src 'self'; connect-src " + " ".join(connect) + "; form-action " + " ".join(form) + "; "
            "base-uri 'self'; object-src 'none'; manifest-src 'self'; upgrade-insecure-requests")

ICONS = {
    "moon": '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "sun": '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

def person_ld(lang):
    return {
        "@context": "https://schema.org", "@type": "Person", "@id": SITE_URL + "/#person",
        "name": NAME, "jobTitle": UI[lang]["title"], "email": "mailto:" + EMAIL, "url": url(PATHS["home"][lang]),
        "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressCountry": "MG"},
        "worksFor": {"@type": "Organization", "name": "AVEOLYS"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "IST Antsiranana"},
        "knowsLanguage": ["en", "fr", "mg"], "sameAs": [x for x in (LINKEDIN, UPWORK, INDEED) if x],
        "knowsAbout": ["Security operations", "SIEM", "Incident response", "Penetration testing", "Active Directory security", "Network security", "Identity and access management"],
    }

def breadcrumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (n, p) in enumerate(items)]}

def crumbs_html(lang, items):
    li = []
    for i, (n, p) in enumerate(items):
        if i == len(items) - 1:
            li.append(f'<li><span aria-current="page">{n}</span></li>')
        else:
            li.append(f'<li><a href="{p}">{n}</a></li>')
    label = "Breadcrumb" if lang == "en" else "Fil d'Ariane"
    return f'<nav class="crumbs" aria-label="{label}"><ol>{"".join(li)}</ol></nav>'


# ---------- layout ----------
SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ARROW = '<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'
OUT = '<svg class="ico ico--out" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 11l6-6M6 5h5v5"/></svg>'
DOWN = '<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M8 3v10M4 9l4 4 4-4"/></svg>'
EXPAND = '<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M9.5 2.5h4v4M6.5 13.5h-4v-4M13.5 2.5 9 7M2.5 13.5 7 9"/></svg>'
SEAL = '<svg viewBox="0 0 40 40" fill="none" stroke="#0f1b2d" stroke-width="1.6" aria-hidden="true" focusable="false"><circle cx="20" cy="17" r="10"/><circle cx="20" cy="17" r="6"/><path d="M14 25l-3 10 5-3 3 4 2-8M26 25l3 10-5-3-3 4-1-8"/></svg>'
SOCIAL_ICONS = {
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
    "upwork": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M18.561 13.158c-1.102 0-2.135-.467-3.074-1.227l.228-1.076.008-.042c.207-1.143.849-3.06 2.839-3.06 1.492 0 2.703 1.212 2.703 2.703-.001 1.489-1.212 2.702-2.704 2.702zm0-8.14c-2.539 0-4.51 1.649-5.31 4.366-1.22-1.834-2.148-4.036-2.687-5.892H7.828v7.112c-.002 1.406-1.141 2.546-2.547 2.548-1.405-.002-2.543-1.143-2.545-2.548V3.492H0v7.112c0 2.914 2.37 5.303 5.281 5.303 2.913 0 5.283-2.389 5.283-5.303v-1.19c.529 1.107 1.182 2.229 1.974 3.221l-1.673 7.873h2.797l1.213-5.71c1.063.679 2.285 1.109 3.686 1.109 3 0 5.439-2.452 5.439-5.45 0-3-2.439-5.439-5.439-5.439z"/></svg>',
}

def social_buttons(lang, cls=""):
    note = T(lang, "opens in a new tab", "s&#39;ouvre dans un nouvel onglet")
    items = [("linkedin", "LinkedIn", LINKEDIN), ("upwork", "Upwork", UPWORK)]
    links = "".join(f'<li><a class="social__btn social--{k}" href="{u}" aria-label="{n} ({note})" title="{n}">{SOCIAL_ICONS[k]}</a></li>' for k, n, u in items if u)
    return f'<ul class="social{(" " + cls) if cls else ""}" role="list">{links}</ul>'

MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'

def T(lang, en, fr):
    return en if lang == "en" else fr

def layout(lang, key, path, alt_path, title, desc, body, ld=None, og_type="website", noindex=False):
    ui = UI[lang]
    nav = []
    for k, label in [("projects", T(lang, "Work", "Travaux")), ("about", ui["nav"][2][1]), ("contact", ui["nav"][3][1])]:
        cur = ' aria-current="page"' if k == key else ""
        nav.append(f'<li><a href="{PATHS[k][lang]}"{cur}>{label}</a></li>')
    langs = []
    for l in LANGS:
        name, full = ("EN", "English") if l == "en" else ("FR", "Français")
        if l == lang:
            langs.append(f'<span aria-current="true" lang="{l}">{name}<span class="sr-only"> ({full})</span></span>')
        else:
            langs.append(f'<a href="{alt_path}" hreflang="{l}" lang="{l}">{name}<span class="sr-only"> ({full})</span></a>')
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    canonical = url(path)
    hreflang = ""
    if alt_path and key:
        en_p, fr_p = (path, alt_path) if lang == "en" else (alt_path, path)
        hreflang = (f'<link rel="alternate" hreflang="en" href="{url(en_p)}"><link rel="alternate" hreflang="fr" href="{url(fr_p)}">'
                    f'<link rel="alternate" hreflang="x-default" href="{url(en_p)}">')
    og_img = url(f"/assets/img/og-{lang}.png")
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    indeed_li = f'<li><a href="{INDEED}">Indeed</a></li>' if INDEED else ""
    ga = f'<script defer src="/assets/js/ga.min.js?v={ASSET_V}" data-id="{GA4_ID}"></script>' if GA4_ID else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp()}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
{robots}<link rel="canonical" href="{canonical}">
{hreflang}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NAME}, {escape(ui['title'])}">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'fr_FR'}">
<meta property="og:locale:alternate" content="{'fr_FR' if lang == 'en' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{og_img}">
<meta name="theme-color" content="#0f1b2d">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/hanken.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.min.css?v={ASSET_V}">
<script src="/assets/js/theme.min.js?v={ASSET_V}"></script>
<script defer src="/assets/js/main.min.js?v={ASSET_V}"></script>
{ga}{ld_html}
</head>
<body{' class="home-top"' if key == 'home' else ''}>
<a class="skip" href="#main">{ui['skip']}</a>
<header class="top{' top--home' if key == 'home' else ''}">
  <div class="frame top__row">
    <a class="top__name" href="{PATHS['home'][lang]}"><img class="top__avatar" src="/assets/img/stephanio-96.webp" width="40" height="40" alt="" decoding="async"><span class="top__label">{NAME}</span></a>
    <nav class="top__nav" aria-label="{T(lang, 'Main', 'Principale')}"><ul>{''.join(nav)}</ul></nav>
    <div class="top__tools">
      <div class="lang" role="group" aria-label="{ui['lang_label']}">{'<span class="lang__sep" aria-hidden="true">/</span>'.join(langs)}</div>
      <button class="theme" type="button" aria-pressed="false"><span class="sr-only">{T(lang, 'Dark theme', 'Thème sombre')}</span>{MOON}{SUN}</button>
    </div>
  </div>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="foot">
  <div class="frame foot__row">
    <p>{NAME}, {CITY}</p>
    {social_buttons(lang, "social--small")}
    <ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><a href="{PATHS['privacy'][lang]}">{ui['footer_links'][0][1]}</a></li>
      <li><a href="{PATHS['legal'][lang]}">{ui['footer_links'][1][1]}</a></li>
    </ul>
  </div>
</footer>
</body>
</html>
"""

# ---------- shared blocks ----------
def page_head(lang, h1, lead, crumbs, case=None, photo=False):
    lead_html = f'<p class="lede">{lead}</p>' if lead else ""
    tag = f'<p class="case-tag">{case}</p>' if case else ""
    pic = (f'<img class="head__photo" src="/assets/img/stephanio.webp" width="480" height="480" alt="{T(lang, "Portrait of Stephanio RAZARISON", "Portrait de Stephanio RAZARISON")}" decoding="async">'
           if photo else "")
    return (f'<section class="frame head{" head--photo" if photo else ""}" aria-labelledby="page-h"><div class="head__text">{crumbs_html(lang, crumbs)}{tag}'
            f'<h1 id="page-h">{h1}</h1>{lead_html}</div>{pic}</section>')

def case_grid(lang, h="h3", cta=True):
    """The six cases as a bento: CASE-01 wide, a closing card that asks for contact."""
    cards = []
    for i, p in enumerate(PROJECTS):
        live = p["status"]["en"] == "In production"
        wide = i in (0, 5)
        tools = "".join(f"<li>{t}</li>" for t in (p["tools"] if wide else p["tools"][:4]))
        n = len(SHOTS.get(p["case"], []))
        shots = f'<p class="card__shots">{T(lang, f"{n} screenshots inside", f"{n} captures à l&#39;intérieur")}</p>' if n else ""
        flow = ""
        if p["case"] == "CASE-01":
            flow = '<ol class="card__flow" aria-label="' + T(lang, "Pipeline", "Chaîne") + '">' + "".join(f"<li>{x}</li>" for x in p["flow"][lang]) + "</ol>"
        cards.append(f"""<li class="card{' card--wide' if i in (0, 5) else ''}">
  <a class="card__link" href="{project_path(p, lang)}">
    <span class="card__top"><span class="card__id">{p['case']}</span><span class="status{' status--live' if live else ''}"><span class="status__dot" aria-hidden="true"></span>{p['status'][lang]}</span></span>
    <{h} class="card__title">{p['title'][lang]}</{h}>
    <p class="card__line">{p['summary'][lang] if wide else p['card'][lang]}</p>
    {shots}
    <ul class="chips" aria-label="{T(lang, 'Tools', 'Outils')}">{tools}</ul>
    <span class="card__go">{T(lang, 'Open the case', 'Ouvrir le cas')} {ARROW}</span>
  </a>
</li>""")
    if cta:
        cards.append(f"""<li class="card card--cta">
  <div class="card__cta">
    <p class="card__title">{T(lang, 'Need a SOC built or a team to lead?', 'Un SOC à construire ou une équipe à diriger ?')}</p>
    <p class="card__line">{T(lang, 'I reply in English or French, usually within a day.', 'Je réponds en français ou en anglais, en général sous 24 heures.')}</p>
    <a class="btn btn--gold" href="{PATHS['contact'][lang]}">{T(lang, 'Get in touch', 'Me contacter')} {ARROW}</a>
  </div>
</li>""")
    return f'<ol class="cards" role="list">{"".join(cards)}</ol>'

def flow_svg(lang):
    """Logs from five sources reach Wazuh; only level 10+ alerts travel on to Shuffle and TheHive."""
    src = T(lang, ["Endpoints and servers", "Web app firewall", "Active Directory", "Microsoft 365", "Mail server"],
                  ["Postes et serveurs", "Pare-feu applicatif", "Active Directory", "Microsoft 365", "Serveur de messagerie"])
    ys = [50, 120, 190, 260, 330]
    parts = []
    for i, (label, y) in enumerate(zip(src, ys)):
        d = f"M150 {y} C 200 {y}, 196 190, 234 190"
        parts.append(f'<text class="fl-src" x="140" y="{y + 5}" text-anchor="end">{label}</text>'
                     f'<circle class="fl-port" cx="150" cy="{y}" r="3.5"/>'
                     f'<path id="fl-p{i}" class="fl-line" d="{d}"/>')
        for k in range(3):
            begin = round(i * 0.37 + k * 1.1, 2)
            parts.append(f'<circle class="fl-dot" r="3.5" opacity="0"><animateMotion dur="2.2s" begin="{begin}s" repeatCount="indefinite"><mpath href="#fl-p{i}"/></animateMotion>'
                         f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="2.2s" begin="{begin}s" repeatCount="indefinite"/></circle>')
    def node(x, y, w, label, cls=""):
        return (f'<g class="fl-node{cls}" tabindex="-1"><rect x="{x - w / 2}" y="{y - 19}" width="{w}" height="38" rx="10"/>'
                f'<text x="{x}" y="{y + 5}" text-anchor="middle">{label}</text></g>')
    alert_t = T(lang, "level ≥ 10", "niveau ≥ 10")
    parts.append('<path id="fl-a" class="fl-line fl-line--alert" d="M306 190 H430"/>')
    parts.append('<path id="fl-c" class="fl-line fl-line--enrich" d="M470 171 V109"/><path id="fl-m" class="fl-line fl-line--enrich" d="M470 209 V271"/>')
    parts.append(f'<text class="fl-tag" x="368" y="166" text-anchor="middle">{alert_t}</text>')
    parts.append(node(270, 190, 72, "Wazuh", " fl-node--hub"))
    parts.append(node(470, 190, 80, "TheHive"))
    parts.append(node(470, 90, 80, "Cortex"))
    parts.append(node(470, 290, 80, "MISP"))
    # Shuffle sits on the alert line
    parts.append('<g class="fl-node fl-node--soar"><rect x="331" y="176" width="74" height="28" rx="14"/><text x="368" y="195" text-anchor="middle">Shuffle</text></g>')
    for k in range(2):
        b0 = 0.6 + k * 1.6
        parts.append(f'<circle class="fl-alert" r="5" opacity="0"><animateMotion dur="3.2s" begin="{b0}s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;.3;.7;1" calcMode="linear"><mpath href="#fl-a"/></animateMotion>'
                     f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.28;.32;.7;.74" dur="3.2s" begin="{b0}s" repeatCount="indefinite"/></circle>')
    for pid in ("fl-c", "fl-m"):
        parts.append(f'<circle class="fl-enrich" r="3.5" opacity="0"><animateMotion dur="3.2s" begin="0.6s" repeatCount="indefinite" keyPoints="0;0;1;0;0" keyTimes="0;.72;.84;.96;1" calcMode="linear"><mpath href="#{pid}"/></animateMotion>'
                     f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.7;.74;.95;1" dur="3.2s" begin="0.6s" repeatCount="indefinite"/></circle>')
    title = T(lang, "Animated diagram of my SOC log flow", "Schéma animé du flux de journaux de mon SOC")
    desc = T(lang, "Logs from endpoints and servers, the web application firewall, Active Directory, Microsoft 365 and the mail server flow into Wazuh. Only alerts at level 10 or above go on through Shuffle to TheHive, where Cortex and MISP enrich them.",
                   "Les journaux des postes et serveurs, du pare-feu applicatif, d'Active Directory, de Microsoft 365 et du serveur de messagerie arrivent dans Wazuh. Seules les alertes de niveau 10 ou plus passent par Shuffle jusqu'à TheHive, où Cortex et MISP les enrichissent.")
    return (f'<svg class="flowmap" viewBox="0 28 560 324" role="img" aria-labelledby="fl-t fl-d"><title id="fl-t">{title}</title><desc id="fl-d">{desc}</desc>'
            + "".join(parts) + "</svg>")

def cert_list(lang):
    out = []
    for c in CERT_CARDS:
        logo = (f'<img src="{c["logo"]}" alt="{c["issuer"]}" width="56" height="56" loading="lazy" decoding="async">' if c["logo"]
                else f'<span class="cert__seal">{SEAL}</span>')
        out.append(f"""<li class="cert{'' if c['done'] else ' cert--pending'}">
  <span class="cert__logo">{logo}</span>
  <span class="cert__body"><span class="cert__name">{c['name'][lang]}</span><span class="cert__issuer">{c['issuer']}</span></span>
  <span class="cert__state">{c['state'][lang]}</span>
</li>""")
    return f'<ul class="certs" role="list">{"".join(out)}</ul>'

def img_size(fname):
    from PIL import Image
    with Image.open(os.path.join(ROOT, "assets", "img", fname)) as im:
        return im.size

def figure(src, w, h, alt, notes):
    """A screenshot shows as a small preview; the full image and its notes open on click."""
    note_html = "".join(f"<li>{n}</li>" for n in notes)
    return (f'<li class="thumb"><a class="thumb__link" href="{src}" data-w="{w}" data-h="{h}">'
            f'<img src="{src.replace(".webp", "-thumb.webp")}" width="800" height="500" alt="{alt}" loading="lazy" decoding="async">'
            f'<span class="thumb__cap">{notes[0]}</span><span class="thumb__open">{EXPAND}</span></a>'
            f'<ol class="notes" hidden>{note_html}</ol></li>')

# ---------- pages ----------
def home(lang):
    pg = PAGES["home"][lang]
    if lang == "en":
        role = "Cybersecurity specialist focused on security operations and incident response."
        where = "Based in Antananarivo, Madagascar."
        intro = "I help companies detect attacks sooner and handle every incident the same way: I build their SOC, write the detection rules, and turn the response into playbooks the team can follow."
        l1, l2 = "View selected work", "Get in touch"
        now = [("Now", "SOC Team Lead at AVEOLYS, since July 2023"), ("Before", "Network and security engineer at Huawei Technologies Madagascar, 2021 to 2023"), ("Speaks", "English, French, Malagasy")]
        work_h, work_p = "Selected work", "Six pieces of work, listed the way my team lists its cases. Client findings stay with the clients."
        shot_h = "Inside CASE-01"
        shot_more = "Read the full case"
        flow_alt = "Shuffle workflow Wazuh Alerts: Wazuh webhook, Shuffle Tools step, TheHive alert, MITRE TTP step and five conditional branches that add observables"
        flow_notes = ["The Shuffle workflow I built: every Wazuh alert at level 10 or above becomes a TheHive alert.",
                      "One step adds the MITRE ATT&amp;CK techniques as TTPs; five branches add the observables the alert contains."]
        shot_alt = "Wazuh MITRE ATT&CK dashboard: alerts over the last 24 hours, top tactics, attacks by technique, and techniques per agent"
        shot_notes = ["The MITRE ATT&amp;CK view of the SOC I run at AVEOLYS, last 24 hours, taken from the live console.",
                      "Every technique on it comes from a detection rule mapped to ATT&amp;CK.",
                      "Client host names and the manager name are blurred."]
        how_h = "How I work"
        quote = "My approach is hands-on: I don't just manage security operations; I also design, build, integrate, improve, and operationalize the technologies, intelligence capabilities, and processes behind them."
        how = [("Build", "The whole stack, from deploying the tools to the detection rules, threat intelligence and monitoring."),
               ("Lead", "Daily security operations and incident investigations, with the team."),
               ("Write it down", "IR playbooks, runbooks, detection use cases and response workflows, so the team handles each incident the same way."),
               ("Align", "Policies and procedures with ISO 27001 and NIST, and detection coverage measured against MITRE ATT&amp;CK.")]
        xp_h, sk_h = "Experience", "Skills"
        more = "Full background"
        contact_h = "Get in touch"
        contact_p = "For a role, a contract or a review of your security operations. Email is the quickest way to reach me; I reply in English or French."
    else:
        role = "Spécialiste en cybersécurité, opérations de sécurité et réponse à incident."
        where = "Basé à Antananarivo, Madagascar."
        intro = "J'aide les entreprises à détecter les attaques plus tôt et à traiter chaque incident de la même façon : je construis leur SOC, j'écris les règles de détection et je transforme la réponse en playbooks que l'équipe peut suivre."
        l1, l2 = "Voir les travaux choisis", "Me contacter"
        now = [("Aujourd'hui", "SOC Team Lead chez AVEOLYS, depuis juillet 2023"), ("Avant", "Ingénieur réseau et sécurité chez Huawei Technologies Madagascar, de 2021 à 2023"), ("Langues", "Français, anglais, malgache")]
        work_h, work_p = "Travaux choisis", "Six réalisations, présentées comme mon équipe présente ses cas. Les constats des clients restent chez les clients."
        shot_h = "Au cœur de CASE-01"
        shot_more = "Lire le cas complet"
        flow_alt = "Workflow Shuffle Wazuh Alerts : webhook Wazuh, étape Shuffle Tools, alerte TheHive, étape TTP MITRE et cinq branches conditionnelles qui ajoutent les observables"
        flow_notes = ["Le workflow Shuffle que j'ai construit : chaque alerte Wazuh de niveau 10 ou plus devient une alerte TheHive.",
                      "Une étape ajoute les techniques MITRE ATT&amp;CK comme TTP ; cinq branches ajoutent les observables présents dans l'alerte."]
        shot_alt = "Tableau de bord MITRE ATT&CK de Wazuh : alertes des dernières 24 heures, tactiques principales, attaques par technique et techniques par agent"
        shot_notes = ["La vue MITRE ATT&amp;CK du SOC que je dirige chez AVEOLYS, sur les dernières 24 heures, prise dans la console en production.",
                      "Chaque technique affichée vient d'une règle de détection reliée à ATT&amp;CK.",
                      "Les noms des machines clientes et du manager sont floutés."]
        how_h = "Ma façon de travailler"
        quote = "Mon approche est concrète : je ne me contente pas de gérer les opérations de sécurité, je conçois, je construis, j'intègre, j'améliore et je mets en production les technologies, les capacités de renseignement et les processus qui les font tourner."
        how = [("Construire", "Toute la pile, du déploiement des outils aux règles de détection, au renseignement sur la menace et à la supervision."),
               ("Diriger", "Les opérations de sécurité au quotidien et les investigations, avec l'équipe."),
               ("Écrire", "Playbooks IR, runbooks, cas d'usage de détection et workflows de réponse, pour que l'équipe traite chaque incident de la même façon."),
               ("Aligner", "Politiques et procédures sur ISO 27001 et le NIST, et couverture de détection mesurée avec MITRE ATT&amp;CK.")]
        xp_h, sk_h = "Expérience", "Compétences"
        more = "Parcours complet"
        contact_h = "Me contacter"
        contact_p = "Pour un poste, une mission ou une revue de vos opérations de sécurité. L'e-mail est le moyen le plus rapide ; je réponds en français ou en anglais."
    indeed_btn = f'<a class="btn btn--line" href="{INDEED}">Indeed</a>' if INDEED else ""
    now_html = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in now)
    how_html = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in how)
    xp_html = "".join(f'<li><span class="when">{j["when"]}</span><span class="what"><b>{j["title"]}</b>{j["org"]}</span></li>' for j in EXPERIENCE[lang])
    sk_html = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in SKILLS[lang] if a not in ("Languages", "Langues"))
    flow = PROJECTS[0]["flow"][lang]
    pipe_cap = T(lang, "The log flow of the SOC I built at AVEOLYS: everything reaches Wazuh, and only alerts at level 10 or above go on to TheHive, where Cortex and MISP enrich them.",
                       "Le flux de journaux du SOC que j'ai construit chez AVEOLYS : tout arrive dans Wazuh, et seules les alertes de niveau 10 ou plus vont jusqu'à TheHive, où Cortex et MISP les enrichissent.")
    roles = T(lang, ["Detects: SIEM with behavior analytics", "Routes every level 10+ alert and removes duplicates", "Opens the alert with its observables and MITRE TTPs", "Enrich it: analyzers and threat intelligence"],
                    ["Détecte : SIEM avec analyse comportementale", "Achemine chaque alerte de niveau 10+ et retire les doublons", "Ouvre l'alerte avec ses observables et ses TTP MITRE", "L'enrichissent : analyseurs et renseignement sur la menace"])
    nodes = "".join(f'<li class="pipe__node"><b>{x}</b><span>{roles[i]}</span></li>' for i, x in enumerate(flow))
    cert_h = T(lang, "Certifications and education", "Certifications et formation")
    body = f"""<section class="hero" aria-labelledby="hello">
  <div class="frame hero__grid">
    <div class="hero__main">
      <h1 id="hello" class="enter" data-d="0">{NAME}</h1>
      <p class="hero__role enter" data-d="1">{role}</p>
      <p class="hero__where enter" data-d="2">{where}</p>
      <p class="hero__text enter" data-d="2">{intro}</p>
      <p class="hero__actions enter" data-d="3"><a class="btn btn--gold" href="#work">{l1} {DOWN}</a><a class="btn btn--line" href="{PATHS['contact'][lang]}">{l2} {ARROW}</a></p>
    </div>
    <figure class="hero__flow enter" data-d="2">
      {flow_svg(lang)}
      <figcaption>{pipe_cap}</figcaption>
    </figure>
    <dl class="hero__facts enter" data-d="4">{now_html}</dl>
  </div>
</section>

<section class="frame block" id="work" aria-labelledby="work-h">
  <div class="block__head"><h2 id="work-h">{work_h}</h2><p>{work_p}</p></div>
  {case_grid(lang)}
</section>

<section class="frame block split" aria-labelledby="how-h">
  <div class="block__head"><h2 id="how-h">{how_h}</h2></div>
  <div>
    <blockquote class="quote"><p>{quote}</p></blockquote>
    <ul class="how">{how_html}</ul>
  </div>
</section>

<section class="frame block split" aria-labelledby="ce-h">
  <div class="block__head"><h2 id="ce-h">{cert_h}</h2></div>
  {cert_list(lang)}
</section>

<section class="frame block split" aria-labelledby="xp-h">
  <div class="block__head"><h2 id="xp-h">{xp_h}</h2><p><a class="more" href="{PATHS['about'][lang]}">{more} {ARROW}</a></p></div>
  <ol class="xp">{xp_html}</ol>
</section>

<section class="frame block split" aria-labelledby="sk-h">
  <div class="block__head"><h2 id="sk-h">{sk_h}</h2></div>
  <dl class="skills">{sk_html}</dl>
</section>

<section class="reach" aria-labelledby="ct-h">
  <div class="frame reach__grid">
    <div><h2 id="ct-h">{contact_h}</h2><p>{contact_p}</p></div>
    <div class="reach__links">
      <a class="reach__mail" href="mailto:{EMAIL}">{EMAIL}</a>
      <p class="reach__also">{T(lang, "You can also find me on:", "Vous me trouverez aussi sur :")}</p>
      {social_buttons(lang)}
    </div>
  </div>
</section>"""
    ld = [person_ld(lang), {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": url(PATHS["home"][lang]), "inLanguage": lang}]
    return layout(lang, "home", PATHS["home"][lang], PATHS["home"][other(lang)], pg["title"], pg["desc"], body, ld)

def projects(lang):
    pg = PAGES["projects"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["projects"][lang])]
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="frame block" aria-label="{T(lang, "Case index", "Index des cas")}">{case_grid(lang, "h2", cta=False)}</section>'
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "CollectionPage", "name": pg["h1"], "url": url(PATHS["projects"][lang]), "inLanguage": lang,
          "hasPart": [{"@type": "CreativeWork", "name": p["title"][lang], "url": url(project_path(p, lang))} for p in PROJECTS]}]
    return layout(lang, "projects", PATHS["projects"][lang], PATHS["projects"][other(lang)], pg["title"], pg["desc"], body, ld)

def project(lang, i):
    p, ui = PROJECTS[i], UI[lang]
    path = project_path(p, lang)
    cr = [(ui["crumb_home"], PATHS["home"][lang]), (PAGES["projects"][lang]["h1"], PATHS["projects"][lang]), (p["title"][lang], path)]
    a = ui["aside"]
    prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    facts = [(T(lang, "Status", "Statut"), p["status"][lang]), (a["role"], p["role"][lang]), (a["org"], p["org"][lang]), (a["period"], p["period"][lang]), (a["tools"], ", ".join(p["tools"]))]
    facts_html = "".join(f"<div><dt>{x}</dt><dd>{y}</dd></div>" for x, y in facts)
    extra = ""
    shots = SHOTS.get(p["case"], [])
    if shots:
        facts_html += f'<div><dt>{T(lang, "Screenshots", "Captures")}</dt><dd><a href="#screens">{T(lang, f"{len(shots)}, further down", f"{len(shots)}, plus bas")}</a></dd></div>'
        for fname, alt, notes in shots:
            w, h = img_size(fname)
            extra += figure(f"/assets/img/{fname}", w, h, T(lang, *alt), [T(lang, *n) for n in notes])
    screens = ""
    if extra:
        close = T(lang, "Close", "Fermer"); prv = T(lang, "Previous screenshot", "Capture précédente"); nxt = T(lang, "Next screenshot", "Capture suivante")
        screens = (f'<section id="screens" class="frame screens"><h2>{T(lang, "Screenshots", "Captures")}</h2>'
                   f'<p class="screens__hint">{T(lang, "Select a screenshot to see it full size, with its notes. Sensitive data is blurred.", "Sélectionnez une capture pour la voir en grand, avec ses notes. Les données sensibles sont floutées.")}</p>'
                   f'<ul class="thumbs" role="list">{extra}</ul></section>'
                   f'<dialog class="viewer" aria-label="{T(lang, "Screenshot", "Capture")}"><div class="viewer__bar"><span class="viewer__count"></span>'
                   f'<button type="button" class="viewer__btn" data-go="-1" aria-label="{prv}"><svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 8H3M7 4 3 8l4 4"/></svg></button>'
                   f'<button type="button" class="viewer__btn" data-go="1" aria-label="{nxt}">{ARROW}</button>'
                   f'<button type="button" class="viewer__btn viewer__close" aria-label="{close}"><svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg></button></div>'
                   f'<img class="viewer__img" alt=""><ol class="notes viewer__notes"></ol></dialog>')
    body = page_head(lang, p["title"][lang], p["summary"][lang], cr, case=p["case"]) + f"""<div class="frame doc">
<dl class="doc__facts margin">{facts_html}</dl>
<article class="doc__body prose">{p['body'][lang]}</article>
</div>
{screens}
<nav class="frame pager" aria-label="{T(lang, 'Other cases', 'Autres cas')}">
<a href="{project_path(prev_p, lang)}"><span class="pager__dir">← {ui['prev']}</span><span class="case-tag">{prev_p['case']}</span> {prev_p['title'][lang]}</a>
<a class="pager__next" href="{project_path(next_p, lang)}"><span class="pager__dir">{ui['next']} →</span><span class="case-tag">{next_p['case']}</span> {next_p['title'][lang]}</a>
</nav>"""
    pg_title = f"{p['case']} {p['title'][lang]} | {NAME}"
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "CreativeWork", "name": p["title"][lang], "description": p["summary"][lang],
          "url": url(path), "inLanguage": lang, "author": {"@id": SITE_URL + "/#person"}, "keywords": ", ".join(t.replace("&amp;", "&") for t in p["tools"])}]
    return path, layout(lang, "projects", path, project_path(p, other(lang)), pg_title, p["summary"][lang], body, ld, og_type="article")

def about(lang):
    pg = PAGES["about"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["about"][lang])]
    xp = "".join(f"""<li class="job"><p class="when">{j['when']}</p><div><h3>{j['title']}</h3><p class="org">{j['org']}</p>
<ul>{''.join(f'<li>{x}</li>' for x in j['items'])}</ul></div></li>""" for j in EXPERIENCE[lang])
    skills = "".join(f"<div><dt>{h}</dt><dd>{t}</dd></div>" for h, t in SKILLS[lang])
    certs = "".join(f"<div><dt>{n}</dt><dd>{d}</dd></div>" for n, d in CERTS[lang])
    h_xp, h_sk, h_ce = T(lang, ("Experience", "Skills and tools", "Certifications and education"), ("Expérience", "Compétences et outils", "Certifications et formation"))
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f"""
<section class="frame block split" aria-labelledby="xp"><div class="block__head"><h2 id="xp">{h_xp}</h2></div><ol class="jobs">{xp}</ol></section>
<section class="frame block split" aria-labelledby="sk"><div class="block__head"><h2 id="sk">{h_sk}</h2></div><dl class="skills">{skills}</dl></section>
<section class="frame block split" aria-labelledby="ce"><div class="block__head"><h2 id="ce">{h_ce}</h2></div>{cert_list(lang)}</section>
"""
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "ProfilePage", "url": url(PATHS["about"][lang]), "inLanguage": lang, "mainEntity": person_ld(lang)}]
    return layout(lang, "about", PATHS["about"][lang], PATHS["about"][other(lang)], pg["title"], pg["desc"], body, ld, og_type="profile")

def contact(lang):
    pg = PAGES["contact"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["contact"][lang])]
    rows = [(T(lang, "Email", "E-mail"), f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),

            (T(lang, "Location", "Localisation"), f"{CITY}, {COUNTRY}"),
            (T(lang, "Time zone", "Fuseau horaire"), "UTC+3")]
    dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="frame block split" aria-label="{T(lang, "Contact details", "Coordonnées")}"><div></div><div><dl class="skills contact-list">{dl}</dl><p class="reach__also">{T(lang, "Email is my preferred contact. You can also find me on:", "L&#39;e-mail est mon contact préféré. Vous me trouverez aussi sur :")}</p>{social_buttons(lang)}</div></section>'
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "ContactPage", "url": url(PATHS["contact"][lang]), "inLanguage": lang, "mainEntity": {"@id": SITE_URL + "/#person"}}]
    return layout(lang, "contact", PATHS["contact"][lang], PATHS["contact"][other(lang)], pg["title"], pg["desc"], body, ld)

def privacy(lang):
    pg = PAGES["privacy"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["privacy"][lang])]
    if lang == "en":
        s = [f"<h2>Who is responsible</h2><p>This website is published by {NAME}, {CITY}, {COUNTRY}. For any question about your data, email <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>",
             "<h2>No cookies</h2><p>This site does not set any cookies and does not use advertising or tracking cookies.</p>",
             "<h2>Preferences stored in your browser</h2><p>If you switch the theme or the language, your choice is saved in your browser's local storage (the keys <code>theme</code> and <code>lang</code>) so the site remembers it. It never leaves your device. You can remove it by clearing your browser's site data.</p>"]
        if GA4_ID:
            s[1] = ("<h2>Visit statistics</h2><p>To count visits and see which pages are read, this site uses Google Analytics, which sets the cookies <code>_ga</code> and <code>_ga_*</code> for up to 2 years. "
                    "It is never used for advertising. You can block these cookies in your browser settings.</p>")
        elif CF_ANALYTICS_TOKEN:
            s.append("<h2>Visit statistics</h2><p>I use Cloudflare Web Analytics to count visits and see which pages are read. It does not use cookies, does not store your IP address and does not follow you across other websites. Data is processed by Cloudflare, Inc. (USA). See the <a href=\"https://www.cloudflare.com/privacypolicy/\" rel=\"noopener\">Cloudflare privacy policy</a>.</p>")
        elif not GA4_ID:
            s.append("<h2>Visit statistics</h2><p>No analytics are currently active on this site.</p>")
        if WEB3FORMS_KEY:
            s.append("<h2>Contact form</h2><p>When you use the contact form, your name, email address and message are sent through Web3Forms (a form delivery service) to my mailbox. I use them only to reply to you, I don't share them, and I delete them within 24 months of our last exchange. See the <a href=\"https://web3forms.com/privacy\" rel=\"noopener\">Web3Forms privacy policy</a>.</p>")
        else:
            s.append("<h2>Contacting me</h2><p>If you email me, I use your message only to reply to you, I don't share it, and I delete it within 24 months of our last exchange.</p>")
        s.append("<h2>Links to other sites</h2><p>Links to LinkedIn and Upwork open those services, which apply their own privacy policies.</p>")
        s.append(f"<h2>Your rights</h2><p>You can ask to see, correct or delete the personal data I hold about you by emailing <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. I'll reply within one month. If you are in the European Union, you can also contact your data protection authority.</p>")
    else:
        s = [f"<h2>Responsable</h2><p>Ce site est édité par {NAME}, {CITY}, {COUNTRY}. Pour toute question sur vos données, écrivez à <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>",
             "<h2>Aucun cookie</h2><p>Ce site ne dépose aucun cookie et n'utilise aucun cookie publicitaire ou de suivi.</p>",
             "<h2>Préférences enregistrées dans votre navigateur</h2><p>Si vous changez le thème ou la langue, votre choix est enregistré dans le stockage local de votre navigateur (clés <code>theme</code> et <code>lang</code>) pour que le site s'en souvienne. Il ne quitte jamais votre appareil. Vous pouvez le supprimer en effaçant les données du site dans votre navigateur.</p>"]
        if GA4_ID:
            s[1] = ("<h2>Statistiques de visite</h2><p>Pour compter les visites et voir quelles pages sont lues, ce site utilise Google Analytics, qui dépose les cookies <code>_ga</code> et <code>_ga_*</code> pour 2 ans au plus. "
                    "Ils ne servent jamais à la publicité. Vous pouvez les bloquer dans les réglages de votre navigateur.</p>")
        elif CF_ANALYTICS_TOKEN:
            s.append("<h2>Statistiques de visite</h2><p>J'utilise Cloudflare Web Analytics pour compter les visites et voir quelles pages sont lues. Ce service n'utilise pas de cookies, ne conserve pas votre adresse IP et ne vous suit pas sur d'autres sites. Les données sont traitées par Cloudflare, Inc. (États-Unis). Voir la <a href=\"https://www.cloudflare.com/fr-fr/privacypolicy/\" rel=\"noopener\">politique de confidentialité de Cloudflare</a>.</p>")
        elif not GA4_ID:
            s.append("<h2>Statistiques de visite</h2><p>Aucun outil de statistiques n'est actif sur ce site pour le moment.</p>")
        if WEB3FORMS_KEY:
            s.append("<h2>Formulaire de contact</h2><p>Quand vous utilisez le formulaire, votre nom, votre adresse e-mail et votre message sont transmis par Web3Forms (un service d'envoi de formulaires) vers ma messagerie. Je les utilise uniquement pour vous répondre, je ne les partage pas, et je les supprime dans les 24 mois suivant notre dernier échange. Voir la <a href=\"https://web3forms.com/privacy\" rel=\"noopener\" hreflang=\"en\">politique de confidentialité de Web3Forms</a> (en anglais).</p>")
        else:
            s.append("<h2>Me contacter</h2><p>Si vous m'écrivez par e-mail, j'utilise votre message uniquement pour vous répondre, je ne le partage pas, et je le supprime dans les 24 mois suivant notre dernier échange.</p>")
        s.append("<h2>Liens vers d'autres sites</h2><p>Les liens vers LinkedIn et Upwork ouvrent ces services, qui appliquent leur propre politique de confidentialité.</p>")
        s.append(f"<h2>Vos droits</h2><p>Vous pouvez demander à consulter, corriger ou supprimer les données personnelles que je détiens sur vous en écrivant à <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Je réponds sous un mois. Si vous êtes dans l'Union européenne, vous pouvez aussi saisir votre autorité de protection des données (en France, la CNIL).</p>")
    body = page_head(lang, pg["h1"], "", cr) + f'<section class="frame doc doc--single"><div class="doc__body prose legal">{"".join(s)}</div></section>'
    return layout(lang, "privacy", PATHS["privacy"][lang], PATHS["privacy"][other(lang)], pg["title"], pg["desc"], body, [breadcrumbs_ld(cr)])

def legal(lang):
    pg = PAGES["legal"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["legal"][lang])]
    if lang == "en":
        s = [f"<h2>Publisher</h2><p>{FULL_NAME}, private individual<br>{CITY}, {COUNTRY}<br>Email: <a href=\"mailto:{EMAIL}\">{EMAIL}</a></p><p>Publication director: {FULL_NAME}.</p>",
             "<h2>Content</h2><p>The texts on this site are the property of their author. Product and company names belong to their respective owners and are cited only to describe the work done.</p>",
             f"<h2>Personal data</h2><p>See the <a href=\"{PATHS['privacy'][lang]}\">privacy policy</a>.</p>"]
    else:
        s = [f"<h2>Éditeur</h2><p>{FULL_NAME}, particulier<br>{CITY}, {COUNTRY}<br>E-mail : <a href=\"mailto:{EMAIL}\">{EMAIL}</a></p><p>Directeur de la publication : {FULL_NAME}.</p>",
             "<h2>Contenu</h2><p>Les textes de ce site sont la propriété de leur auteur. Les noms de produits et d'entreprises appartiennent à leurs propriétaires respectifs et ne sont cités que pour décrire le travail réalisé.</p>",
             f"<h2>Données personnelles</h2><p>Voir la <a href=\"{PATHS['privacy'][lang]}\">politique de confidentialité</a>.</p>"]
    body = page_head(lang, pg["h1"], "", cr) + f'<section class="frame doc doc--single"><div class="doc__body prose legal">{"".join(s)}</div></section>'
    return layout(lang, "legal", PATHS["legal"][lang], PATHS["legal"][other(lang)], pg["title"], pg["desc"], body, [breadcrumbs_ld(cr)])

def not_found():
    body = """<section class="frame head" aria-labelledby="page-h">
<p class="case-tag">404</p>
<h1 id="page-h">Page not found</h1>
<p class="lede">This page doesn't exist or has moved. <a href="/">Go to the home page</a> or <a href="/projects/">see the work</a>.</p>
<p class="lede" lang="fr">Cette page n'existe pas ou a été déplacée. <a href="/fr/">Retour à l'accueil en français</a>.</p>
</section>"""
    return layout("en", "", "/404.html", "/fr/", f"Page not found | {NAME}", "This page doesn't exist.", body, noindex=True)

# ---------- write ----------
def french_spacing(html):
    # French typography: narrow no-break space before ? ! ; and no-break space before :
    for mark, sp in (("?", "\u202f"), ("!", "\u202f"), (";", "\u202f"), (":", "\u00a0")):
        html = html.replace(" " + mark + " ", sp + mark + " ").replace(" " + mark + "<", sp + mark + "<")
    return html

EXT = re.compile(r'<a ((?:class="[^"]*" )?)href="(https?://[^"]+)"([^>]*)>(.*?)</a>', re.S)

def external_links(html, lang):
    """Every link to another site opens in a new tab and says so to screen readers."""
    note = "(opens in a new tab)" if lang == "en" else "(s'ouvre dans un nouvel onglet)"
    def fix(m):
        cls, href, rest, inner = m.groups()
        if href.startswith(SITE_URL):
            return m.group(0)
        rest = re.sub(r'\s*rel="[^"]*"', "", rest)
        if "social__btn" in cls:
            return f'<a {cls}href="{href}" target="_blank" rel="noopener noreferrer"{rest}>{inner}</a>'
        return f'<a {cls}href="{href}" target="_blank" rel="noopener noreferrer"{rest}>{inner}{OUT}<span class="sr-only"> {note}</span></a>'
    i = html.find("<body")
    return html[:i] + EXT.sub(fix, html[i:])

def write(path, html):
    html = external_links(html, "fr" if path.startswith("/fr/") else "en")
    if path.startswith("/fr/"):
        html = french_spacing(html)
    target = os.path.join(ROOT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    for old in ["fr", "projects", "about", "contact", "privacy", "legal"]:
        shutil.rmtree(os.path.join(ROOT, old), ignore_errors=True)
    sitemap = []
    for lang in LANGS:
        write(PATHS["home"][lang], home(lang))
        write(PATHS["projects"][lang], projects(lang))
        write(PATHS["about"][lang], about(lang))
        write(PATHS["contact"][lang], contact(lang))
        write(PATHS["privacy"][lang], privacy(lang))
        write(PATHS["legal"][lang], legal(lang))
        for i in range(len(PROJECTS)):
            path, html = project(lang, i)
            write(path, html)
    write("/404.html", not_found())

    # sitemap with language alternates (English entries carry both)
    pairs = [(PATHS[k]["en"], PATHS[k]["fr"]) for k in ["home", "projects", "about", "contact", "privacy", "legal"]]
    pairs += [(project_path(p, "en"), project_path(p, "fr")) for p in PROJECTS]
    for en, fr in pairs:
        for loc in (en, fr):
            sitemap.append(f"""<url><loc>{url(loc)}</loc><lastmod>{LAST_UPDATED}</lastmod>
<xhtml:link rel="alternate" hreflang="en" href="{url(en)}"/><xhtml:link rel="alternate" hreflang="fr" href="{url(fr)}"/><xhtml:link rel="alternate" hreflang="x-default" href="{url(en)}"/></url>""")
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(sitemap) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    with open(os.path.join(ROOT, "site.webmanifest"), "w") as f:
        json.dump({"name": NAME, "short_name": "S. Razarison", "start_url": "/", "display": "browser", "background_color": "#0A1220", "theme_color": "#0A1220",
                   "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, f)
    # security headers for hosts that support them (Cloudflare Pages, Netlify); GitHub Pages ignores this file
    with open(os.path.join(ROOT, "_headers"), "w") as f:
        f.write(f"""/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Content-Security-Policy: {csp()}; frame-ancestors 'none'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable
""")
    # minify CSS and JS
    subprocess.run([ESBUILD, os.path.join(ROOT, "src/css/site.css"), "--minify", "--outfile=" + os.path.join(ROOT, "assets/css/site.min.css"), "--log-level=warning"], check=True)
    for js in ["theme", "main", "ga"]:
        subprocess.run([ESBUILD, os.path.join(ROOT, f"src/js/{js}.js"), "--minify", "--outfile=" + os.path.join(ROOT, f"assets/js/{js}.min.js"), "--log-level=warning"], check=True)
    print("built", len(sitemap), "pages + 404")

if __name__ == "__main__":
    main()
