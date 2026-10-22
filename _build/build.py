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
V = "12"  # asset cache-buster

# PHONE FLAG: leave PHONE_DISPLAY = None until the giffgaff number is live. [TWR PHONE: giffgaff number to come]
# Set both, e.g. PHONE_DISPLAY = "07xxx xxxxxx" and PHONE_E164 = "+447xxxxxxxxx" (NEVER 07944 915880),
# and every Call Dan button, the footer number, the contact number and schema "telephone" appear automatically.
PHONE_DISPLAY = None
PHONE_E164 = None
HAS_PHONE = bool(PHONE_DISPLAY and PHONE_E164)
PHONE = PHONE_DISPLAY or ""
TEL = "tel:" + (PHONE_E164 or "")
EMAIL = "dan@twresults.com"
ADDRESS = 'Derby, by appointment'
FORM_ENDPOINT = "[FORM ENDPOINT]"   # Formspree, e.g. https://formspree.io/f/xxxxxxx
TAGLINE = "Get found on Google. Get more work."
# Source checked 18/10/2026: Backlinko organic CTR study (published 27/08/2019, updated 16/04/2025):
# "we found that the top 3 Google search results get 54.4% of all clicks" and "only .63% of Google searchers clicked on something from the second page".
# It measures ORGANIC search results (Search Console data), not the Google Maps pack.
BACKLINKO_URL = "https://backlinko.com/google-ctr-stats"
CALLBACK = "I'll call you back within one working day."
# DRAFT town list: must match the Google profile service area before launch
TOWNS = ["Derby", "Chellaston", "Alvaston", "Mickleover", "Littleover", "Allestree", "Spondon", "Belper", "Ripley", "Long Eaton", "Ashby"]
REACH = "Derby and surrounding areas, the East Midlands and UK-wide"
REACH_LINE = "Based in Derby. Working across Derby and surrounding areas, the East Midlands and UK-wide."
WIDE_AREAS = [{"@type": "AdministrativeArea", "name": "East Midlands"}, {"@type": "Country", "name": "United Kingdom"}]
TOWNS_DRAFT = '<span class="ph">[DRAFT: town list to confirm with Dan]</span>'

NAV = [("what-we-do/", "What we do"), ("results/", "Results"), ("contact/", "Contact")]
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
        "description": "Local SEO, Google Business Profile work and websites for trades and local businesses in Derby, the East Midlands and UK-wide.",
        "founder": {"@type": "Person", "@id": SITE + "/#dan", "name": "Dan Cooper"},
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

EXCL = "One business per trade, per town. When we work together, I won't take on a competitor in your trade in your town."
FAQ = [
    ("Can you guarantee I'll be number one?", "No. Google decides the rankings, so anyone who guarantees you the top spot is guessing. What I can promise is the work that gives you the best chance, and a plain English report every month showing where you stand."),
    ("How long does it take?", "It depends on your trade, your town and who you're up against. You'll see your position in a report every month."),
    ("Do I get tied into a contract?", "There's a 3-month minimum, then it's month to month. Google rewards businesses that stay active and up to date: regular posts, new reviews and accurate details. It takes weeks for changes to show up in the rankings, so 3 months gives the work a fair chance to show results."),
    ("Will you work with my competitors?", EXCL),
    ("Who do I actually talk to?", "Me, Dan. Every time."),
]
FAQ_WWD = [FAQ.pop(1)] + [
    ("I already have a website. Can you work with it?", "Yes, in most cases, whoever built it."),
    ("I only have a Facebook page.", "Then you need a simple website. I build those, set up in your name."),
]
def faq_html(items=None):
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{ph_text(a)}</p></details>" for q, a in (items or FAQ)) + "</div>"
def faq_schema(items=None):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in (items or FAQ)]}

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
    nav_html = "" if slug == "" else f'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>\n  <nav class="nav" id="nav" aria-label="Main"><ul>{navli}</ul></nav>'
    tail = body.rstrip()[-600:]
    if slug != "contact/" and 'class="band' not in tail:
        body += f'\n<section class="band navy on-navy final-cta"><div class="wrap"><div><h2>Where do you rank?</h2><p>Free Google check. {CALLBACK}</p></div><a class="btn" href="{form_href}">Get a free Google check</a></div></section>\n'
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
  {nav_html}
  {head_btn}
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="legal-bar"><div class="wrap"><p>&copy; 2026 TW Results, {ADDRESS}. <a href="mailto:{EMAIL}">{EMAIL}</a> &middot; <a href="{p}privacy/">Privacy</a></p></div></footer>
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
    return f"""<p class="pre-form">If you&rsquo;re on page 2 of Google, almost nobody sees you. We work to get you onto the map and the first page.</p>
<div class="formcard"><span class="c3"></span><span class="c4"></span>
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

# CASE STUDY SCREENSHOTS FLAG: [] = none shown (launch). Add dates to show dated Google Maps screenshot slots again,
# e.g. CASE_STUDY_SHOTS = ["10/09/2026", "07/10/2026"] (until real images are wired in they show as placeholders).
CASE_STUDY_SHOTS = []
def shots_html():
    return f'<div class="shots">{"".join(shot(d) for d in CASE_STUDY_SHOTS)}</div>' if CASE_STUDY_SHOTS else ""
# HEADSHOT FLAG: None = no photo on the home page. Set to an image path under the site root, e.g. "assets/dan.webp",
# and a small square photo of Dan shows beside the "You deal with me, Dan" line.
HEADSHOT = None
def headshot(note="Dan outdoors in Derby, daylight, shoulders up. 4:5, 1200 x 1500px WebP"):
    return f'<figure class="photo"><b>[HEADSHOT]</b><span>{note}</span></figure>'

SERVICES = [
    ("google-maps", "Google Maps and local SEO", "Your Google profile set up properly, with posts, reviews and listings."),
    ("website-fixes", "Website fixes", "Clear wording, a fast site, a call button on every page."),
    ("new-websites", "New websites", "A simple, fast site in your name."),
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
def towns_li(p=""):
    return "".join(f'<li><a href="{p}{AREA_LINKS[t]}">{t}</a></li>' if t in AREA_LINKS else f"<li>{t}</li>" for t in TOWNS)
CITE = f'<a href="{BACKLINKO_URL}" rel="noopener">Backlinko organic click-through rate study</a>, updated 16/04/2025'
EE_WORK = "I built an optimised website, set up and optimised the Google Business Profile, and handled reviews, posts and citations."
EE_START = "Brand-new business, launched July 2026, went from page 2&ndash;3 of Google to #2 on Google Maps for &ldquo;embroidery Derby&rdquo; in a few weeks."
EE_CHECKS = "Checked 10/09/2026 and 07/10/2026: #2 both times, position held."
EE_FIGS = [("80%", "of work now inbound (reported by the business)"), ("10", "more enquiries a week (reported by the business)")]
def ee_result():
    figs = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in EE_FIGS)
    return (f'<p class="big" aria-hidden="true">#2</p>'
            f'<p class="big-cap">#2 on Google Maps for &ldquo;embroidery Derby&rdquo; in a few weeks.</p>'
            f'<dl class="kpis">{figs}</dl>')
def call_cta(extra=""):
    return f'<div class="cta"><a class="btn" href="{TEL}">Call Dan</a><a class="tel" href="{TEL}">{PHONE}</a>{extra}</div>' if HAS_PHONE else (f'<div class="cta">{extra}</div>' if extra else "")

STAT_LINE = "The top 3 on Google get over half the clicks. Clicks are calls. In your area, those calls go to your competitors."
def big_stats():
    items = [("#2", "on Google Maps for &ldquo;embroidery Derby&rdquo; in a few weeks"), *EE_FIGS]
    return '<dl class="bigstats">' + "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in items) + "</dl>"

home = f"""
<section class="hero hero-navy on-navy" aria-labelledby="h1">
 <div class="wrap hero-n-grid"><div>
  <h1 id="h1">{TAGLINE}</h1>
  <p class="kw">Local SEO, Google Maps and websites for trades and local businesses in {REACH}.</p>
  <div class="cta"><a class="btn btn-w" href="#enquiry">Get a free Google check</a>{f'<a class="tel" href="{TEL}">Call Dan: {PHONE}</a>' if HAS_PHONE else ""}</div>
 </div>
 <div class="hero-proof"><span class="n" aria-hidden="true">#2</span><span class="t">on Google Maps for &ldquo;embroidery Derby&rdquo; in a few weeks. A Derby client.</span></div>
 </div>
</section>

<section class="sec problem" aria-labelledby="h-problem">
 <div class="wrap"><div class="split mid">
  <div>
   <h2 id="h-problem">Not in the top 3? Your competitors are getting your calls.</h2>
   <p class="sub">Your competitors aren&rsquo;t better than you. They&rsquo;re just easier to find.</p>
   <p class="lede">{STAT_LINE}</p>
   <p class="small">Source: {CITE}. Organic search results.</p>
  </div>
  {serp()}
 </div></div>
</section>

<section class="sec pale form-sec" aria-label="Free Google check">
 <div class="wrap narrow">
  {form(0)}
  <p class="alt">Prefer email? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="alt"><a class="link" href="results/">See the results</a></p>
 </div>
</section>

<section class="sec svc-tight" aria-labelledby="h-services">
 <div class="wrap">
  <h2 id="h-services">Local SEO and websites for trades and local businesses</h2>
  <ul class="tiles">{"".join(f'<li><h3>{h}</h3><p>{t}</p></li>' for a, h, t in SERVICES)}</ul>
  <p><a class="link" href="what-we-do/">What I do</a></p>
 </div>
</section>

<section class="sec navy on-navy" aria-labelledby="h-results">
 <div class="wrap">
  <h2 id="h-results">Results for a Derby business</h2>
  {big_stats()}
  <div class="split">
  <div>
   <p class="lede">Eaton Embroidery, a Derby embroidery business, is a client.</p>
   <p>{EE_WORK}</p>
   <p class="small">{EE_START} {EE_CHECKS}</p>
   <p style="margin-top:1.5rem"><a class="link" href="results/">See the case study</a></p>
  </div>
  {shots_html()}
 </div></div>
</section>

<section class="dan-line" aria-label="Who you deal with"><div class="wrap">{f'<img class="dan-photo" src="{HEADSHOT}" alt="Dan Cooper" width="96" height="96">' if HEADSHOT else ""}<p>You deal with me, Dan, from the first chat to every monthly report.</p></div></section>

<section class="sec pale" aria-labelledby="h-steps">
 <div class="wrap">
  <h2 id="h-steps">How it works</h2>
  <ol class="steps">{"".join(f"<li><h3>{h}</h3><p>{t}</p></li>" for h, t in STEPS)}</ol>
  <p class="excl">{ph_text(EXCL)}</p>
 </div>
</section>

<section class="sec" aria-labelledby="h-faq">
 <div class="wrap"><div class="split">
  <h2 id="h-faq">Local SEO questions</h2>
  {faq_html()}
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
<section class="page-hero on-navy"><div class="wrap">
 {crumbs_html(WWD_CRUMBS, 1)}
 <h1>Local SEO and websites for Derby businesses</h1>
 <p class="lede">Three services, in plain English. I start with a free Google check and tell you what&rsquo;s worth doing.</p>
</div></section>
<div class="wrap">{"".join(svc(*s) for s in SVC_DETAIL)}</div>
<section class="sec pale" aria-labelledby="h-faq"><div class="wrap"><div class="split">
 <h2 id="h-faq">More questions</h2>
 {faq_html(FAQ_WWD)}
</div></div></section>
<section class="band navy on-navy"><div class="wrap"><h2>Want to know where you stand?</h2><a class="btn" href="../contact/#enquiry">Get a free Google check</a></div></section>
"""

# ---------------- Results (case study) ----------------
RES_CRUMBS = [("", "Home"), ("results/", "Results")]
results = f"""
<section class="page-hero on-navy"><div class="wrap">
 {crumbs_html(RES_CRUMBS, 1)}
 <h1>Local SEO case study: an embroidery business in Derby</h1>
 <p class="lede">Eaton Embroidery is a Derby embroidery business and a TW Results client. I built its website and Google Business Profile and took it to #2 on Google Maps for &ldquo;embroidery Derby&rdquo; within a few weeks.</p>
 {big_stats()}
</div></section>
<section class="sec" aria-labelledby="h-work"><div class="wrap"><div class="split">
 <h2 id="h-work">What I did</h2>
 <ul class="plain"><li>Built an optimised website</li><li>Set up and optimised the Google Business Profile</li><li>Reviews: every new review replied to</li><li>Regular Google posts</li><li>Citations: matching business details on directories such as Yell and Bing</li></ul>
</div></div></section>
<section class="sec pale" aria-labelledby="h-fact"><div class="wrap"><div class="split">
 <div><h2 id="h-fact">Results for a Derby business</h2>
  <p class="lede">{EE_START}</p>
  <p class="small">{EE_CHECKS}</p></div>
 {shots_html()}
</div></div></section>
<section class="sec" aria-labelledby="h-log"><div class="wrap"><div class="split">
 <h2 id="h-log">Results log</h2>
 <ol class="log"><li><time datetime="2026-07">July 2026</time><p>Brand-new business launched. Page 2&ndash;3 of Google for &ldquo;embroidery Derby&rdquo;.</p></li><li><time datetime="2026-09-10">10/09/2026</time><p>Checked after the work: #2 on Google Maps for &ldquo;embroidery Derby&rdquo;.</p></li><li><time datetime="2026-10-07">07/10/2026</time><p>Checked again: #2, position held.</p></li></ol>
</div></div></section>
<section class="band navy on-navy"><div class="wrap"><h2>Where do you rank?</h2><a class="btn" href="../contact/#enquiry">Get a free Google check</a></div></section>
"""

# ---------------- Contact ----------------
CON_CRUMBS = [("", "Home"), ("contact/", "Contact")]
phone_big = f'<a class="phone-big" href="{TEL}">{PHONE}</a>' if HAS_PHONE else ""
contact = f"""
<section class="page-hero on-navy"><div class="wrap">
 {crumbs_html(CON_CRUMBS, 1)}
 <div class="hero-grid">
  <div>
   <h1>Free Google check for Derby businesses</h1>
   <p class="lede">Send the form and I&rsquo;ll check how you show up on Google. {CALLBACK}</p>
   {phone_big}
   <dl class="facts">
    <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
    <div><dt>Meetings</dt><dd>In Derby, by appointment</dd></div>
    <div><dt>Covering</dt><dd>{REACH}</dd></div>
   </dl>
  </div>
  <div>{form(1)}</div>
 </div>
</div></section>
"""

# ---------------- Privacy ----------------
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import privacy_notice
# ICO FLAG: None = no ICO line on the privacy page (e.g. if Dan is exempt from the data protection fee);
# "pending" = shows [ICO REG NO: pending]; a real number, e.g. "ZB123456" = shows "ICO registration number: ZB123456".
ICO_REG = None
PRIVACY_HTML = privacy_notice.to_html('<p><button class="btn btn-s" type="button" data-cookie-reset>Change my cookie choice</button></p>', ico=ICO_REG)
privacy = f"""
<section class="page-hero on-navy"><div class="wrap">
 <h1>Privacy</h1>
 <p class="lede">What I collect, why, and how to get it deleted.</p>
</div></section>
<section class="sec"><div class="wrap"><div class="prose">
 {PRIVACY_HTML}
</div></div></section>
"""

notfound = f"""
<section class="page-hero on-navy"><div class="wrap">
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
<section class="page-hero on-navy"><div class="wrap">
 {crumbs_html(crumbs, 2)}
 <div class="hero-grid">
  <div>
   <h1>Local SEO and websites in {name}</h1>
   <p class="lede">{a["intro"]}</p>
   {f'<ul class="plain" style="margin-top:1.5rem">{local}</ul>' if local else ""}
  </div>
  <div>{form(2)}</div>
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
     wwd, [ORG, crumbs_schema(WWD_CRUMBS), faq_schema(FAQ_WWD)], "what-we-do/"),
    ("results/", "results/index.html", 1, "Local SEO Case Study, Derby | TW Results",
     "Case study: a new Derby embroidery business, launched July 2026, went from page 2–3 of Google to #2 on Google Maps for 'embroidery Derby' in a few weeks.",
     results, [ORG, crumbs_schema(RES_CRUMBS)], "results/"),
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
