#!/usr/bin/env python3
"""Builds the static site into the repository root. Run: python3 src/build.py"""
import json, os, shutil, subprocess, sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
from config import *          # noqa: F401,F403
from content import *         # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESBUILD = os.environ.get("ESBUILD", "esbuild")
ASSET_V = LAST_UPDATED.replace("-", "")

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
        "knowsLanguage": ["en", "fr", "mg"], "sameAs": [LINKEDIN, UPWORK],
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
<meta name="theme-color" content="#f6f6f3">
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
<body>
<a class="skip" href="#main">{ui['skip']}</a>
<header class="top">
  <div class="frame top__row">
    <a class="top__name" href="{PATHS['home'][lang]}">{NAME}</a>
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
    <ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><a href="{LINKEDIN}" rel="noopener">LinkedIn</a></li>
      <li><a href="{UPWORK}" rel="noopener">Upwork</a></li>
      <li><a href="{PATHS['privacy'][lang]}">{ui['footer_links'][0][1]}</a></li>
      <li><a href="{PATHS['legal'][lang]}">{ui['footer_links'][1][1]}</a></li>
    </ul>
  </div>
</footer>
</body>
</html>
"""

# ---------- shared blocks ----------
def page_head(lang, h1, lead, crumbs, case=None):
    lead_html = f'<p class="lede">{lead}</p>' if lead else ""
    tag = f'<p class="case-tag">{case}</p>' if case else ""
    return (f'<section class="frame head" aria-labelledby="page-h">{crumbs_html(lang, crumbs)}{tag}'
            f'<h1 id="page-h">{h1}</h1>{lead_html}</section>')

def case_index(lang, h="h3"):
    """The recurring idea: projects listed the way a SOC lists its cases."""
    cols = T(lang, ("Case", "What", "Where", "Status"), ("Cas", "Quoi", "Où", "Statut"))
    rows = []
    for p in PROJECTS:
        rows.append(f"""<li class="case">
  <a class="case__link" href="{project_path(p, lang)}">
    <span class="case__id">{p['case']}</span>
    <span class="case__what"><{h} class="case__title">{p['title'][lang]}</{h}><span class="case__line">{p['card'][lang]}</span></span>
    <span class="case__where">{p['org'][lang]}</span>
    <span class="case__status">{p['status'][lang]}</span>
    <span class="case__go" aria-hidden="true">→</span>
  </a>
</li>""")
    head = f'<div class="cases__head" aria-hidden="true"><span>{cols[0]}</span><span>{cols[1]}</span><span>{cols[2]}</span><span>{cols[3]}</span></div>'
    return f'<div class="cases">{head}<ol class="cases__list">{"".join(rows)}</ol></div>'

def figure(src, w, h, alt, notes):
    note_html = "".join(f"<li>{n}</li>" for n in notes)
    return (f'<figure class="shot"><img src="{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">'
            f'<figcaption><ol class="notes">{note_html}</ol></figcaption></figure>')

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
    now_html = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in now)
    how_html = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in how)
    xp_html = "".join(f'<li><span class="when">{j["when"]}</span><span class="what"><b>{j["title"]}</b>{j["org"]}</span></li>' for j in EXPERIENCE[lang])
    sk_html = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in SKILLS[lang] if a not in ("Languages", "Langues"))
    body = f"""<section class="frame intro" aria-labelledby="hello">
  <div class="intro__main">
    <h1 id="hello">{NAME}</h1>
    <p class="intro__role">{role}</p>
    <p class="intro__where">{where}</p>
    <p class="intro__text">{intro}</p>
    <p class="intro__links"><a href="#work">{l1} <span aria-hidden="true">→</span></a><a href="{PATHS['contact'][lang]}">{l2} <span aria-hidden="true">→</span></a></p>
  </div>
  <dl class="intro__side margin">{now_html}</dl>
</section>

<section class="frame block" id="work" aria-labelledby="work-h">
  <div class="block__head"><h2 id="work-h">{work_h}</h2><p>{work_p}</p></div>
  {case_index(lang)}
</section>

<section class="frame block" aria-labelledby="shot-h">
  <div class="block__head"><h2 id="shot-h">{shot_h}</h2></div>
  {figure('/assets/img/wazuh-mitre.webp', 1568, 731, shot_alt, shot_notes)}
</section>

<section class="frame block split" aria-labelledby="how-h">
  <div class="block__head"><h2 id="how-h">{how_h}</h2></div>
  <div>
    <p class="quote">{quote}</p>
    <ol class="how">{how_html}</ol>
  </div>
</section>

<section class="frame block split" aria-labelledby="xp-h">
  <div class="block__head"><h2 id="xp-h">{xp_h}</h2><p><a href="{PATHS['about'][lang]}">{more} <span aria-hidden="true">→</span></a></p></div>
  <ol class="xp">{xp_html}</ol>
</section>

<section class="frame block split" aria-labelledby="sk-h">
  <div class="block__head"><h2 id="sk-h">{sk_h}</h2></div>
  <dl class="skills">{sk_html}</dl>
</section>

<section class="frame block split contact-block" aria-labelledby="ct-h">
  <div class="block__head"><h2 id="ct-h">{contact_h}</h2></div>
  <div><p>{contact_p}</p><p class="big-link"><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
</section>"""
    ld = [person_ld(lang), {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": url(PATHS["home"][lang]), "inLanguage": lang}]
    return layout(lang, "home", PATHS["home"][lang], PATHS["home"][other(lang)], pg["title"], pg["desc"], body, ld)

def projects(lang):
    pg = PAGES["projects"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["projects"][lang])]
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="frame block" aria-label="{T(lang, "Case index", "Index des cas")}">{case_index(lang, "h2")}</section>'
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
    if p["case"] == "CASE-01":
        extra = figure("/assets/img/shuffle-workflow.webp", 1048, 806,
                       T(lang, "Shuffle workflow Wazuh Alerts: Wazuh webhook, Shuffle Tools step, TheHive alert, then five conditional branches that add observables",
                            "Workflow Shuffle Wazuh Alerts : webhook Wazuh, étape Shuffle Tools, alerte TheHive, puis cinq branches conditionnelles qui ajoutent les observables"),
                       [T(lang, "The Shuffle workflow behind this pipeline: the Wazuh webhook comes in, a Shuffle Tools step prepares it, and TheHive gets the alert.",
                              "Le workflow Shuffle derrière cette chaîne : le webhook Wazuh arrive, une étape Shuffle Tools le prépare, et TheHive reçoit l'alerte."),
                        T(lang, "Each branch adds one type of observable only when the alert contains it: source IP, target email, RDP or AD source IP, SHA256 hash, host name.",
                              "Chaque branche ajoute un type d'observable seulement si l'alerte le contient : IP source, e-mail ciblé, IP source RDP ou AD, empreinte SHA256, nom de machine."),
                        T(lang, "The step at the top reads the MITRE ATT&amp;CK technique IDs of the Wazuh rule, asks TheHive which tactic each belongs to, and adds them to the alert as TTPs. That is why every custom rule I write carries a MITRE block.",
                              "L'étape du haut lit les ID de techniques MITRE ATT&amp;CK de la règle Wazuh, demande à TheHive la tactique de chacune et les ajoute à l'alerte comme TTP. C'est pour ça que chaque règle personnalisée que j'écris porte un bloc MITRE.")])
        extra += figure("/assets/img/wazuh-overview.webp", 1568, 500,
                       T(lang, "Wazuh overview: 52 active and 15 disconnected agents, and the alerts of the last 24 hours by severity",
                            "Vue d'ensemble Wazuh : 52 agents actifs et 15 déconnectés, et les alertes des dernières 24 heures par sévérité"),
                       [T(lang, "The Wazuh overview on the day this page was written: agents connected and alerts of the last 24 hours by severity.",
                              "La vue d'ensemble Wazuh le jour où cette page a été écrite : agents connectés et alertes des dernières 24 heures par sévérité."),
                        T(lang, "Most alerts sit in the low levels on purpose: only level 10 and above opens a case.",
                              "La plupart des alertes restent volontairement aux niveaux bas : seul le niveau 10 et plus ouvre un cas.")])
        extra += figure("/assets/img/wazuh-mitre.webp", 1568, 731,
                        T(lang, "Wazuh MITRE ATT&CK dashboard with host names blurred", "Tableau de bord MITRE ATT&CK de Wazuh, noms de machines floutés"),
                        [T(lang, "The same SOC seen through MITRE ATT&amp;CK. Client host names are blurred.", "Le même SOC vu par MITRE ATT&amp;CK. Les noms des machines clientes sont floutés.")])
    body = page_head(lang, p["title"][lang], p["summary"][lang], cr, case=p["case"]) + f"""<div class="frame doc">
<dl class="doc__facts margin">{facts_html}</dl>
<article class="doc__body prose">{p['body'][lang]}{extra}</article>
</div>
<nav class="frame pager" aria-label="{T(lang, 'Other cases', 'Autres cas')}">
<a href="{project_path(prev_p, lang)}"><span class="sr-only">{ui['prev']} : </span><span class="case-tag">{prev_p['case']}</span> {prev_p['title'][lang]}</a>
<a href="{project_path(next_p, lang)}"><span class="sr-only">{ui['next']} : </span><span class="case-tag">{next_p['case']}</span> {next_p['title'][lang]}</a>
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
<section class="frame block split" aria-labelledby="ce"><div class="block__head"><h2 id="ce">{h_ce}</h2></div><dl class="skills">{certs}</dl></section>
"""
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "ProfilePage", "url": url(PATHS["about"][lang]), "inLanguage": lang, "mainEntity": person_ld(lang)}]
    return layout(lang, "about", PATHS["about"][lang], PATHS["about"][other(lang)], pg["title"], pg["desc"], body, ld, og_type="profile")

def contact(lang):
    pg = PAGES["contact"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["contact"][lang])]
    rows = [(T(lang, "Email", "E-mail"), f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),
            ("LinkedIn", f'<a href="{LINKEDIN}" rel="noopener">razarison-romeo-bienvenu-stephanio</a>'),
            ("Upwork", f'<a href="{UPWORK}" rel="noopener">{T(lang, "Upwork profile", "Profil Upwork")}</a>'),
            (T(lang, "Location", "Localisation"), f"{CITY}, {COUNTRY}"),
            (T(lang, "Time zone", "Fuseau horaire"), T(lang, "UTC+3, most of the European working day", "UTC+3, la plupart des heures de bureau européennes"))]
    dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="frame block split" aria-label="{T(lang, "Contact details", "Coordonnées")}"><div></div><dl class="skills contact-list">{dl}</dl></section>'
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "ContactPage", "url": url(PATHS["contact"][lang]), "inLanguage": lang, "mainEntity": {"@id": SITE_URL + "/#person"}}]
    return layout(lang, "contact", PATHS["contact"][lang], PATHS["contact"][other(lang)], pg["title"], pg["desc"], body, ld)

def privacy(lang):
    pg = PAGES["privacy"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["privacy"][lang])]
    upd = LAST_UPDATED
    if lang == "en":
        s = [f"<p>Last updated: {upd}.</p>",
             f"<h2>Who is responsible</h2><p>This website is published by {NAME}, {CITY}, {COUNTRY}. For any question about your data, email <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>",
             "<h2>No cookies</h2><p>This site does not set any cookies and does not use advertising or tracking cookies.</p>",
             "<h2>Preferences stored in your browser</h2><p>If you switch the theme or the language, your choice is saved in your browser's local storage (the keys <code>theme</code> and <code>lang</code>) so the site remembers it. It never leaves your device. You can remove it by clearing your browser's site data.</p>",
             "<h2>Hosting</h2><p>The site is hosted by GitHub Pages (GitHub, Inc., USA). Like any web host, GitHub processes technical data such as your IP address to deliver the pages and keep the service secure. See the <a href=\"https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement\" rel=\"noopener\">GitHub privacy statement</a>.</p>"]
        if GA4_ID:
            s[2] = "<h2>Cookies</h2><p>This site uses cookies for visit statistics with Google Analytics, never for advertising.</p>"
            s.append("<h2>Visit statistics (Google Analytics)</h2><p>I use Google Analytics 4 to count visits and see which pages are read, from which country and on which type of device. Google Analytics sets the cookies <code>_ga</code> and <code>_ga_*</code>, which last up to 2 years. Google does not record or store IP addresses in Google Analytics 4. Data is kept for 14 months, then deleted.</p>"
                     "<p>The data is processed by Google (Google Ireland Limited for visitors in Europe, Google LLC in the USA). Google LLC is certified under the EU-US Data Privacy Framework. See <a href=\"https://policies.google.com/privacy\" rel=\"noopener\">Google's privacy policy</a> and <a href=\"https://policies.google.com/technologies/partner-sites\" rel=\"noopener\">how Google uses data from sites that use its services</a>.</p>"
                     "<p>You can block these cookies in your browser settings, or install <a href=\"https://tools.google.com/dlpage/gaoptout\" rel=\"noopener\">Google's opt-out add-on</a>.</p>")
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
        s = [f"<p>Dernière mise à jour : {upd}.</p>",
             f"<h2>Responsable</h2><p>Ce site est édité par {NAME}, {CITY}, {COUNTRY}. Pour toute question sur vos données, écrivez à <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>",
             "<h2>Aucun cookie</h2><p>Ce site ne dépose aucun cookie et n'utilise aucun cookie publicitaire ou de suivi.</p>",
             "<h2>Préférences enregistrées dans votre navigateur</h2><p>Si vous changez le thème ou la langue, votre choix est enregistré dans le stockage local de votre navigateur (clés <code>theme</code> et <code>lang</code>) pour que le site s'en souvienne. Il ne quitte jamais votre appareil. Vous pouvez le supprimer en effaçant les données du site dans votre navigateur.</p>",
             "<h2>Hébergement</h2><p>Le site est hébergé par GitHub Pages (GitHub, Inc., États-Unis). Comme tout hébergeur, GitHub traite des données techniques, comme votre adresse IP, pour servir les pages et sécuriser le service. Voir la <a href=\"https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement\" rel=\"noopener\" hreflang=\"en\">déclaration de confidentialité de GitHub</a> (en anglais).</p>"]
        if GA4_ID:
            s[2] = "<h2>Cookies</h2><p>Ce site utilise des cookies pour les statistiques de visite avec Google Analytics, jamais pour la publicité.</p>"
            s.append("<h2>Statistiques de visite (Google Analytics)</h2><p>J'utilise Google Analytics 4 pour compter les visites et voir quelles pages sont lues, depuis quel pays et sur quel type d'appareil. Google Analytics dépose les cookies <code>_ga</code> et <code>_ga_*</code>, valables jusqu'à 2 ans. Google n'enregistre ni ne conserve les adresses IP dans Google Analytics 4. Les données sont conservées 14 mois, puis supprimées.</p>"
                     "<p>Les données sont traitées par Google (Google Ireland Limited pour les visiteurs en Europe, Google LLC aux États-Unis). Google LLC est certifiée au titre du cadre de protection des données UE-États-Unis (Data Privacy Framework). Voir les <a href=\"https://policies.google.com/privacy?hl=fr\" rel=\"noopener\">règles de confidentialité de Google</a> et la page <a href=\"https://policies.google.com/technologies/partner-sites?hl=fr\" rel=\"noopener\">sur l'utilisation des données par Google sur les sites partenaires</a>.</p>"
                     "<p>Vous pouvez bloquer ces cookies dans les réglages de votre navigateur, ou installer <a href=\"https://tools.google.com/dlpage/gaoptout?hl=fr\" rel=\"noopener\">le module de désactivation de Google</a>.</p>")
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
        s = [f"<h2>Publisher</h2><p>{NAME}, private individual<br>{CITY}, {COUNTRY}<br>Email: <a href=\"mailto:{EMAIL}\">{EMAIL}</a></p><p>Publication director: {NAME}.</p>",
             "<h2>Host</h2><p>GitHub, Inc.<br>88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA<br><a href=\"https://pages.github.com\" rel=\"noopener\">pages.github.com</a></p>",
             "<h2>Content</h2><p>The texts on this site are the property of their author. Product and company names belong to their respective owners and are cited only to describe the work done.</p>",
             f"<h2>Personal data</h2><p>See the <a href=\"{PATHS['privacy'][lang]}\">privacy policy</a>.</p>"]
    else:
        s = [f"<h2>Éditeur</h2><p>{NAME}, particulier<br>{CITY}, {COUNTRY}<br>E-mail : <a href=\"mailto:{EMAIL}\">{EMAIL}</a></p><p>Directeur de la publication : {NAME}.</p>",
             "<h2>Hébergeur</h2><p>GitHub, Inc.<br>88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis<br><a href=\"https://pages.github.com\" rel=\"noopener\">pages.github.com</a></p>",
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

def write(path, html):
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
