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


def consent_html(lang):
    if not GA4_ID:
        return ""
    if lang == "en":
        t, d, acc, dec, more = ("Cookies for visit statistics",
            "With your permission, I use Google Analytics to count visits and see which pages are read. It sets cookies. If you decline, nothing is loaded.",
            "Accept", "Decline", "Privacy policy")
    else:
        t, d, acc, dec, more = ("Cookies de statistiques",
            "Avec votre accord, j'utilise Google Analytics pour compter les visites et voir quelles pages sont lues. Ce service dépose des cookies. Si vous refusez, rien n'est chargé.",
            "Accepter", "Refuser", "Politique de confidentialité")
    return f"""<section class="consent" id="consent" data-ga="{GA4_ID}" aria-labelledby="consent-title" hidden>
<div class="consent-text"><h2 id="consent-title">{t}</h2><p>{d} <a href="{PATHS['privacy'][lang]}">{more}</a></p></div>
<div class="consent-actions"><button class="btn btn-ghost" type="button" data-consent="denied">{dec}</button><button class="btn btn-ghost" type="button" data-consent="granted">{acc}</button></div>
</section>
"""

def consent_link(lang):
    if not GA4_ID:
        return ""
    label = "Cookie settings" if lang == "en" else "Gestion des cookies"
    return f'<li><button class="linkish" type="button" data-consent-open>{label}</button></li>'

# ---------- layout ----------
def layout(lang, key, path, alt_path, title, desc, body, ld=None, og_type="website", noindex=False):
    ui = UI[lang]
    nav = []
    for k, label in ui["nav"]:
        cur = ' aria-current="page"' if k == key else ""
        nav.append(f'<li><a href="{PATHS[k][lang]}"{cur}>{label}</a></li>')
    langs = []
    for l in LANGS:
        name = "EN" if l == "en" else "FR"
        full = "English" if l == "en" else "Français"
        if l == lang:
            langs.append(f'<span aria-current="true" lang="{l}"><span class="sr-only">{full}</span><span aria-hidden="true">{name}</span></span>')
        else:
            langs.append(f'<a href="{alt_path}" hreflang="{l}" lang="{l}"><span class="sr-only">{full}</span><span aria-hidden="true">{name}</span></a>')
    footer_links = "".join(f'<li><a href="{PATHS[k][lang]}">{label}</a></li>' for k, label in ui["footer_links"])
    lds = ld or []
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    analytics = ""
    if CF_ANALYTICS_TOKEN:
        analytics = f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{CF_ANALYTICS_TOKEN}"}}\'></script>'
    canonical = url(path)
    hreflang = ""
    if alt_path and key:
        en_p, fr_p = (path, alt_path) if lang == "en" else (alt_path, path)
        hreflang = (f'<link rel="alternate" hreflang="en" href="{url(en_p)}"><link rel="alternate" hreflang="fr" href="{url(fr_p)}">'
                    f'<link rel="alternate" hreflang="x-default" href="{url(en_p)}">')
    og_img = url(f"/assets/img/og-{lang}.png")
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="dark">
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
<meta name="theme-color" content="#0A1220">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/sora.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/main.min.css?v={ASSET_V}">
<script src="/assets/js/theme.min.js?v={ASSET_V}"></script>
<script defer src="/assets/js/main.min.js?v={ASSET_V}"></script>
{analytics}{ld_html}
</head>
<body>
<a class="skip" href="#main">{ui['skip']}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{PATHS['home'][lang]}"><span class="brand-mark" aria-hidden="true">SR</span><span class="brand-name">{NAME}</span><span class="sr-only">, {UI[lang]['nav'][0][1]}</span></a>
    <div class="tools">
      <div class="lang" role="group" aria-label="{ui['lang_label']}">{''.join(langs)}</div>
      <button class="icon-btn theme-toggle" type="button" aria-pressed="true"><span class="sr-only">{ui['theme']}</span>{ICONS['moon']}{ICONS['sun']}</button>
      <button class="icon-btn menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="sr-only">{ui['menu']}</span>{ICONS['menu']}</button>
    </div>
    <nav class="nav" id="site-nav" aria-label="{'Main' if lang == 'en' else 'Principale'}"><ul>{''.join(nav)}</ul></nav>
  </div>
</header>
<main id="main" tabindex="-1">
{body}
</main>
{consent_html(lang)}<footer class="site-footer">
  <div class="wrap">
    <p>{ui['footer_rights']}</p>
    <ul>{footer_links}{consent_link(lang)}<li><a href="{LINKEDIN}" rel="noopener">LinkedIn</a></li><li><a href="{UPWORK}" rel="noopener">Upwork</a></li></ul>
  </div>
</footer>
</body>
</html>
"""

# ---------- shared blocks ----------
def chips(tools):
    return '<ul class="chips">' + "".join(f"<li>{t}</li>" for t in tools) + "</ul>"

def project_cards(lang, projects, h="h3"):
    out = []
    for p in projects:
        out.append(f"""<article class="card">
  <p class="meta">{p['meta'][lang]}</p>
  <{h}><a href="{project_path(p, lang)}">{p['title'][lang]}</a></{h}>
  <p>{p['summary'][lang]}</p>
  {chips(p['tools'][:4])}
</article>""")
    return '<div class="grid">' + "".join(out) + "</div>"

def cta(lang):
    if lang == "en":
        h, p, a1, a2 = "Need help securing your systems?", "SOC setup and tuning, incident response, penetration tests or an Active Directory audit. I work remotely, in English or French.", "Get in touch", "See my experience"
    else:
        h, p, a1, a2 = "Besoin de sécuriser vos systèmes ?", "Mise en place ou réglage d'un SOC, réponse à incident, tests d'intrusion ou audit Active Directory. Je travaille à distance, en français ou en anglais.", "Me contacter", "Voir mon parcours"
    return f"""<section class="section" aria-labelledby="cta-title"><div class="wrap"><div class="cta">
<h2 id="cta-title">{h}</h2><p>{p}</p>
<div class="actions"><a class="btn btn-primary" href="{PATHS['contact'][lang]}">{a1}</a><a class="btn btn-ghost" href="{PATHS['about'][lang]}">{a2}</a></div>
</div></div></section>"""

def feed_li(item):
    color, title, desc, tag = item
    return f'<li><i class="dot dot-{color}" aria-hidden="true"></i><span><b>{title}</b><span class="d">{desc}</span></span><span class="tag tag-{color}">{tag}</span></li>'

# ---------- pages ----------
def home(lang):
    ui, pg = UI[lang], PAGES["home"][lang]
    if lang == "en":
        badge, lead = "Open to remote work", "I build and run security operations: SIEM and automated response, incident handling, penetration tests and Active Directory audits. Five years in the field, currently leading the SOC team at AVEOLYS in Antananarivo, Madagascar."
        b1, b2, feed_h, feed_s = "View my projects", "Contact me", "Alerts my SOC handles", "Examples"
        facts_h, proj_h, proj_p = "In numbers", "Selected projects", "Real work for AVEOLYS and its clients. Each case study explains what I did and how."
    else:
        badge, lead = "Ouvert au travail à distance", "Je construis et j'exploite des opérations de sécurité : SIEM et réponse automatisée, gestion des incidents, tests d'intrusion et audits Active Directory. Cinq ans dans le métier, je dirige aujourd'hui l'équipe SOC d'AVEOLYS à Antananarivo, Madagascar."
        b1, b2, feed_h, feed_s = "Voir mes projets", "Me contacter", "Alertes traitées par mon SOC", "Exemples"
        facts_h, proj_h, proj_p = "En chiffres", "Projets choisis", "Du vrai travail pour AVEOLYS et ses clients. Chaque étude de cas explique ce que j'ai fait et comment."
    feed = FEED[lang]
    facts = "".join(f'<div class="fact"><b>{n}</b><span>{t}</span></div>' for n, t in FACTS[lang])
    body = f"""<section class="hero" aria-labelledby="hero-title">
<canvas id="net" aria-hidden="true"></canvas>
<div class="wrap">
  <div>
    <p class="badge"><i aria-hidden="true"></i>{badge}</p>
    <h1 id="hero-title">{NAME}</h1>
    <p class="title">{ui['title']}</p>
    <p class="lead">{lead}</p>
    <div class="actions"><a class="btn btn-primary" href="{PATHS['projects'][lang]}">{b1}</a><a class="btn btn-ghost" href="{PATHS['contact'][lang]}">{b2}</a></div>
  </div>
  <section class="feed-card" aria-labelledby="feed-title">
    <h2 id="feed-title">{feed_h} <small>{feed_s}</small></h2>
    <ul class="feed" id="feed">{''.join(feed_li(x) for x in feed[:4])}</ul>
    <template id="feed-items">{''.join(feed_li(x) for x in feed[4:] + feed[:4])}</template>
  </section>
</div>
</section>
<section class="section" aria-labelledby="facts-title"><div class="wrap">
  <h2 class="sr-only" id="facts-title">{facts_h}</h2>
  <div class="facts">{facts}</div>
</div></section>
<section class="section" aria-labelledby="proj-title"><div class="wrap">
  <div class="section-head"><h2 id="proj-title">{proj_h}</h2><p>{proj_p}</p></div>
  {project_cards(lang, PROJECTS[:3])}
  <div class="actions"><a class="btn btn-ghost" href="{PATHS['projects'][lang]}">{ui['all_projects']}</a></div>
</div></section>
{cta(lang)}"""
    ld = [person_ld(lang), {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": url(PATHS["home"][lang]), "inLanguage": lang}]
    return layout(lang, "home", PATHS["home"][lang], PATHS["home"][other(lang)], pg["title"], pg["desc"], body, ld)

def page_head(lang, h1, lead, crumbs):
    lead_html = f"<p>{lead}</p>" if lead else ""
    return f'<div class="page-head"><div class="wrap">{crumbs_html(lang, crumbs)}<h1>{h1}</h1>{lead_html}</div></div>'

def projects(lang):
    pg = PAGES["projects"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["projects"][lang])]
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="section" aria-label="{pg["h1"]}"><div class="wrap">{project_cards(lang, PROJECTS, "h2")}</div></section>' + cta(lang)
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "CollectionPage", "name": pg["h1"], "url": url(PATHS["projects"][lang]), "inLanguage": lang,
          "hasPart": [{"@type": "CreativeWork", "name": p["title"][lang], "url": url(project_path(p, lang))} for p in PROJECTS]}]
    return layout(lang, "projects", PATHS["projects"][lang], PATHS["projects"][other(lang)], pg["title"], pg["desc"], body, ld)

def project(lang, i):
    p, ui = PROJECTS[i], UI[lang]
    path = project_path(p, lang)
    cr = [(ui["crumb_home"], PATHS["home"][lang]), (PAGES["projects"][lang]["h1"], PATHS["projects"][lang]), (p["title"][lang], path)]
    a = ui["aside"]
    prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    body = page_head(lang, p["title"][lang], p["summary"][lang], cr) + f"""<section class="section"><div class="wrap detail">
<div class="body">{p['body'][lang]}
<nav class="pager" aria-label="{'Projects' if lang == 'en' else 'Projets'}">
<a href="{project_path(prev_p, lang)}"><span class="sr-only">{ui['prev']}: </span>← {prev_p['title'][lang]}</a>
<a href="{project_path(next_p, lang)}"><span class="sr-only">{ui['next']}: </span>{next_p['title'][lang]} →</a>
</nav></div>
<aside class="aside" aria-label="{'Project summary' if lang == 'en' else 'Résumé du projet'}"><dl>
<div><dt>{a['role']}</dt><dd>{p['role'][lang]}</dd></div>
<div><dt>{a['org']}</dt><dd>{p['org'][lang]}</dd></div>
<div><dt>{a['period']}</dt><dd>{p['period'][lang]}</dd></div>
<div><dt>{a['tools']}</dt><dd>{chips(p['tools'])}</dd></div>
</dl></aside>
</div></section>""" + cta(lang)
    pg_title = f"{p['title'][lang]} | {NAME}"
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "CreativeWork", "name": p["title"][lang], "description": p["summary"][lang],
          "url": url(path), "inLanguage": lang, "author": {"@id": SITE_URL + "/#person"}, "keywords": ", ".join(t.replace("&amp;", "&") for t in p["tools"])}]
    return path, layout(lang, "projects", path, project_path(p, other(lang)), pg_title, p["summary"][lang], body, ld, og_type="article")

def about(lang):
    pg = PAGES["about"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["about"][lang])]
    xp = "".join(f"""<li><p class="when">{j['when']}</p><h3>{j['title']}</h3><p class="org">{j['org']}</p>
<ul class="list">{''.join(f'<li>{x}</li>' for x in j['items'])}</ul></li>""" for j in EXPERIENCE[lang])
    skills = "".join(f'<div class="panel"><h3>{h}</h3><p>{t}</p></div>' for h, t in SKILLS[lang])
    certs = "".join(f"<li><b>{n}</b><span>{d}</span></li>" for n, d in CERTS[lang])
    h_xp, h_sk, h_ce = ("Experience", "Skills", "Certifications and education") if lang == "en" else ("Expérience", "Compétences", "Certifications et formation")
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f"""
<section class="section" aria-labelledby="xp"><div class="wrap"><div class="section-head"><h2 id="xp">{h_xp}</h2></div><ol class="timeline">{xp}</ol></div></section>
<section class="section" aria-labelledby="sk"><div class="wrap"><div class="section-head"><h2 id="sk">{h_sk}</h2></div><div class="cols">{skills}</div></div></section>
<section class="section" aria-labelledby="ce"><div class="wrap"><div class="section-head"><h2 id="ce">{h_ce}</h2></div><ul class="certs">{certs}</ul></div></section>
""" + cta(lang)
    ld = [breadcrumbs_ld(cr), {"@context": "https://schema.org", "@type": "ProfilePage", "url": url(PATHS["about"][lang]), "inLanguage": lang, "mainEntity": person_ld(lang)}]
    return layout(lang, "about", PATHS["about"][lang], PATHS["about"][other(lang)], pg["title"], pg["desc"], body, ld, og_type="profile")

def contact(lang):
    pg = PAGES["contact"][lang]
    cr = [(UI[lang]["crumb_home"], PATHS["home"][lang]), (pg["h1"], PATHS["contact"][lang])]
    if lang == "en":
        L = dict(email="Email", li="LinkedIn", up="Upwork", where="Location", loc=f"{CITY}, {COUNTRY} (UTC+3)", form_h="Send a message",
                 name="Your name", mail="Your email", msg="Your message", msg_hint="At least 20 characters.", send="Send message",
                 req="This field is required.", bad="Enter a valid email address, for example name@company.com.", short="Your message is too short: write at least 20 characters.",
                 sending="Sending…", sent="Thank you, your message has been sent. I'll reply by email.", failed="The message could not be sent. Please email me directly at " + EMAIL + ".",
                 note=f'Your name, email and message are only used to reply to you. They are delivered by Web3Forms and kept in my mailbox. See the <a href="{PATHS["privacy"][lang]}">privacy policy</a>.',
                 noform="There is no contact form on this site: your message goes straight to my mailbox and no third party stores it.")
    else:
        L = dict(email="E-mail", li="LinkedIn", up="Upwork", where="Localisation", loc=f"{CITY}, {COUNTRY} (UTC+3)", form_h="Envoyer un message",
                 name="Votre nom", mail="Votre e-mail", msg="Votre message", msg_hint="20 caractères minimum.", send="Envoyer le message",
                 req="Ce champ est obligatoire.", bad="Saisissez une adresse e-mail valide, par exemple nom@entreprise.com.", short="Votre message est trop court : écrivez au moins 20 caractères.",
                 sending="Envoi en cours…", sent="Merci, votre message a bien été envoyé. Je vous répondrai par e-mail.", failed="Le message n'a pas pu être envoyé. Écrivez-moi directement à " + EMAIL + ".",
                 note=f'Votre nom, votre e-mail et votre message servent uniquement à vous répondre. Ils sont transmis par Web3Forms et conservés dans ma messagerie. Voir la <a href="{PATHS["privacy"][lang]}">politique de confidentialité</a>.',
                 noform="Ce site n'a pas de formulaire de contact : votre message arrive directement dans ma messagerie et aucun tiers ne le conserve.")
    links = f"""<ul class="links-list">
<li><span>{L['email']}</span><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li><span>{L['li']}</span><a href="{LINKEDIN}" rel="noopener">linkedin.com/in/razarison-romeo-bienvenu-stephanio</a></li>
<li><span>{L['up']}</span><a href="{UPWORK}" rel="noopener">{'Upwork profile' if lang == 'en' else 'Profil Upwork'}</a></li>
<li><span>{L['where']}</span>{L['loc']}</li>
</ul>"""
    if WEB3FORMS_KEY:
        right = f"""<form class="contact" action="https://api.web3forms.com/submit" method="post" novalidate aria-labelledby="form-title"
 data-required="{L['req']}" data-email="{L['bad']}" data-short="{L['short']}" data-sending="{L['sending']}" data-sent="{L['sent']}" data-failed="{escape(L['failed'])}">
<h2 id="form-title">{L['form_h']}</h2>
<input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
<input type="hidden" name="subject" value="Portfolio contact">
<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="field"><label for="name">{L['name']}</label><input id="name" name="name" type="text" autocomplete="name" required aria-describedby="name-error"><p class="error" id="name-error" aria-live="polite"></p></div>
<div class="field"><label for="email">{L['mail']}</label><input id="email" name="email" type="email" autocomplete="email" required aria-describedby="email-error"><p class="error" id="email-error" aria-live="polite"></p></div>
<div class="field"><label for="message">{L['msg']}</label><p class="hint" id="message-hint">{L['msg_hint']}</p><textarea id="message" name="message" required minlength="20" aria-describedby="message-hint message-error"></textarea><p class="error" id="message-error" aria-live="polite"></p></div>
<button class="btn btn-primary" type="submit">{L['send']}</button>
<p class="form-status" role="status" aria-live="polite"></p>
<p class="privacy-note">{L['note']}</p>
</form>"""
    else:
        right = f'<div class="panel"><p>{L["noform"]}</p><div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}">{L["email"]}: {EMAIL}</a></div></div>'
    body = page_head(lang, pg["h1"], pg["lead"], cr) + f'<section class="section"><div class="wrap contact-grid"><div>{links}</div><div>{right}</div></div></section>'
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
            s[2] = "<h2>Cookies</h2><p>This site sets cookies only if you accept them in the banner. They are used for visit statistics with Google Analytics, never for advertising.</p>"
            s.append("<h2>Visit statistics (Google Analytics)</h2><p>If you click \"Accept\", I use Google Analytics 4 to count visits and see which pages are read, from which country and on which type of device. Google Analytics sets the cookies <code>_ga</code> and <code>_ga_*</code>, which last up to 2 years. Google does not record or store IP addresses in Google Analytics 4. Data is kept for 14 months, then deleted.</p>"
                     "<p>The data is processed by Google (Google Ireland Limited for visitors in Europe, Google LLC in the USA). Google LLC is certified under the EU-US Data Privacy Framework. See <a href=\"https://policies.google.com/privacy\" rel=\"noopener\">Google's privacy policy</a> and <a href=\"https://policies.google.com/technologies/partner-sites\" rel=\"noopener\">how Google uses data from sites that use its services</a>.</p>"
                     "<p>If you click \"Decline\", or don't answer, no Google script is loaded. You can change your choice at any time with the \"Cookie settings\" link at the bottom of every page. Your choice is remembered in your browser's local storage (key <code>consent</code>) for 13 months.</p>")
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
            s[2] = "<h2>Cookies</h2><p>Ce site ne dépose des cookies que si vous les acceptez dans le bandeau. Ils servent aux statistiques de visite avec Google Analytics, jamais à la publicité.</p>"
            s.append("<h2>Statistiques de visite (Google Analytics)</h2><p>Si vous cliquez sur « Accepter », j'utilise Google Analytics 4 pour compter les visites et voir quelles pages sont lues, depuis quel pays et sur quel type d'appareil. Google Analytics dépose les cookies <code>_ga</code> et <code>_ga_*</code>, valables jusqu'à 2 ans. Google n'enregistre ni ne conserve les adresses IP dans Google Analytics 4. Les données sont conservées 14 mois, puis supprimées.</p>"
                     "<p>Les données sont traitées par Google (Google Ireland Limited pour les visiteurs en Europe, Google LLC aux États-Unis). Google LLC est certifiée au titre du cadre de protection des données UE-États-Unis (Data Privacy Framework). Voir les <a href=\"https://policies.google.com/privacy?hl=fr\" rel=\"noopener\">règles de confidentialité de Google</a> et la page <a href=\"https://policies.google.com/technologies/partner-sites?hl=fr\" rel=\"noopener\">sur l'utilisation des données par Google sur les sites partenaires</a>.</p>"
                     "<p>Si vous cliquez sur « Refuser », ou si vous ne répondez pas, aucun script Google n'est chargé. Vous pouvez changer d'avis à tout moment avec le lien « Gestion des cookies » en bas de chaque page. Votre choix est mémorisé dans le stockage local de votre navigateur (clé <code>consent</code>) pendant 13 mois.</p>")
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
    body = page_head(lang, pg["h1"], "", cr) + f'<section class="section"><div class="wrap prose legal">{"".join(s)}</div></section>'
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
    body = page_head(lang, pg["h1"], "", cr) + f'<section class="section"><div class="wrap prose legal">{"".join(s)}</div></section>'
    return layout(lang, "legal", PATHS["legal"][lang], PATHS["legal"][other(lang)], pg["title"], pg["desc"], body, [breadcrumbs_ld(cr)])

def not_found():
    body = """<section class="notfound"><div class="wrap">
<h1>Page not found</h1>
<p>This page doesn't exist or has moved. Check the address, or go back to the home page.</p>
<div class="actions"><a class="btn btn-primary" href="/">Go to the home page</a><a class="btn btn-ghost" href="/projects/">See the projects</a></div>
<p lang="fr">Page introuvable. Cette page n'existe pas ou a été déplacée. <a href="/fr/">Retour à l'accueil en français</a>.</p>
</div></section>"""
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
    subprocess.run([ESBUILD, os.path.join(ROOT, "src/css/main.css"), "--minify", "--outfile=" + os.path.join(ROOT, "assets/css/main.min.css"), "--log-level=warning"], check=True)
    for js in ["theme", "main"]:
        subprocess.run([ESBUILD, os.path.join(ROOT, f"src/js/{js}.js"), "--minify", "--outfile=" + os.path.join(ROOT, f"assets/js/{js}.min.js"), "--log-level=warning"], check=True)
    print("built", len(sitemap), "pages + 404")

if __name__ == "__main__":
    main()
