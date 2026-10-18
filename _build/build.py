#!/usr/bin/env python3
"""Builds the TW Results static site (v2, 18/10/2026) into the repo root.
Run:  python3 _build/build.py            (preview build: noindex + Disallow-all robots)
      python3 _build/build.py --live     (launch build: indexable, robots allows all, 404 base = /)
"""
import json, os, sys, html, re

LIVE = "--live" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://twresults.com"
LASTMOD = "2026-10-18"
PREVIEW_BASE = "/twresults-preview/"
V = "5"  # asset cache-buster

# PHONE FLAG: leave PHONE_DISPLAY = None until the giffgaff number is live. [TWR PHONE: giffgaff number to come]
# Set both, e.g. PHONE_DISPLAY = "07xxx xxxxxx" and PHONE_E164 = "+447xxxxxxxxx" (NEVER 07944 915880),
# and every Call Dan button, the footer number, the contact number and schema "telephone" appear automatically.
PHONE_DISPLAY = None
PHONE_E164 = None
HAS_PHONE = bool(PHONE_DISPLAY and PHONE_E164)
PHONE = PHONE_DISPLAY or ""
TEL = "tel:" + (PHONE_E164 or "")
EMAIL = "dan@twresults.com"
ADDRESS = '<span class="ph">[ADDRESS: Derby, by appointment]</span>'
FORM_ENDPOINT = "[FORM ENDPOINT]"   # Formspree, e.g. https://formspree.io/f/xxxxxxx
TAGLINE = "Get found on Google. Get more work."
# Source checked 18/10/2026: Backlinko organic CTR study (published 27/08/2019, updated 16/04/2025):
# "we found that the top 3 Google search results get 54.4% of all clicks" and "only .63% of Google searchers clicked on something from the second page".
# It measures ORGANIC search results (Search Console data), not the Google Maps pack.
BACKLINKO_URL = "https://backlinko.com/google-ctr-stats"
CALLBACK = "I'll call you back within one working day."
# DRAFT town list: must match the Google profile service area before launch
TOWNS = ["Derby", "Chellaston", "Alvaston", "Mickleover", "Littleover", "Allestree", "Spondon", "Belper", "Ripley", "Long Eaton", "Ashby"]
REACH = "Derby, the East Midlands and UK-wide (remote)"
REACH_LINE = "Based in Derby. Working across the East Midlands, and with businesses UK-wide remotely."
WIDE_AREAS = [{"@type": "AdministrativeArea", "name": "East Midlands"}, {"@type": "Country", "name": "United Kingdom"}]
TOWNS_DRAFT = '<span class="ph">[DRAFT: town list to confirm with Dan]</span>'

NAV = [("what-we-do/", "What we do"), ("results/", "Results"), ("about-dan/", "About Dan"), ("contact/", "Contact")]
WM = '<span class="tw">TW</span> <span class="rs">| Results</span>'

def esc(s): return html.escape(s, quote=False)
def ph_text(s):
    """Escape text and wrap any [PLACEHOLDER] in a visible marker."""
    return re.sub(r"(\[[A-Z][^\]]*\])", r'<span class="ph">\1</span>', esc(s))

# ---------------- schema ----------------
def org_schema():
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": SITE + "/#business",
        "name": "TW Results",
        "url": SITE + "/",
        "email": EMAIL,
        "logo": SITE + "/assets/apple-touch-icon.png",
        "image": SITE + "/assets/og-image.png",
        "description": "Local SEO, Google Business Profile work and websites for trades and local businesses in Derby, the East Midlands and UK-wide (remote).",
        "founder": {"@type": "Person", "@id": SITE + "/about-dan/#dan", "name": "Dan Cooper"},
        "areaServed": [{"@type": "City", "name": t} for t in TOWNS] + WIDE_AREAS,
        "knowsAbout": ["Local SEO", "Google Business Profile optimisation", "Google Maps rankings", "Websites for tradespeople"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "serviceType": t, "areaServed": [{"@type": "City", "name": t} for t in TOWNS] + WIDE_AREAS}}
            for n, t in [("Google Maps and local SEO", "Local SEO and Google Business Profile optimisation"),
                         ("Website fixes", "Website improvements for trades"),
                         ("New websites for trades", "Web design for tradespeople")]]},
    } | ({"telephone": PHONE_E164} if HAS_PHONE else {})

def crumbs_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": SITE + "/" + u} for i, (u, n) in enumerate(items, 1)]}

def crumbs_html(items, depth):
    p = "../" * depth
    lis = "".join(f'<li><a href="{p}{u}">{n}</a></li>' for u, n in items[:-1]) + f'<li aria-current="page">{items[-1][1]}</li>'
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

FAQ = [
    ("Can you guarantee I'll be number one?", "No. Nobody honest can. I do the work Google rewards and show you where you stand every month."),
    ("How long does it take?", "It depends on your trade, your town and who you're up against. You'll see your position in a report every month."),
    ("Do I get tied into a contract?", "A minimum of 3 monthly payments, then month to month with 30 days' notice. [DRAFT: terms not final]"),
    ("I already have a website. Can you work with it?", "Yes, in most cases, whoever built it."),
    ("I only have a Facebook page.", "Then you need a simple website. I build those, set up in your name."),
    ("Who do I actually talk to?", "Me, Dan. Every time."),
]
def faq_html():
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{ph_text(a)}</p></details>" for q, a in FAQ) + "</div>"
def faq_schema():
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

# ---------------- shared pieces ----------------
def page(slug, title, desc, body, schema=None, depth=1, current=None):
    assert len(title) < 60, (title, len(title))
    assert len(desc) < 155, (desc, len(desc))
    p = "../" * depth
    canon = SITE + "/" + slug
    base = ""
    if slug == "404.html":
        base = '<base href="%s">' % ("/" if LIVE else PREVIEW_BASE)
        p = ""
    robots = "" if LIVE else '<meta name="robots" content="noindex, nofollow">\n'
    navli = "".join('<li><a href="%s%s"%s>%s</a></li>' % (p, u, ' aria-current="page"' if u == current else "", t) for u, t in NAV)
    sch = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(s, ensure_ascii=False, separators=(",", ":")) for s in (schema or []))
    form_href = "#enquiry" if (slug in ("", "contact/") or slug.startswith("areas/")) else p + "contact/#enquiry"
    head_btn = f'<a class="btn" href="{TEL}">Call Dan</a>' if HAS_PHONE else f'<a class="btn" href="{form_href}">Free Google check</a>'
    bar_btn = f'<a class="btn" href="{TEL}">Call Dan</a>' if HAS_PHONE else f'<a class="btn" href="{form_href}">Get a free Google check</a>'
    foot_phone = f'<p>Call: <a href="{TEL}">{PHONE}</a></p>' if HAS_PHONE else ""
    foot_links = "".join('<li><a href="%s%s">%s</a></li>' % (p, u, t) for u, t in [("", "Home")] + NAV + [("privacy/", "Privacy")])
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{esc(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#121F45">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TW Results">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="TW | Results. Get found on Google. Get more work.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{p}favicon.ico" sizes="32x32">
<link rel="icon" href="{p}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/apple-touch-icon.png">
<link rel="preload" href="{p}assets/fonts/arimo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/site.css?v={V}">
{sch}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
 <div class="wrap">
  <a class="wm" href="{p or './'}" aria-label="TW Results home">{WM}</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <nav class="nav" id="nav" aria-label="Main"><ul>{navli}</ul></nav>
  {head_btn}
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot on-navy">
 <div class="wrap">
  <div class="foot-grid">
   <div>
    <a class="wm" href="{p or './'}" aria-label="TW Results home">{WM}</a>
    <p class="foot-tag">{TAGLINE}</p>
   </div>
   <div>
    <h2>Pages</h2>
    <ul>{foot_links}</ul>
   </div>
   <div>
    <h2>Get hold of Dan</h2>
    {foot_phone}
    <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p>Local SEO and websites for trades and local businesses. {REACH_LINE}</p>
   </div>
  </div>
  <div class="legal"><p>&copy; 2026 TW Results. Daniel Cooper trading as TW Results.</p></div>
 </div>
</footer>
<div class="callbar on-navy">{bar_btn}</div>
<div class="cookie" id="cookie" hidden role="region" aria-label="Cookies">
 <div class="wrap"><p>Can we use analytics cookies to see how the site is used? <a href="{p}privacy/">Privacy</a></p>
 <div class="cta" style="margin:0"><button class="btn" type="button" data-consent="yes">Accept</button><button class="btn btn-s" type="button" data-consent="no">Reject</button></div></div>
</div>
<script src="{p}assets/site.js?v={V}" defer></script>
</body>
</html>
"""

def form(depth, heading_tag="h2", heading="Free Google check"):
    p = "../" * depth
    return f"""<div class="formcard"><span class="c3"></span><span class="c4"></span>
 <{heading_tag} class="form-h">{heading}</{heading_tag}>
 <p class="promise">Send this and I&rsquo;ll run a free Google check on your business and call you back within one working day.</p>
 <form id="enquiry" action="{FORM_ENDPOINT}" method="POST" novalidate>
  <p class="hp" aria-hidden="true"><label for="gotcha">Leave this empty</label><input id="gotcha" name="_gotcha" tabindex="-1" autocomplete="off"></p>
  <input type="hidden" name="_subject" value="Free Google check request from twresults.com">
  <div class="f-row">
  <div class="f"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required></div>
  <div class="f"><label for="business">Trade or business</label><input id="business" name="business" autocomplete="organization" required placeholder="e.g. Barber shop"></div>
  </div>
  <div class="f"><label for="contact">Phone or email</label><input id="contact" name="contact" autocomplete="tel" required></div>
  <div class="f"><label for="message">Message <span class="opt">(optional)</span></label><textarea id="message" name="message" rows="3"></textarea></div>
  <button class="btn" type="submit">Send to Dan</button>
  <p class="consent">I only use your details to reply. <a href="{p}privacy/">Privacy notice</a>.</p>
  <p class="form-msg" id="form-msg" role="status" tabindex="-1"></p>
 </form>
</div>"""

def serp(hero=False):
    rows = "".join(f'<li><span class="n">{n}</span><span><span class="nm">Competitor</span><span class="bar"></span><span class="bar s"></span></span></li>' for n in ("1", "2", "3"))
    return f"""<figure class="{'serp-hero' if hero else ''}" style="margin:0">
 <p class="serp-h">Three names. One phone call.</p>
 <div class="serp" role="img" aria-label="A mock page of Google search results for a local service near me in Derby. Three competitors fill the top three places. Your business is on page 2.">
  <div class="serp-q"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="7.5" cy="7.5" r="5.5" fill="none" stroke="#121F45" stroke-width="2"/><path d="M11.6 11.6 L16 16" stroke="#121F45" stroke-width="2"/></svg><span><span id="trade">barber</span> near me, Derby</span></div>
  <ol>{rows}</ol>
  <span class="gap">4 to 10: other businesses</span>
  <p class="page2">Page 2</p>
  <div class="you"><span class="n">14</span><span><span class="nm">You</span><span class="bar s"></span></span></div>
 </div>
 <figcaption class="serp-note">Illustration of Google&rsquo;s organic search results.</figcaption>
</figure>"""

def shot(date):
    return (f'<figure style="margin:0"><div class="photo wide"><b>[CASE STUDY SCREENSHOT {date}]</b>'
            f'<span>Google Maps results for &lsquo;embroidery Derby&rsquo;, private browser, dated</span></div>'
            f'<figcaption class="cap">&lsquo;embroidery Derby&rsquo;, Google Maps, checked {date}.</figcaption></figure>')

def headshot(note="Dan outdoors in Derby, daylight, shoulders up. 4:5, 1200 x 1500px WebP"):
    return f'<figure class="photo"><b>[HEADSHOT]</b><span>{note}</span></figure>'

SERVICES = [
    ("google-maps", "Google Maps and local SEO", "Your Google Business Profile set up properly, weekly posts, more reviews and matching directory listings."),
    ("website-fixes", "Website fixes", "Clear wording, a fast site and a call button on every page, whoever built it."),
    ("new-websites", "New websites", "A simple, fast site in your name, if you haven't got one."),
]
STEPS = [
    ("Free Google check", "I check where you show up and who&rsquo;s ahead of you. You get a straight answer."),
    ("I fix it", "Your Google profile, website and directory details, sorted."),
    ("Monthly report", "One page: what I did and where you rank."),
]

# ---------------- Home ----------------
# ---------------- Town / city pages (template) ----------------
# To publish a town page, add an entry to AREA_PAGES (see README). Nothing is published while it's empty.
# Each entry needs its own unique intro and local detail; never copy one town's text to another.
AREA_PAGES = [
    # {"name": "Chellaston", "slug": "chellaston",
    #  "desc": "Local SEO, Google Maps and websites for trades and local businesses in Chellaston, Derby. Free Google check from Dan.",
    #  "intro": "One or two sentences that are true about working with businesses in Chellaston.",
    #  "local": ["A real, specific local point", "Another one"]},
]
def area_url(a): return f"areas/{a['slug']}/"
AREA_LINKS = {a["name"]: area_url(a) for a in AREA_PAGES}
towns_li = "".join(f'<li><a href="{AREA_LINKS[t]}">{t}</a></li>' if t in AREA_LINKS else f"<li>{t}</li>" for t in TOWNS)
CITE = f'<a href="{BACKLINKO_URL}" rel="noopener">Backlinko organic click-through rate study</a>, updated 16/04/2025'
EE_WORK = "I built an optimised website, set up and optimised the Google Business Profile, and handled reviews, posts and citations."
EE_START = "Brand-new business, launched July 2026, from page 2&ndash;3 to #2 on Google Maps in a few weeks. Search: &ldquo;embroidery Derby&rdquo;."
EE_CHECKS = "Checked 10/09/2026 and 07/10/2026: #2 both times, position held."
EE_FIGS = [("80%", "of work now inbound"), ("About 10", "more enquiries a week")]
def ee_result():
    figs = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in EE_FIGS)
    return (f'<p class="big" aria-hidden="true">#2</p>'
            f'<p class="big-cap">#2 on Google Maps for &ldquo;embroidery Derby&rdquo; in a few weeks.</p>'
            f'<dl class="kpis">{figs}</dl><p class="note">Figures reported by the client.</p>')
def call_cta(extra=""):
    return f'<div class="cta"><a class="btn" href="{TEL}">Call Dan</a><a class="tel" href="{TEL}">{PHONE}</a>{extra}</div>' if HAS_PHONE else (f'<div class="cta">{extra}</div>' if extra else "")

home = f"""
<section class="hero" aria-labelledby="h1">
 <div class="wrap"><div class="hero-grid">
  <div>
   <h1 id="h1">{TAGLINE}</h1>
   <p class="kw">Local SEO, Google Maps and websites for trades and local businesses in {REACH}.</p>
   {call_cta()}
   {serp(hero=True)}
  </div>
  <div class="hero-side">
   {form(0)}
   <p class="alt">Prefer email? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>
 </div></div>
</section>

<section class="sec stat-sec" aria-labelledby="h-problem">
 <div class="wrap"><div class="split">
  <h2 id="h-problem">Page 2 gets almost nothing.</h2>
  <div>
   <p class="lede">The top 3 Google search results get 54.4% of all clicks. Only 0.63% of searchers click anything on page 2.</p>
   <p>For your trade, in your area, the top 3 is your competitors. I fix that.</p>
   <p class="small">Source: {CITE}. Organic search results, not the map.</p>
  </div>
 </div></div>
</section>

<section class="sec pale" aria-labelledby="h-services">
 <div class="wrap">
  <h2 id="h-services">Local SEO and websites for trades and local businesses</h2>
  <ul class="rows">{"".join(f'<li><h3>{h}</h3><p>{t}</p><a class="link" href="what-we-do/#{a}">More<span class="vh"> about {h.lower()}</span></a></li>' for a, h, t in SERVICES)}</ul>
 </div>
</section>

<section class="sec navy on-navy" aria-labelledby="h-results">
 <div class="wrap"><div class="split">
  <div>
   <h2 id="h-results">Results for a Derby business</h2>
   {ee_result()}
   <p class="lede">Eaton Embroidery, a Derby embroidery business, is a client.</p>
   <p>{EE_WORK}</p>
   <p class="small">{EE_START} {EE_CHECKS}</p>
   <p style="margin-top:1.5rem"><a class="link" href="results/">See the case study</a></p>
  </div>
  <div class="shots">{shot("10/09/2026")}{shot("07/10/2026")}</div>
 </div></div>
</section>

<section class="sec" aria-labelledby="h-dan">
 <div class="wrap"><div class="person">
  {headshot()}
  <div>
   <h2 id="h-dan">You deal with me, Dan</h2>
   <p class="lede">I&rsquo;m Dan Cooper. I help trades and local businesses, in Derby and further afield, that are good at what they do but hard to find on Google.</p>
   <p>No account managers, no call centre. If something won&rsquo;t help, I&rsquo;ll tell you before you spend anything.</p>
   <p><a class="link" href="about-dan/">About me</a></p>
  </div>
 </div></div>
</section>

<section class="sec pale" aria-labelledby="h-steps">
 <div class="wrap">
  <h2 id="h-steps">How it works</h2>
  <ol class="steps">{"".join(f"<li><h3>{h}</h3><p>{t}</p></li>" for h, t in STEPS)}</ol>
 </div>
</section>

<section class="sec" aria-labelledby="h-faq">
 <div class="wrap"><div class="split">
  <h2 id="h-faq">Local SEO questions</h2>
  {faq_html()}
 </div></div>
</section>

<section class="sec pale" aria-labelledby="h-areas">
 <div class="wrap"><div class="split">
  <h2 id="h-areas">Areas I cover</h2>
  <div>
   <p class="lede">{REACH_LINE}</p>
   <ul class="towns">{towns_li}</ul>
   <p class="small">Towns around Derby I cover in person. {TOWNS_DRAFT}</p>
   <div class="cta"><a class="btn" href="#enquiry">Get a free Google check</a></div>
  </div>
 </div></div>
</section>
"""

# ---------------- What we do ----------------
SVC_DETAIL = [
    ("google-maps", "Google Maps and local SEO in Derby",
     "Get into the top three on Google Maps when people near you search for what you do.",
     ["Your Google Business Profile set up properly: categories, services, area, hours, photos", "A post on your profile every week", "More reviews from real customers, and a reply to every one", "Matching details on the directories that matter", "Where you rank, checked every month"],
     "Send photos of your work and ask happy customers for a review."),
    ("website-fixes", "Website fixes that bring in calls",
     "Plenty of local business websites look fine but don&rsquo;t make the phone ring. I fix that, whoever built yours.",
     ["Clear wording: what you do and where", "A fast site that works on a phone", "Pages for your services and towns", "A call or booking button on every page"],
     "Tell me the work you want more of, and check the wording."),
    ("new-websites", "New websites for trades and local businesses",
     "No website, or just a Facebook page? I build a simple, fast site that Google can send people to.",
     ["Your services, areas and photos of your work", "A contact form straight to your email", "Built to be found on Google", "Set up in your name, so you own it"],
     "Send your logo, a few photos and a list of services."),
]
def svc(a, h, intro, gets, you):
    lis = "".join(f"<li>{g}</li>" for g in gets)
    return (f'<section class="svc" id="{a}" aria-labelledby="h-{a}"><div class="split">'
            f'<div><h2 id="h-{a}">{h}</h2><p class="lede">{intro}</p></div>'
            f'<div><h3 style="margin-bottom:1rem">What you get</h3><ul class="plain">{lis}</ul>'
            f'<p style="margin-top:1.5rem"><b>What you do:</b> {you}</p></div></div></section>')

WWD_CRUMBS = [("", "Home"), ("what-we-do/", "What we do")]
wwd = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(WWD_CRUMBS, 1)}
 <h1>Local SEO and websites for Derby businesses</h1>
 <p class="lede">Three services, in plain English. I start with a free Google check and tell you what&rsquo;s worth doing.</p>
</div></section>
<div class="wrap">{"".join(svc(*s) for s in SVC_DETAIL)}</div>
<section class="band navy on-navy"><div class="wrap"><h2>Want to know where you stand?</h2><a class="btn" href="../contact/#enquiry">Get a free Google check</a></div></section>
"""

# ---------------- Results (case study) ----------------
RES_CRUMBS = [("", "Home"), ("results/", "Results")]
results = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(RES_CRUMBS, 1)}
 <h1>Local SEO case study: an embroidery business in Derby</h1>
 <p class="lede">Eaton Embroidery is a Derby embroidery business and a TW Results client. I built its website and Google Business Profile and took it to #2 on Google Maps for &ldquo;embroidery Derby&rdquo; within a few weeks.</p>
</div></section>
<section class="sec" aria-labelledby="h-work"><div class="wrap"><div class="split">
 <h2 id="h-work">What I did</h2>
 <ul class="plain"><li>Built an optimised website</li><li>Set up and optimised the Google Business Profile</li><li>Reviews: every new review replied to</li><li>Regular Google posts</li><li>Citations: matching business details on directories such as Yell and Bing</li></ul>
</div></div></section>
<section class="sec navy on-navy" aria-labelledby="h-fact"><div class="wrap"><div class="split">
 <div><h2 id="h-fact">Results for a Derby business</h2>
  {ee_result()}
  <p class="small">{EE_START}</p></div>
 <div class="shots">{shot("10/09/2026")}{shot("07/10/2026")}</div>
</div></div></section>
<section class="sec pale" aria-labelledby="h-log"><div class="wrap"><div class="split">
 <h2 id="h-log">Results log</h2>
 <ol class="log"><li><time datetime="2026-07">July 2026</time><p>Brand-new business launched. Page 2&ndash;3 on Google Maps for &ldquo;embroidery Derby&rdquo;.</p></li><li><time datetime="2026-09-10">10/09/2026</time><p>Checked after the work: #2 on Google Maps for &ldquo;embroidery Derby&rdquo;.</p></li><li><time datetime="2026-10-07">07/10/2026</time><p>Checked again: #2, position held.</p></li></ol>
</div></div></section>
<section class="band navy on-navy"><div class="wrap"><h2>Where do you rank?</h2><a class="btn" href="../contact/#enquiry">Get a free Google check</a></div></section>
"""

# ---------------- About Dan ----------------
ABOUT_CRUMBS = [("", "Home"), ("about-dan/", "About Dan")]
about = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(ABOUT_CRUMBS, 1)}
 <div class="person">
  {headshot()}
  <div>
   <h1>Dan Cooper, local SEO in Derby</h1>
   <p class="lede">I run TW Results from Derby and work with trades and local businesses across the East Midlands and UK-wide. They&rsquo;re good at what they do but hard to find on Google.</p>
   <p>I keep it simple: find what&rsquo;s wrong, fix it, show you the result every month. No account managers, no call centre.</p>
   <p><span class="ph">[DAN TO ADD 1 TO 2 LINES OF REAL BACKGROUND]</span></p>
   {call_cta('<a class="link" href="../contact/#enquiry">Get a free Google check</a>')}
  </div>
 </div>
</div></section>
"""

# ---------------- Contact ----------------
CON_CRUMBS = [("", "Home"), ("contact/", "Contact")]
phone_big = f'<a class="phone-big" href="{TEL}">{PHONE}</a>' if HAS_PHONE else ""
contact = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(CON_CRUMBS, 1)}
 <div class="hero-grid">
  <div>
   <h1>Free Google check for Derby businesses</h1>
   <p class="lede">Send the form and I&rsquo;ll check how you show up on Google. {CALLBACK}</p>
   {phone_big}
   <dl class="facts">
    <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
    <div><dt>Meetings</dt><dd>{ADDRESS}</dd></div>
    <div><dt>Covering</dt><dd>{REACH}</dd></div>
   </dl>
  </div>
  {form(1)}
 </div>
</div></section>
"""

# ---------------- Privacy ----------------
privacy = f"""
<section class="page-hero"><div class="wrap">
 <h1>Privacy</h1>
 <p class="lede">What I collect, why, and how to get it deleted.</p>
</div></section>
<section class="sec"><div class="wrap"><div class="prose">
 <p><span class="ph">[DRAFT: Dan to approve]</span> Last updated <span class="ph">[DATE OF APPROVAL]</span>.</p>
 <h2>Who I am</h2><p>TW Results is run by Daniel Cooper, trading as TW Results, based in Derby. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
 <h2>What the form collects</h2><p>Your name, trade or business, phone number or email, and your message. I use it only to run your free Google check, reply to you and, if you become a client, to do the work. I don&rsquo;t sell it or pass it on.</p>
 <h2>Who processes it</h2><p>The form is sent through Formspree, which passes it to my email. My email runs on Google Workspace.</p>
 <h2>Analytics</h2><p>If you click Accept on the cookie bar, I use Google Analytics 4 to count visits. It doesn&rsquo;t load unless you accept.</p>
 <h2>How long I keep it</h2><p>Enquiries that don&rsquo;t turn into work are deleted after <span class="ph">[RETENTION PERIOD: Dan to confirm]</span>. Client records are kept as long as the law requires for tax and accounts.</p>
 <h2>Your rights</h2><p>You can ask to see, correct or delete your details. Email <a href="mailto:{EMAIL}">{EMAIL}</a>. You can also complain to the Information Commissioner&rsquo;s Office at <a href="https://ico.org.uk">ico.org.uk</a>.</p>
</div></div></section>
"""

notfound = f"""
<section class="page-hero"><div class="wrap">
 <h1>That page doesn&rsquo;t exist.</h1>
 <p class="lede">It may have moved, or the link was wrong.</p>
 <div class="cta"><a class="btn" href="./">Go to the home page</a><a class="link" href="contact/#enquiry">Get a free Google check</a></div>
</div></section>
"""

def area_page(a):
    """Reusable town/city page: /areas/<slug>/ with its own title, meta, H1, breadcrumb and schema."""
    name, P = a["name"], "../../"
    crumbs = [("", "Home"), (area_url(a), name)]
    title = a.get("title") or f"Local SEO in {name} | TW Results"
    assert a.get("desc") and a.get("intro"), "each town page needs its own desc and intro"
    local = "".join(f"<li>{x}</li>" for x in a.get("local", []))
    body = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(crumbs, 2)}
 <div class="hero-grid">
  <div>
   <h1>Local SEO and websites in {name}</h1>
   <p class="lede">{a["intro"]}</p>
   {f'<ul class="plain" style="margin-top:1.5rem">{local}</ul>' if local else ""}
  </div>
  {form(2)}
 </div>
</div></section>
<section class="sec pale" aria-labelledby="h-svc"><div class="wrap">
 <h2 id="h-svc">What I do for {name} businesses</h2>
 <ul class="rows">{"".join(f'<li><h3>{h}</h3><p>{t}</p><a class="link" href="{P}what-we-do/#{s_}">More<span class="vh"> about {h.lower()}</span></a></li>' for s_, h, t in SERVICES)}</ul>
</div></section>
<section class="band navy on-navy"><div class="wrap"><h2>Where do you rank in {name}?</h2><a class="btn" href="#enquiry">Get a free Google check</a></div></section>
"""
    svc_schema = {"@context": "https://schema.org", "@type": "Service", "name": f"Local SEO in {name}",
                  "serviceType": "Local SEO and Google Business Profile optimisation",
                  "provider": {"@id": SITE + "/#business"}, "areaServed": {"@type": "City", "name": name},
                  "url": SITE + "/" + area_url(a)}
    return (area_url(a), area_url(a) + "index.html", 2, title, a["desc"], body, [ORG, crumbs_schema(crumbs), svc_schema], None)

ORG = org_schema()
PAGES = [
    ("", "index.html", 0, "Local SEO for Trades & Businesses, Derby | TW Results",
     "Local SEO, Google Maps and websites for trades and local businesses in Derby, the East Midlands and UK-wide. Free Google check.",
     home, [ORG, faq_schema()], None),
    ("what-we-do/", "what-we-do/index.html", 1, "Local SEO & Websites, Derby | TW Results",
     "Google Business Profile and local SEO, website fixes and new websites for trades and local businesses in Derby, the East Midlands and UK-wide.",
     wwd, [ORG, crumbs_schema(WWD_CRUMBS)], "what-we-do/"),
    ("results/", "results/index.html", 1, "Local SEO Case Study, Derby | TW Results",
     "Case study: a brand-new Derby embroidery business, launched July 2026, from page 2–3 to #2 on Google Maps for 'embroidery Derby' in a few weeks.",
     results, [ORG, crumbs_schema(RES_CRUMBS)], "results/"),
    ("about-dan/", "about-dan/index.html", 1, "About Dan Cooper, Local SEO Derby | TW Results",
     "Dan Cooper runs TW Results from Derby, helping trades and local businesses get found on Google. No account managers: you deal with Dan.",
     about, [ORG, crumbs_schema(ABOUT_CRUMBS), {"@context": "https://schema.org", "@type": "Person", "@id": SITE + "/about-dan/#dan", "name": "Dan Cooper", "jobTitle": "Founder", "worksFor": {"@id": SITE + "/#business"}, "email": EMAIL}], "about-dan/"),
    ("contact/", "contact/index.html", 1, "Free Google Check, Derby | TW Results",
     "Ask Dan for a free Google check on your Derby business. Send the form and I'll call you back within one working day.",
     contact, [ORG, crumbs_schema(CON_CRUMBS)], "contact/"),
    ("privacy/", "privacy/index.html", 1, "Privacy | TW Results",
     "How TW Results handles the details you send through the enquiry form, and how analytics cookies are used.",
     privacy, None, None),
    ("404.html", "404.html", 0, "Page not found | TW Results",
     "That page doesn't exist. Go to the TW Results home page or ask for a free Google check.", notfound, None, None),
]

PAGES += [area_page(a) for a in AREA_PAGES]

for slug, out, depth, title, desc, body, schema, cur in PAGES:
    if depth == 1:
        for u, _ in NAV:
            body = body.replace(f'href="{u}', f'href="../{u}')
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page(slug, title, desc, body, schema, depth, cur))

with open(os.path.join(ROOT, "robots.txt"), "w") as f:
    if LIVE:
        f.write("User-agent: *\nAllow: /\n\nUser-agent: Googlebot\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nSitemap: https://twresults.com/sitemap.xml\n")
    else:
        f.write("# PREVIEW BUILD: blocks all crawlers. Rebuild with --live before launch.\nUser-agent: *\nDisallow: /\n")

urls = [s for s, *_ in PAGES if s != "404.html"]
with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        f.write(f"  <url><loc>{SITE}/{u}</loc><lastmod>{LASTMOD}</lastmod></url>\n")
    f.write("</urlset>\n")
print("built", "LIVE" if LIVE else "PREVIEW")
