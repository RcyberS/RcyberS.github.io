# All page text, in English (default) and French. Facts here come only from the site owner.
from config import EMAIL, NAME

LANGS = ["en", "fr"]

UI = {
    "en": {
        "skip": "Skip to content",
        "nav": [("home", "Home"), ("projects", "Projects"), ("about", "About"), ("contact", "Contact")],
        "menu": "Menu",
        "theme": "Dark theme",
        "lang_label": "Language",
        "title": "Cybersecurity Specialist | Defensive, Offensive & Cloud Security",
        "footer_rights": f"© 2026 {NAME}",
        "footer_links": [("privacy", "Privacy policy"), ("legal", "Legal notice")],
        "crumb_home": "Home",
        "read_project": "Read the case study",
        "all_projects": "All projects",
        "prev": "Previous project",
        "next": "Next project",
        "aside": {"role": "My role", "org": "Where", "period": "When", "tools": "Tools"},
    },
    "fr": {
        "skip": "Aller au contenu",
        "nav": [("home", "Accueil"), ("projects", "Projets"), ("about", "À propos"), ("contact", "Contact")],
        "menu": "Menu",
        "theme": "Thème sombre",
        "lang_label": "Langue",
        "title": "Spécialiste en cybersécurité | Sécurité défensive, offensive et cloud",
        "footer_rights": f"© 2026 {NAME}",
        "footer_links": [("privacy", "Politique de confidentialité"), ("legal", "Mentions légales")],
        "crumb_home": "Accueil",
        "read_project": "Lire l'étude de cas",
        "all_projects": "Tous les projets",
        "prev": "Projet précédent",
        "next": "Projet suivant",
        "aside": {"role": "Mon rôle", "org": "Où", "period": "Quand", "tools": "Outils"},
    },
}

# URL paths per page and language
PATHS = {
    "home": {"en": "/", "fr": "/fr/"},
    "projects": {"en": "/projects/", "fr": "/fr/projets/"},
    "about": {"en": "/about/", "fr": "/fr/a-propos/"},
    "contact": {"en": "/contact/", "fr": "/fr/contact/"},
    "privacy": {"en": "/privacy/", "fr": "/fr/confidentialite/"},
    "legal": {"en": "/legal/", "fr": "/fr/mentions-legales/"},
}

FACTS = {
    "en": [("5", "years in cybersecurity"), ("62", "endpoints and servers monitored"), ("12", "incident response playbooks written"), ("4", "firewall vendors operated")],
    "fr": [("5", "ans en cybersécurité"), ("62", "postes et serveurs supervisés"), ("12", "playbooks de réponse à incident rédigés"), ("4", "constructeurs de pare-feu exploités")],
}

FEED = {
    "en": [("red", "VPN brute-force", "Source IP blocked", "Blocked"), ("blue", "Kerberoasting attempt", "Case opened in TheHive", "Investigating"),
           ("green", "Phishing link clicked", "Mailbox cleaned", "Resolved"), ("red", "Malware on a laptop", "Endpoint isolated", "Contained"),
           ("blue", "Mail forwarding rule", "Checked with the user", "Investigating"), ("green", "New admin account", "Confirmed with IT", "Resolved"),
           ("red", "Internet port scan", "Blocked at the firewall", "Blocked"), ("green", "Audit policy change", "Machine account, noise", "Resolved")],
    "fr": [("red", "Force brute sur le VPN", "IP source bloquée", "Bloqué"), ("blue", "Tentative de Kerberoasting", "Cas ouvert dans TheHive", "En analyse"),
           ("green", "Lien de phishing cliqué", "Boîte mail nettoyée", "Résolu"), ("red", "Malware sur un portable", "Poste isolé", "Contenu"),
           ("blue", "Règle de transfert mail", "Vérifiée avec l'utilisateur", "En analyse"), ("green", "Nouveau compte admin", "Confirmé avec l'IT", "Résolu"),
           ("red", "Scan de ports depuis Internet", "Bloqué au pare-feu", "Bloqué"), ("green", "Changement de politique d'audit", "Compte machine, bruit", "Résolu")],
}

EXPERIENCE = {
    "en": [
        {"when": "July 2023 – present", "title": "SOC Team Lead", "org": "AVEOLYS, Antananarivo", "items": [
            "Built the company's SOC from scratch: Wazuh SIEM with behavior analytics, and an automated response pipeline on Shuffle, TheHive and Cortex with MISP threat intelligence.",
            "Lead the team through the full incident lifecycle: detection, qualification, investigation, containment and post-incident review.",
            "Wrote the custom detection rules for mail, the web application firewall, Microsoft 365 and Active Directory, each mapped to MITRE ATT&amp;CK.",
            "Wrote the incident response playbooks and runbooks, keep them up to date after each incident, and run tabletop exercises.",
            "Carry out penetration tests and security audits for client companies, and Active Directory audits with the ANSSI's ORADAD tool.",
            "Deployed Keycloak single sign-on with MFA for internal and client applications.",
            "Operate Sophos, Stormshield and Forcepoint firewalls, Suricata IDS/IPS, a WAF and Bitdefender GravityZone."]},
        {"when": "May 2021 – June 2023", "title": "Network &amp; Security Engineer", "org": "Huawei Technologies Madagascar", "items": [
            "Deployed and administered Huawei USG6700E next-generation firewalls and the HiSec Endpoint and HiSec Insight security platforms.",
            "Designed and ran MPLS, IPsec VPN, OSPF and BGP networks, with VLAN segmentation, 802.1X access control and VRRP redundancy.",
            "Contributed to identity and access management and to business continuity and disaster recovery plans."]},
        {"when": "June – August 2019", "title": "IT Security Intern", "org": "MICTSL (Madagascar International Container Terminal Services Ltd)", "items": [
            "Implemented SolarWinds Security Event Manager (SEM) as the company's SIEM.",
            "Connected the network devices and servers to SEM so their security logs were collected in one place.",
            "Set up alert rules and reports in SEM to spot suspicious events.",
            "Applied security patches to workstations and servers.",
            "Supported the administration of the LAN and Wi-Fi network."]},
    ],
    "fr": [
        {"when": "Juillet 2023 – aujourd'hui", "title": "SOC Team Lead", "org": "AVEOLYS, Antananarivo", "items": [
            "Création du SOC de l'entreprise à partir de zéro : SIEM Wazuh avec analyse comportementale, et chaîne de réponse automatisée avec Shuffle, TheHive et Cortex, enrichie par MISP.",
            "Pilotage de l'équipe sur tout le cycle de vie des incidents : détection, qualification, investigation, confinement et retour d'expérience.",
            "Rédaction des règles de détection sur mesure pour la messagerie, le WAF, Microsoft 365 et Active Directory, chacune reliée à MITRE ATT&amp;CK.",
            "Rédaction des playbooks et runbooks de réponse à incident, mis à jour après chaque incident, et animation d'exercices sur table.",
            "Tests d'intrusion et audits de sécurité pour des entreprises clientes, et audits Active Directory avec l'outil ORADAD de l'ANSSI.",
            "Déploiement de l'authentification unique Keycloak avec MFA pour les applications internes et clientes.",
            "Exploitation de pare-feu Sophos, Stormshield et Forcepoint, de l'IDS/IPS Suricata, d'un WAF et de Bitdefender GravityZone."]},
        {"when": "Mai 2021 – juin 2023", "title": "Ingénieur réseau et sécurité", "org": "Huawei Technologies Madagascar", "items": [
            "Déploiement et administration des pare-feu nouvelle génération Huawei USG6700E et des plateformes de sécurité HiSec Endpoint et HiSec Insight.",
            "Conception et exploitation de réseaux MPLS, VPN IPsec, OSPF et BGP, avec segmentation VLAN, contrôle d'accès 802.1X et redondance VRRP.",
            "Participation à la gestion des identités et des accès, et aux plans de continuité et de reprise d'activité."]},
        {"when": "Juin – août 2019", "title": "Stagiaire en sécurité informatique", "org": "MICTSL (Madagascar International Container Terminal Services Ltd)", "items": [
            "Mise en place de SolarWinds Security Event Manager (SEM) comme SIEM de l'entreprise.",
            "Raccordement des équipements réseau et des serveurs à SEM pour centraliser leurs journaux de sécurité.",
            "Configuration de règles d'alerte et de rapports dans SEM pour repérer les événements suspects.",
            "Application des correctifs de sécurité sur les postes et les serveurs.",
            "Appui à l'administration du réseau local et du Wi-Fi."]},
    ],
}

SKILLS = {
    "en": [
        ("Defensive security", "SIEM (Wazuh, ELK, SolarWinds SEM), SOAR (Shuffle, TheHive, Cortex), incident response, threat hunting, threat intelligence (MISP), malware analysis in a sandbox, YARA, EDR (Bitdefender GravityZone)"),
        ("Offensive security", "Penetration testing, Active Directory attacks (Kerberoasting, Pass-the-Hash), BloodHound, Impacket, Mimikatz, vulnerability scanning (OpenVAS), Internet exposure reviews"),
        ("Cloud and identity", "Microsoft 365 and Exchange Online monitoring, Keycloak SSO, MFA, OIDC and SAML, Active Directory and Kerberos, AD auditing (ORADAD, PingCastle)"),
        ("Network security", "Next-generation firewalls (Sophos, Stormshield, Forcepoint, Huawei USG), Suricata IDS/IPS, WAF, IPsec and MPLS VPN, OSPF, BGP, VLAN, 802.1X"),
        ("Frameworks", "MITRE ATT&amp;CK, NIST CSF, NIST SP 800-61, ISO 27001, GDPR"),
        ("Languages", "English and French, fluent. Malagasy, native."),
    ],
    "fr": [
        ("Sécurité défensive", "SIEM (Wazuh, ELK, SolarWinds SEM), SOAR (Shuffle, TheHive, Cortex), réponse à incident, threat hunting, renseignement sur la menace (MISP), analyse de malware en sandbox, YARA, EDR (Bitdefender GravityZone)"),
        ("Sécurité offensive", "Tests d'intrusion, attaques Active Directory (Kerberoasting, Pass-the-Hash), BloodHound, Impacket, Mimikatz, scan de vulnérabilités (OpenVAS), revue de l'exposition Internet"),
        ("Cloud et identité", "Supervision de Microsoft 365 et Exchange Online, SSO Keycloak, MFA, OIDC et SAML, Active Directory et Kerberos, audit AD (ORADAD, PingCastle)"),
        ("Sécurité réseau", "Pare-feu nouvelle génération (Sophos, Stormshield, Forcepoint, Huawei USG), IDS/IPS Suricata, WAF, VPN IPsec et MPLS, OSPF, BGP, VLAN, 802.1X"),
        ("Référentiels", "MITRE ATT&amp;CK, NIST CSF, NIST SP 800-61, ISO 27001, RGPD"),
        ("Langues", "Anglais et français courants. Malgache, langue maternelle."),
    ],
}

CERTS = {
    "en": [("Certified SOC Analyst (CSA)", "EC-Council"), ("CISSP", "ISC2, in preparation"), ("Ethical Hacker", "Cisco"), ("Bachelor's degree in Systems and Networks", "IST Antsiranana, 2021")],
    "fr": [("Certified SOC Analyst (CSA)", "EC-Council"), ("CISSP", "ISC2, en préparation"), ("Ethical Hacker", "Cisco"), ("Licence en systèmes et réseaux", "IST Antsiranana, 2021")],
}

def flow(items):
    out = []
    for i, x in enumerate(items):
        if i:
            out.append('<li class="arrow" aria-hidden="true">→</li>')
        out.append(f"<li>{x}</li>")
    return '<div class="diagram"><ol class="flow">' + "".join(out) + "</ol></div>"

PROJECTS = [
  {
    "slug": {"en": "building-a-soc", "fr": "creation-soc"},
    "title": {"en": "Building a SOC from scratch", "fr": "Créer un SOC à partir de zéro"},
    "summary": {"en": "A full detection and response platform: SIEM, automated case handling and threat intelligence, now watching 62 endpoints and servers.",
                "fr": "Une plateforme complète de détection et de réponse : SIEM, gestion automatisée des cas et renseignement sur la menace, qui supervise aujourd'hui 62 postes et serveurs."},
    "meta": {"en": "AVEOLYS · 2023 – present", "fr": "AVEOLYS · 2023 – aujourd'hui"},
    "role": {"en": "Design, deployment and operation", "fr": "Conception, déploiement et exploitation"},
    "org": {"en": "AVEOLYS, Antananarivo", "fr": "AVEOLYS, Antananarivo"},
    "period": {"en": "July 2023 – present", "fr": "Juillet 2023 – aujourd'hui"},
    "tools": ["Wazuh", "Shuffle", "TheHive", "Cortex", "MISP", "Suricata", "Sysmon"],
    "body": {
      "en": """<h2>Starting point</h2>
<p>When I joined AVEOLYS in July 2023, the company had no Security Operations Center. Logs stayed on each server and nobody was alerted when something went wrong.</p>
<h2>What I built</h2>
<p>I deployed <strong>Wazuh</strong> as the SIEM, with a user-behavior analytics layer, and connected it to an automated pipeline:</p>
""" + flow(["Wazuh", "Shuffle", "TheHive", "Cortex + MISP"]) + """
<ul class="list">
<li>Every alert at level 10 or above is sent to <strong>Shuffle</strong>, which removes duplicates and opens a case in <strong>TheHive</strong>.</li>
<li>The IP addresses, hashes and domains in the alert are added to the case as observables, with TLP and PAP levels.</li>
<li><strong>Cortex</strong> and <strong>MISP</strong> enrich those observables with what is already known about them, before an analyst opens the case.</li>
</ul>
<h2>What it covers</h2>
<p>The platform monitors <strong>62 endpoints and servers</strong>. It also collects logs from the Zimbra mail server, the web application firewall, Microsoft 365 and Active Directory, with Sysmon on Windows machines.</p>
<h2>Result</h2>
<p>One chain from a raw log to a qualified case. Analysts start their work with the context already attached, instead of searching for it by hand.</p>""",
      "fr": """<h2>Point de départ</h2>
<p>Quand j'ai rejoint AVEOLYS en juillet 2023, l'entreprise n'avait pas de SOC. Les journaux restaient sur chaque serveur et personne n'était alerté en cas de problème.</p>
<h2>Ce que j'ai construit</h2>
<p>J'ai déployé <strong>Wazuh</strong> comme SIEM, avec une couche d'analyse comportementale des utilisateurs, et je l'ai relié à une chaîne automatisée :</p>
""" + flow(["Wazuh", "Shuffle", "TheHive", "Cortex + MISP"]) + """
<ul class="list">
<li>Chaque alerte de niveau 10 ou plus est envoyée à <strong>Shuffle</strong>, qui supprime les doublons et ouvre un cas dans <strong>TheHive</strong>.</li>
<li>Les adresses IP, empreintes et domaines de l'alerte sont ajoutés au cas comme observables, avec les niveaux TLP et PAP.</li>
<li><strong>Cortex</strong> et <strong>MISP</strong> enrichissent ces observables avec ce que l'on sait déjà d'eux, avant qu'un analyste ouvre le cas.</li>
</ul>
<h2>Périmètre</h2>
<p>La plateforme supervise <strong>62 postes et serveurs</strong>. Elle collecte aussi les journaux du serveur de messagerie Zimbra, du pare-feu applicatif (WAF), de Microsoft 365 et d'Active Directory, avec Sysmon sur les machines Windows.</p>
<h2>Résultat</h2>
<p>Une seule chaîne, du journal brut au cas qualifié. Les analystes commencent leur travail avec le contexte déjà rattaché, au lieu de le chercher à la main.</p>""",
    },
  },
  {
    "slug": {"en": "detection-engineering", "fr": "ingenierie-de-detection"},
    "title": {"en": "Detection engineering and alert noise reduction", "fr": "Ingénierie de détection et réduction du bruit"},
    "summary": {"en": "More than 60 custom Wazuh rules for mail, WAF, Microsoft 365 and Active Directory, and the tuning that removed thousands of useless alerts a day.",
                "fr": "Plus de 60 règles Wazuh sur mesure pour la messagerie, le WAF, Microsoft 365 et Active Directory, et le réglage qui a supprimé des milliers d'alertes inutiles par jour."},
    "meta": {"en": "AVEOLYS · 2023 – present", "fr": "AVEOLYS · 2023 – aujourd'hui"},
    "role": {"en": "Rule design, testing and tuning", "fr": "Conception, test et réglage des règles"},
    "org": {"en": "AVEOLYS, Antananarivo", "fr": "AVEOLYS, Antananarivo"},
    "period": {"en": "2023 – present", "fr": "2023 – aujourd'hui"},
    "tools": ["Wazuh rules and decoders", "MITRE ATT&amp;CK", "Sysmon", "Microsoft 365"],
    "body": {
      "en": """<h2>The problem</h2>
<p>Out of the box, a SIEM either misses what matters or floods the team. I wrote custom rules for the systems we actually run, and tuned the ones that produced noise.</p>
<h2>What the rules cover</h2>
<div class="table-scroll"><table class="data">
<thead><tr><th scope="col">Area</th><th scope="col">Examples of what is detected</th></tr></thead>
<tbody>
<tr><td>Zimbra mail</td><td>Brute force on one account or from one IP, credential stuffing across many accounts, blocking attackers who target key mailboxes</td></tr>
<tr><td>Web application firewall</td><td>Blocked attacks, repeated attacks from the same source, reconnaissance</td></tr>
<tr><td>Microsoft 365</td><td>New inbox and forwarding rules, mailbox permission changes, mass sending, eDiscovery searches and exports</td></tr>
<tr><td>Active Directory</td><td>Password spraying, Kerberoasting, Golden Ticket, additions to admin groups, RDP sweeps, cleared security logs</td></tr>
</tbody></table></div>
<p>Every rule carries its <strong>MITRE ATT&amp;CK</strong> technique. That mapping flows into TheHive, so each case shows which attack technique it is about.</p>
<h2>Cutting the noise</h2>
<p>Windows event 4719 (audit policy changed) fired constantly, almost always from machine accounts. I split it into two rules: from a machine account it drops to level 4 and stays in the logs; from a person it rises to level 12 and reaches the team. That single change removed <strong>thousands of alerts a day</strong>.</p>
<p>I use the same approach for other frequent alerts: keep the log, lower the level, and only page the team when a person or an unusual source is involved.</p>""",
      "fr": """<h2>Le problème</h2>
<p>Un SIEM installé tel quel rate ce qui compte ou noie l'équipe sous les alertes. J'ai écrit des règles sur mesure pour les systèmes que nous exploitons vraiment, et réglé celles qui produisaient du bruit.</p>
<h2>Ce que couvrent les règles</h2>
<div class="table-scroll"><table class="data">
<thead><tr><th scope="col">Domaine</th><th scope="col">Exemples de détections</th></tr></thead>
<tbody>
<tr><td>Messagerie Zimbra</td><td>Force brute sur un compte ou depuis une IP, credential stuffing sur de nombreux comptes, blocage des attaquants qui visent les boîtes sensibles</td></tr>
<tr><td>Pare-feu applicatif (WAF)</td><td>Attaques bloquées, attaques répétées depuis la même source, reconnaissance</td></tr>
<tr><td>Microsoft 365</td><td>Nouvelles règles de boîte et de transfert, changements de permissions, envois massifs, recherches et exports eDiscovery</td></tr>
<tr><td>Active Directory</td><td>Password spraying, Kerberoasting, Golden Ticket, ajouts aux groupes d'administration, balayages RDP, journaux de sécurité effacés</td></tr>
</tbody></table></div>
<p>Chaque règle porte sa technique <strong>MITRE ATT&amp;CK</strong>. Cette information remonte dans TheHive : chaque cas indique la technique d'attaque concernée.</p>
<h2>Réduire le bruit</h2>
<p>L'événement Windows 4719 (modification de la politique d'audit) se déclenchait sans arrêt, presque toujours depuis des comptes machines. Je l'ai séparé en deux règles : depuis un compte machine, il descend au niveau 4 et reste dans les journaux ; depuis une personne, il monte au niveau 12 et alerte l'équipe. Ce seul changement a supprimé <strong>des milliers d'alertes par jour</strong>.</p>
<p>J'applique la même méthode aux autres alertes fréquentes : garder le journal, baisser le niveau, et n'alerter l'équipe que lorsqu'une personne ou une source inhabituelle est en cause.</p>""",
    },
  },
  {
    "slug": {"en": "penetration-tests", "fr": "tests-d-intrusion"},
    "title": {"en": "Penetration tests and security audits", "fr": "Tests d'intrusion et audits de sécurité"},
    "summary": {"en": "Security testing for companies in Antananarivo and Toamasina: Odity, Galana GDP and Galana GRT.",
                "fr": "Tests de sécurité pour des entreprises d'Antananarivo et de Toamasina : Odity, Galana GDP et Galana GRT."},
    "meta": {"en": "AVEOLYS clients", "fr": "Clients d'AVEOLYS"},
    "role": {"en": "Penetration tester and auditor", "fr": "Pentesteur et auditeur"},
    "org": {"en": "Antananarivo and Toamasina", "fr": "Antananarivo et Toamasina"},
    "period": {"en": "Since 2023", "fr": "Depuis 2023"},
    "tools": ["BloodHound", "Impacket", "Mimikatz", "OpenVAS", "PingCastle"],
    "body": {
      "en": """<h2>Clients</h2>
<ul class="list">
<li><strong>Odity</strong>, Antananarivo</li>
<li><strong>Galana GDP</strong>, Antananarivo</li>
<li><strong>Galana GDP</strong>, Toamasina</li>
<li><strong>Galana GRT</strong>, Toamasina</li>
</ul>
<h2>How I work</h2>
""" + flow(["Scope", "Discovery", "Testing", "Report", "Follow-up"]) + """
<ul class="list">
<li><strong>Scope:</strong> agree with the client on what is tested, when, and what is off limits.</li>
<li><strong>Discovery:</strong> map the exposed services and scan for known vulnerabilities with OpenVAS.</li>
<li><strong>Testing:</strong> test the internal network and Active Directory the way an attacker would, including Kerberoasting and Pass-the-Hash, with BloodHound, Impacket and Mimikatz.</li>
<li><strong>Report:</strong> each finding is explained with its risk and a fix, ordered by priority.</li>
<li><strong>Follow-up:</strong> help the client's team apply the fixes, then check them.</li>
</ul>
<p class="note">Findings belong to each client and are never published here.</p>""",
      "fr": """<h2>Clients</h2>
<ul class="list">
<li><strong>Odity</strong>, Antananarivo</li>
<li><strong>Galana GDP</strong>, Antananarivo</li>
<li><strong>Galana GDP</strong>, Toamasina</li>
<li><strong>Galana GRT</strong>, Toamasina</li>
</ul>
<h2>Ma méthode</h2>
""" + flow(["Périmètre", "Découverte", "Tests", "Rapport", "Suivi"]) + """
<ul class="list">
<li><strong>Périmètre :</strong> définir avec le client ce qui est testé, quand, et ce qui est exclu.</li>
<li><strong>Découverte :</strong> cartographier les services exposés et rechercher les vulnérabilités connues avec OpenVAS.</li>
<li><strong>Tests :</strong> tester le réseau interne et Active Directory comme le ferait un attaquant, y compris Kerberoasting et Pass-the-Hash, avec BloodHound, Impacket et Mimikatz.</li>
<li><strong>Rapport :</strong> chaque constat est expliqué avec son risque et une correction, par ordre de priorité.</li>
<li><strong>Suivi :</strong> aider l'équipe du client à appliquer les corrections, puis les vérifier.</li>
</ul>
<p class="note">Les constats appartiennent à chaque client et ne sont jamais publiés ici.</p>""",
    },
  },
  {
    "slug": {"en": "active-directory-audits", "fr": "audits-active-directory"},
    "title": {"en": "Active Directory audits and hardening", "fr": "Audits et durcissement Active Directory"},
    "summary": {"en": "A repeatable audit cycle based on the ANSSI method: collect, score, fix, re-scan, including for a healthcare group.",
                "fr": "Un cycle d'audit reproductible selon la méthode de l'ANSSI : collecter, évaluer, corriger, réévaluer, notamment pour un groupe de santé."},
    "meta": {"en": "AVEOLYS clients", "fr": "Clients d'AVEOLYS"},
    "role": {"en": "Auditor and hardening lead", "fr": "Auditeur et responsable du durcissement"},
    "org": {"en": "AVEOLYS clients, including a healthcare group", "fr": "Clients d'AVEOLYS, dont un groupe de santé"},
    "period": {"en": "Since 2023", "fr": "Depuis 2023"},
    "tools": ["ORADAD", "PingCastle", "BloodHound"],
    "body": {
      "en": """<h2>Why Active Directory</h2>
<p>In most companies, whoever controls Active Directory controls everything. Attackers know it, so the domain is the first thing I audit.</p>
<h2>The cycle</h2>
""" + flow(["Collect", "Score", "Fix", "Re-scan"]) + """
<ul class="list">
<li><strong>Collect:</strong> run ORADAD, the collection tool from the ANSSI (France's national cybersecurity agency), on the domain.</li>
<li><strong>Score:</strong> read the ANSSI report, then use PingCastle and BloodHound to see the attack paths to admin accounts.</li>
<li><strong>Fix:</strong> write a remediation sheet for each finding, covering privileged accounts, Kerberos settings, services on domain controllers and legacy systems, and plan it with the client's IT team.</li>
<li><strong>Re-scan:</strong> run the audit again and track every finding until it is closed.</li>
</ul>
<h2>Healthcare</h2>
<p>For a healthcare group, the work followed France's CaRE program for hospitals: Active Directory audit, hardening and a review of what is exposed to the Internet.</p>
<p class="note">Clients and findings stay confidential.</p>""",
      "fr": """<h2>Pourquoi Active Directory</h2>
<p>Dans la plupart des entreprises, qui contrôle Active Directory contrôle tout. Les attaquants le savent : le domaine est donc la première chose que j'audite.</p>
<h2>Le cycle</h2>
""" + flow(["Collecter", "Évaluer", "Corriger", "Réévaluer"]) + """
<ul class="list">
<li><strong>Collecter :</strong> lancer ORADAD, l'outil de collecte de l'ANSSI, sur le domaine.</li>
<li><strong>Évaluer :</strong> lire le rapport de l'ANSSI, puis utiliser PingCastle et BloodHound pour voir les chemins d'attaque vers les comptes d'administration.</li>
<li><strong>Corriger :</strong> rédiger une fiche de correction pour chaque constat (comptes à privilèges, paramètres Kerberos, services sur les contrôleurs de domaine, systèmes obsolètes) et la planifier avec l'équipe IT du client.</li>
<li><strong>Réévaluer :</strong> relancer l'audit et suivre chaque constat jusqu'à sa fermeture.</li>
</ul>
<h2>Santé</h2>
<p>Pour un groupe de santé, le travail a suivi le programme CaRE pour les établissements de santé en France : audit Active Directory, durcissement et revue de l'exposition sur Internet.</p>
<p class="note">Les clients et les constats restent confidentiels.</p>""",
    },
  },
  {
    "slug": {"en": "incident-response-playbooks", "fr": "playbooks-reponse-incident"},
    "title": {"en": "Incident response playbooks and runbooks", "fr": "Playbooks et runbooks de réponse à incident"},
    "summary": {"en": "Twelve playbooks in the NIST SP 800-61 format, tied to the detection rules and improved after every incident.",
                "fr": "Douze playbooks au format NIST SP 800-61, reliés aux règles de détection et améliorés après chaque incident."},
    "meta": {"en": "AVEOLYS · 2023 – present", "fr": "AVEOLYS · 2023 – aujourd'hui"},
    "role": {"en": "Author and owner", "fr": "Rédacteur et responsable"},
    "org": {"en": "AVEOLYS, Antananarivo", "fr": "AVEOLYS, Antananarivo"},
    "period": {"en": "2023 – present", "fr": "2023 – aujourd'hui"},
    "tools": ["NIST SP 800-61r3", "NIST CSF 2.0", "MITRE ATT&amp;CK", "TheHive"],
    "body": {
      "en": """<h2>Why playbooks</h2>
<p>At 3 a.m., nobody should have to improvise. A playbook tells the analyst on duty what to check, what to contain and who to call, for one specific type of incident.</p>
<h2>What each playbook contains</h2>
<p>I follow the NIST SP 800-61r3 and CSF 2.0 structure: the detection rules involved, indicators of compromise, detection, triage, containment, eradication, recovery, post-incident review, escalation, and the time to detect and to respond (MTTD and MTTR).</p>
<h2>The twelve scenarios</h2>
<div class="table-scroll"><table class="data">
<thead><tr><th scope="col">Scenario</th><th scope="col">Priority</th></tr></thead>
<tbody>
<tr><td>Mail brute force and credential stuffing</td><td>P2</td></tr>
<tr><td>Attacks on key mailboxes</td><td>P2</td></tr>
<tr><td>Web attacks (SQL injection, XSS, remote code execution)</td><td>P2</td></tr>
<tr><td>Kerberoasting and Golden Ticket</td><td>P1</td></tr>
<tr><td>Privilege escalation in Active Directory</td><td>P1</td></tr>
<tr><td>Lateral movement over RDP and Pass-the-Hash</td><td>P2</td></tr>
<tr><td>Log deletion and anti-forensics</td><td>P1</td></tr>
<tr><td>Microsoft 365 mailbox compromise and business email compromise</td><td>P2</td></tr>
<tr><td>Data exfiltration through eDiscovery or DLP violations</td><td>P1</td></tr>
<tr><td>Active Directory brute force</td><td>P2</td></tr>
<tr><td>Loss of visibility on a domain controller</td><td>P2</td></tr>
<tr><td>File integrity changes and malware</td><td>P2</td></tr>
</tbody></table></div>
<h2>Runbooks</h2>
<p>Alongside the playbooks, I write runbooks for the routine work: the exact steps to run a task the same way every time, whoever is on duty.</p>
<h2>Continuous improvement</h2>
<p>After every real incident, the post-incident review asks what slowed us down. The answer goes back into the playbook, and often into a new or better detection rule. Tabletop exercises with the team test the playbooks before a real incident does.</p>""",
      "fr": """<h2>Pourquoi des playbooks</h2>
<p>À 3 heures du matin, personne ne devrait improviser. Un playbook indique à l'analyste d'astreinte quoi vérifier, quoi confiner et qui appeler, pour un type d'incident précis.</p>
<h2>Contenu de chaque playbook</h2>
<p>Je suis la structure NIST SP 800-61r3 et CSF 2.0 : règles de détection concernées, indicateurs de compromission, détection, triage, confinement, éradication, reprise, retour d'expérience, escalade, et délais de détection et de réponse (MTTD et MTTR).</p>
<h2>Les douze scénarios</h2>
<div class="table-scroll"><table class="data">
<thead><tr><th scope="col">Scénario</th><th scope="col">Priorité</th></tr></thead>
<tbody>
<tr><td>Force brute et credential stuffing sur la messagerie</td><td>P2</td></tr>
<tr><td>Attaques sur les boîtes mail sensibles</td><td>P2</td></tr>
<tr><td>Attaques web (injection SQL, XSS, exécution de code à distance)</td><td>P2</td></tr>
<tr><td>Kerberoasting et Golden Ticket</td><td>P1</td></tr>
<tr><td>Élévation de privilèges dans Active Directory</td><td>P1</td></tr>
<tr><td>Mouvement latéral par RDP et Pass-the-Hash</td><td>P2</td></tr>
<tr><td>Effacement de journaux et anti-forensique</td><td>P1</td></tr>
<tr><td>Compromission de boîte Microsoft 365 et fraude au président (BEC)</td><td>P2</td></tr>
<tr><td>Exfiltration par eDiscovery ou violation DLP</td><td>P1</td></tr>
<tr><td>Force brute Active Directory</td><td>P2</td></tr>
<tr><td>Perte de visibilité sur un contrôleur de domaine</td><td>P2</td></tr>
<tr><td>Modification de fichiers sensibles et malware</td><td>P2</td></tr>
</tbody></table></div>
<h2>Runbooks</h2>
<p>En complément des playbooks, je rédige des runbooks pour le travail courant : les étapes exactes pour faire une tâche de la même façon à chaque fois, quelle que soit la personne d'astreinte.</p>
<h2>Amélioration continue</h2>
<p>Après chaque incident réel, le retour d'expérience cherche ce qui nous a ralentis. La réponse revient dans le playbook, et souvent dans une règle de détection nouvelle ou améliorée. Des exercices sur table avec l'équipe testent les playbooks avant qu'un vrai incident ne le fasse.</p>""",
    },
  },
  {
    "slug": {"en": "single-sign-on-mfa", "fr": "authentification-unique-mfa"},
    "title": {"en": "Single sign-on with MFA", "fr": "Authentification unique avec MFA"},
    "summary": {"en": "One Keycloak login with one-time-password MFA, backed by Active Directory, for the security tools and business applications.",
                "fr": "Un seul identifiant Keycloak avec MFA par mot de passe à usage unique, adossé à Active Directory, pour les outils de sécurité et les applications métier."},
    "meta": {"en": "AVEOLYS", "fr": "AVEOLYS"},
    "role": {"en": "Design and deployment", "fr": "Conception et déploiement"},
    "org": {"en": "AVEOLYS, Antananarivo", "fr": "AVEOLYS, Antananarivo"},
    "period": {"en": "Since 2023", "fr": "Depuis 2023"},
    "tools": ["Keycloak", "Active Directory", "Kerberos", "OIDC", "SAML"],
    "body": {
      "en": """<h2>The goal</h2>
<p>Each application had its own accounts and passwords. More accounts mean more passwords to steal, and leavers whose access is forgotten somewhere.</p>
<h2>What I deployed</h2>
""" + flow(["Active Directory", "Keycloak + MFA", "Applications"]) + """
<ul class="list">
<li><strong>Keycloak</strong> as the identity provider, connected to Active Directory and Kerberos, so staff use their usual company account.</li>
<li><strong>One-time-password MFA</strong> on top of the password.</li>
<li>Applications connected over <strong>OIDC</strong> or <strong>SAML</strong>, including Wazuh, Shuffle, Zimbra, Microsoft 365, Bitdefender GravityZone, KaseyaOne, the internal wiki and the internal ERP.</li>
</ul>
<h2>Result</h2>
<p>Staff have one account to protect, and removing someone's access happens in one place.</p>""",
      "fr": """<h2>L'objectif</h2>
<p>Chaque application avait ses propres comptes et mots de passe. Plus de comptes, c'est plus de mots de passe à voler, et des accès oubliés quelque part quand quelqu'un part.</p>
<h2>Ce que j'ai déployé</h2>
""" + flow(["Active Directory", "Keycloak + MFA", "Applications"]) + """
<ul class="list">
<li><strong>Keycloak</strong> comme fournisseur d'identité, relié à Active Directory et Kerberos : chacun utilise son compte habituel de l'entreprise.</li>
<li><strong>MFA par mot de passe à usage unique</strong> en plus du mot de passe.</li>
<li>Applications raccordées en <strong>OIDC</strong> ou <strong>SAML</strong>, dont Wazuh, Shuffle, Zimbra, Microsoft 365, Bitdefender GravityZone, KaseyaOne, le wiki interne et l'ERP interne.</li>
</ul>
<h2>Résultat</h2>
<p>Chacun n'a plus qu'un compte à protéger, et la suppression d'un accès se fait à un seul endroit.</p>""",
    },
  },
]

PAGES = {
  "home": {
    "en": {"title": f"{NAME} | Cybersecurity Specialist", "desc": "Cybersecurity specialist in Madagascar: SOC build and operation, incident response, penetration tests and Active Directory audits. Open to remote work."},
    "fr": {"title": f"{NAME} | Spécialiste en cybersécurité", "desc": "Spécialiste en cybersécurité à Madagascar : création et exploitation de SOC, réponse à incident, tests d'intrusion et audits Active Directory. Ouvert au travail à distance."},
  },
  "projects": {
    "en": {"title": f"Projects | {NAME}", "desc": "Case studies: building a SOC, detection engineering, penetration tests, Active Directory audits, incident response playbooks and single sign-on.", "h1": "Projects", "lead": "Six pieces of work, each with what I did and the tools I used. Client findings are never published."},
    "fr": {"title": f"Projets | {NAME}", "desc": "Études de cas : création d'un SOC, ingénierie de détection, tests d'intrusion, audits Active Directory, playbooks de réponse à incident et authentification unique.", "h1": "Projets", "lead": "Six réalisations, chacune avec ce que j'ai fait et les outils utilisés. Les constats des clients ne sont jamais publiés."},
  },
  "about": {
    "en": {"title": f"About | {NAME}", "desc": "Experience at AVEOLYS, Huawei Technologies Madagascar and MICTSL, skills, certifications and education of Stephanio RAZARISON.", "h1": "About me",
           "lead": "I started in networks, moved into security, and now build and run security operations. Five years on the defensive side, with offensive testing for clients."},
    "fr": {"title": f"À propos | {NAME}", "desc": "Expérience chez AVEOLYS, Huawei Technologies Madagascar et MICTSL, compétences, certifications et formation de Stephanio RAZARISON.", "h1": "À propos",
           "lead": "J'ai commencé dans les réseaux, je suis passé à la sécurité, et aujourd'hui je construis et j'exploite des opérations de sécurité. Cinq ans côté défense, avec des tests offensifs pour des clients."},
  },
  "contact": {
    "en": {"title": f"Contact | {NAME}", "desc": "Contact Stephanio RAZARISON for remote cybersecurity work: SOC, incident response, penetration tests and Active Directory audits.", "h1": "Contact",
           "lead": "For a project, a contract or a full-time role, email is the quickest way to reach me. I'm in UTC+3, which overlaps most of the European working day."},
    "fr": {"title": f"Contact | {NAME}", "desc": "Contacter Stephanio RAZARISON pour une mission de cybersécurité à distance : SOC, réponse à incident, tests d'intrusion et audits Active Directory.", "h1": "Contact",
           "lead": "Pour un projet, une mission ou un poste, l'e-mail est le moyen le plus rapide de me joindre. Je suis en UTC+3, ce qui couvre la plupart des heures de bureau en Europe."},
  },
  "privacy": {
    "en": {"title": f"Privacy policy | {NAME}", "desc": "How this website handles personal data: hosting logs, contact messages, analytics and stored preferences.", "h1": "Privacy policy"},
    "fr": {"title": f"Politique de confidentialité | {NAME}", "desc": "Comment ce site traite les données personnelles : journaux d'hébergement, messages de contact, statistiques et préférences enregistrées.", "h1": "Politique de confidentialité"},
  },
  "legal": {
    "en": {"title": f"Legal notice | {NAME}", "desc": "Publisher and host of this website.", "h1": "Legal notice"},
    "fr": {"title": f"Mentions légales | {NAME}", "desc": "Éditeur et hébergeur de ce site.", "h1": "Mentions légales"},
  },
}
