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
V = "2"  # asset cache-buster

PHONE = '<span class="ph">[TWR PHONE: giffgaff number to come]</span>'
TEL = "tel:[TWR PHONE E.164]"
EMAIL = "dan@twresults.com"
ADDRESS = '<span class="ph">[ADDRESS: Derby, by appointment]</span>'
FORM_ENDPOINT = "[FORM ENDPOINT]"   # Formspree, e.g. https://formspree.io/f/xxxxxxx
TAGLINE = "Get found on Google. Get more work."
LOCKED = "The top 3 on Google get over half the clicks. For your trade, in your area, that's your competitors. We fix that."
CALLBACK = "We'll call you back within one working day."
# DRAFT town list: must match the Google profile service area before launch
TOWNS = ["Derby", "Chellaston", "Alvaston", "Mickleover", "Littleover", "Allestree", "Spondon", "Belper", "Ripley", "Long Eaton", "Burton", "Ashby", "Nottingham"]
TOWNS_DRAFT = '<span class="ph">[DRAFT: town list to confirm]</span>'

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
        # "telephone": add the real giffgaff number in +44 format once it is live (must match the Google profile)
        "logo": SITE + "/assets/apple-touch-icon.png",
        "image": SITE + "/assets/og-image.png",
        "description": "Local SEO, Google Business Profile work and websites for tradespeople in Derby and the East Midlands.",
        "founder": {"@type": "Person", "@id": SITE + "/about-dan/#dan", "name": "Dan Cooper"},
        "address": {"@type": "PostalAddress", "addressLocality": "Derby", "addressRegion": "Derbyshire", "addressCountry": "GB"},
        "areaServed": [{"@type": "City", "name": t} for t in TOWNS] + [{"@type": "AdministrativeArea", "name": "East Midlands"}],
        "knowsAbout": ["Local SEO", "Google Business Profile optimisation", "Google Maps rankings", "Websites for tradespeople"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "serviceType": t, "areaServed": "Derby and the East Midlands"}}
            for n, t in [("Google Maps and local SEO", "Local SEO and Google Business Profile optimisation"),
                         ("Website fixes", "Website improvements for trades"),
                         ("New websites for trades", "Web design for tradespeople")]]},
    }

def crumbs_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": SITE + "/" + u} for i, (u, n) in enumerate(items, 1)]}

def crumbs_html(items, depth):
    p = "../" * depth
    lis = "".join(f'<li><a href="{p}{u}">{n}</a></li>' for u, n in items[:-1]) + f'<li aria-current="page">{items[-1][1]}</li>'
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

FAQ = [
    ("Can you guarantee I'll be number one?", "No. Nobody honest can. We do the work Google rewards and show you where you stand every month."),
    ("How long does it take?", "It depends on your trade, your town and who you're up against. You'll see your position in a report every month."),
    ("Do I get tied into a contract?", "A minimum of 3 monthly payments, then month to month with 30 days' notice. [DRAFT: terms not final]"),
    ("I already have a website. Can you work with it?", "Yes, in most cases, whoever built it."),
    ("I only have a Facebook page.", "Then you need a simple website. We build those, set up in your name."),
    ("Who do I actually talk to?", "Dan. Every time."),
]
def faq_html():
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{ph_text(a)}</p></details>" for q, a in FAQ) + "</div>"
def faq_schema():
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s*\[DRAFT[^\]]*\]", "", a)}} for q, a in FAQ]}

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
  <a class="btn" href="{TEL}">Call Dan</a>
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
    <p>Call: <a href="{TEL}">{PHONE}</a></p>
    <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p>Local SEO and websites for trades across Derby and the East Midlands.</p>
   </div>
  </div>
  <div class="legal"><p>&copy; 2026 TW Results. Daniel Cooper trading as TW Results.</p></div>
 </div>
</footer>
<div class="callbar on-navy"><a class="btn" href="{TEL}">Call Dan</a></div>
<div class="cookie" id="cookie" hidden role="region" aria-label="Cookies">
 <div class="wrap"><p>Can we use analytics cookies to see how the site is used? <a href="{p}privacy/">Privacy</a></p>
 <div class="cta" style="margin:0"><button class="btn" type="button" data-consent="yes">Accept</button><button class="btn btn-s" type="button" data-consent="no">Reject</button></div></div>
</div>
<script src="{p}assets/site.js?v={V}" defer></script>
</body>
</html>
"""

def form(depth, heading_tag="h2", heading="Get a free Google check"):
    p = "../" * depth
    return f"""<div class="formcard" id="check"><span class="c3"></span><span class="c4"></span>
 <{heading_tag} class="form-h">{heading}</{heading_tag}>
 <p class="promise">Tell us who you are. {CALLBACK}</p>
 <form id="enquiry" action="{FORM_ENDPOINT}" method="POST" novalidate>
  <p class="hp" aria-hidden="true"><label for="gotcha">Leave this empty</label><input id="gotcha" name="_gotcha" tabindex="-1" autocomplete="off"></p>
  <input type="hidden" name="_subject" value="New enquiry from twresults.com">
  <div class="f"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required></div>
  <div class="f"><label for="business">Trade or business</label><input id="business" name="business" autocomplete="organization" required placeholder="e.g. Smith Plastering, Belper"></div>
  <div class="f"><label for="contact">Phone or email</label><input id="contact" name="contact" autocomplete="tel" required></div>
  <div class="f"><label for="message">Message <span class="opt">(optional)</span></label><textarea id="message" name="message" rows="3"></textarea></div>
  <label class="tick"><input type="checkbox" name="free_google_check" value="Yes" checked> Yes, I'd like a free Google check</label>
  <button class="btn" type="submit">Send to Dan</button>
  <p class="consent">We only use your details to reply. <a href="{p}privacy/">Privacy notice</a>.</p>
  <p class="form-msg" id="form-msg" role="status" tabindex="-1"></p>
 </form>
</div>"""

MAP_SVG = """<svg viewBox="0 0 400 120" preserveAspectRatio="xMidYMid slice" width="100%" height="100%" aria-hidden="true" focusable="false" style="position:absolute;inset:0">
<g fill="none" stroke="#FFFFFF" stroke-width="9"><path d="M-10 92 L140 78 L250 102 L410 70"/><path d="M90 -10 L120 130"/><path d="M300 -10 L262 130"/></g>
<g fill="none" stroke="#FFFFFF" stroke-width="4"><path d="M-10 34 L180 44 L410 24"/><path d="M190 44 L205 130"/><path d="M350 24 L370 130"/></g>
<g fill="none" stroke="#B4C8EA" stroke-width="1.5"><path d="M-10 62 C80 58 160 118 260 58 S380 50 410 54"/></g>
<g font-family="Arimo,Arial,sans-serif" font-weight="700" font-size="13">
<g transform="translate(70 56)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">1</text></g>
<g transform="translate(232 70)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">2</text></g>
<g transform="translate(330 40)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">3</text></g>
</g></svg>"""

def serp():
    rows = "".join(f'<li><span class="n">{n}</span><span><span class="nm">{nm}</span><span class="bar"></span><span class="bar s"></span></span><span class="call">Call</span></li>'
                   for n, nm in [("1", "Competitor"), ("2", "Competitor"), ("3", "Competitor")])
    return f"""<figure style="margin:0">
 <div class="serp" role="img" aria-label="A mock Google Maps result for a trade near me in Derby. Three competitors fill the top three places. Your business is on page 2.">
  <div class="serp-q"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="7.5" cy="7.5" r="5.5" fill="none" stroke="#121F45" stroke-width="2"/><path d="M11.6 11.6 L16 16" stroke="#121F45" stroke-width="2"/></svg><span><span id="trade">plasterer</span> near me, Derby</span></div>
  <div class="serp-map">{MAP_SVG}</div>
  <ol>{rows}</ol>
  <span class="gap">4 to 20: other businesses</span>
  <p class="page2">Page 2</p>
  <div class="you"><span class="n">21</span><span><span class="nm">You</span><span class="bar s"></span></span><span class="call">No call</span></div>
 </div>
 <figcaption class="serp-note">Illustration. Most people ring one of the first three.</figcaption>
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
    ("new-websites", "New websites for trades", "A simple, fast site in your name, if you haven't got one."),
]
STEPS = [
    ("Free Google check", "We look at where you show up and who&rsquo;s ahead of you. You get a straight answer."),
    ("We fix it", "Your Google profile, website and directory details, sorted."),
    ("Monthly report", "One page: what we did and where you rank."),
]

# ---------------- Home ----------------
towns_li = "".join(f"<li>{t}</li>" for t in TOWNS)
home = f"""
<section class="hero" aria-labelledby="h1">
 <div class="wrap"><div class="hero-grid">
  <div>
   <h1 id="h1">{TAGLINE}</h1>
   <p class="kw">Local SEO, Google Maps and websites for trades in Derby and the East Midlands.</p>
   <p class="stat">{esc(LOCKED)}<cite>Source: Backlinko, 2025 (share of clicks in Google search)</cite></p>
   <div class="cta"><a class="btn" href="{TEL}">Call Dan</a><a class="tel" href="{TEL}">{PHONE}</a></div>
  </div>
  {form(0)}
 </div></div>
</section>

<section class="sec" aria-labelledby="h-problem">
 <div class="wrap"><div class="split mid">
  <div>
   <h2 id="h-problem">Three names. One phone call.</h2>
   <p class="lede">Customers ring one of the first three. If you&rsquo;re on page 2, the work goes to someone else.</p>
  </div>
  {serp()}
 </div></div>
</section>

<section class="sec pale" aria-labelledby="h-services">
 <div class="wrap">
  <h2 id="h-services">Local SEO and websites for Derby trades</h2>
  <ul class="rows">{"".join(f'<li><h3>{h}</h3><p>{t}</p><a class="link" href="what-we-do/#{a}">More<span class="vh"> about {h.lower()}</span></a></li>' for a, h, t in SERVICES)}</ul>
 </div>
</section>

<section class="sec navy on-navy" aria-labelledby="h-results">
 <div class="wrap"><div class="split">
  <div>
   <p class="big" aria-hidden="true">#2</p>
   <h2 id="h-results">On Google Maps for &lsquo;embroidery Derby&rsquo;</h2>
   <p>Case study: Eaton Embroidery, a Derby embroidery business.</p>
   <dl class="dates"><div><dt>10/09/2026</dt><dd>#2</dd></div><div><dt>07/10/2026</dt><dd>Still #2</dd></div></dl>
   <p style="margin-top:2rem"><a class="link" href="results/">See the case study</a></p>
  </div>
  <div class="shots">{shot("10/09/2026")}{shot("07/10/2026")}</div>
 </div></div>
</section>

<section class="sec" aria-labelledby="h-dan">
 <div class="wrap"><div class="person">
  {headshot()}
  <div>
   <h2 id="h-dan">You deal with Dan</h2>
   <p class="lede">I&rsquo;m Dan Cooper. I help trades across Derby who are good at the job but hard to find on Google.</p>
   <p>No account managers, no call centre. If something won&rsquo;t help, I&rsquo;ll tell you before you spend anything.</p>
   <p><a class="link" href="about-dan/">About Dan</a></p>
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
  <h2 id="h-areas">Areas we cover</h2>
  <div>
   <ul class="towns">{towns_li}</ul>
   <p class="small">And the rest of the East Midlands. {TOWNS_DRAFT}</p>
   <div class="cta"><a class="btn" href="#check">Get a free Google check</a></div>
  </div>
 </div></div>
</section>
"""

# ---------------- What we do ----------------
SVC_DETAIL = [
    ("google-maps", "Google Maps and local SEO in Derby",
     "Get into the top three on Google Maps when people near you search for your trade.",
     ["Your Google Business Profile set up properly: categories, services, area, hours, photos", "A post on your profile every week", "More reviews from real customers, and replies to every one", "Matching details on the directories that matter", "Where you rank, checked every month"],
     "Send photos of your work and ask happy customers for a review."),
    ("website-fixes", "Website fixes that bring in calls",
     "Plenty of trade websites look fine but don&rsquo;t make the phone ring. We fix that, whoever built yours.",
     ["Clear wording: what you do and where", "A fast site that works on a phone", "Pages for your services and towns", "A call button on every page"],
     "Tell us the work you want more of, and check the wording."),
    ("new-websites", "New websites for trades",
     "No website, or just a Facebook page? We build a simple, fast site that Google can send people to.",
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
 <h1>Local SEO and websites for trades in Derby</h1>
 <p class="lede">Three services. Plain English. We start with a free Google check and tell you what&rsquo;s worth doing.</p>
</div></section>
<div class="wrap">{"".join(svc(*s) for s in SVC_DETAIL)}</div>
<section class="band navy on-navy"><div class="wrap"><h2>Want to know where you stand?</h2><a class="btn" href="../contact/#check">Get a free Google check</a></div></section>
"""

# ---------------- Results (case study) ----------------
RES_CRUMBS = [("", "Home"), ("results/", "Results")]
results = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(RES_CRUMBS, 1)}
 <h1>Local SEO case study: embroidery in Derby</h1>
 <p class="lede">Eaton Embroidery is a Derby embroidery business and our first case study client. We log the results with dates, good or bad.</p>
</div></section>
<section class="sec navy on-navy" aria-labelledby="h-fact"><div class="wrap"><div class="split">
 <div><p class="big" aria-hidden="true">#2</p><h2 id="h-fact">On Google Maps for &lsquo;embroidery Derby&rsquo;</h2>
  <dl class="dates"><div><dt>10/09/2026 (start)</dt><dd>#2</dd></div><div><dt>07/10/2026</dt><dd>Still #2</dd></div></dl>
  <p style="margin-top:1.5rem">A top-three spot, held. Checked in a private browser.</p></div>
 <div class="shots">{shot("10/09/2026")}{shot("07/10/2026")}</div>
</div></div></section>
<section class="sec" aria-labelledby="h-work"><div class="wrap"><div class="split">
 <h2 id="h-work">The monthly work</h2>
 <ul class="plain"><li>Google Business Profile kept complete</li><li>A post every week</li><li>New photos of finished work</li><li>A reply to every review</li><li>Website fixes to match what people search for</li></ul>
</div></div></section>
<section class="sec pale" aria-labelledby="h-log"><div class="wrap"><div class="split">
 <h2 id="h-log">Results log</h2>
 <ol class="log"><li><time datetime="2026-09-10">10/09/2026</time><p>Tracking starts. #2 for &lsquo;embroidery Derby&rsquo;.</p></li><li><time datetime="2026-10-07">07/10/2026</time><p>Still #2 for &lsquo;embroidery Derby&rsquo;.</p></li></ol>
</div></div></section>
<section class="band navy on-navy"><div class="wrap"><h2>Where do you rank?</h2><a class="btn" href="../contact/#check">Get a free Google check</a></div></section>
"""

# ---------------- About Dan ----------------
ABOUT_CRUMBS = [("", "Home"), ("about-dan/", "About Dan")]
about = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(ABOUT_CRUMBS, 1)}
 <div class="person">
  {headshot()}
  <div>
   <h1>Dan Cooper, local SEO for Derby trades</h1>
   <p class="lede">I run TW Results from Derby. I work with trades who are good at the job but hard to find on Google.</p>
   <p>I keep it simple: find what&rsquo;s wrong, fix it, show you the result every month. No account managers, no call centre.</p>
   <p><span class="ph">[DAN TO ADD 1 TO 2 LINES OF REAL BACKGROUND]</span></p>
   <div class="cta"><a class="btn" href="{TEL}">Call Dan</a><a class="link" href="../contact/#check">Get a free Google check</a></div>
  </div>
 </div>
</div></section>
"""

# ---------------- Contact ----------------
CON_CRUMBS = [("", "Home"), ("contact/", "Contact")]
contact = f"""
<section class="page-hero"><div class="wrap">
 {crumbs_html(CON_CRUMBS, 1)}
 <div class="hero-grid">
  <div>
   <h1>Free Google check for Derby trades</h1>
   <p class="lede">Send the form or call. {CALLBACK}</p>
   <a class="phone-big" href="{TEL}">{PHONE}</a>
   <dl class="facts">
    <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
    <div><dt>Meetings</dt><dd>{ADDRESS}</dd></div>
    <div><dt>Covering</dt><dd>Derby and the East Midlands</dd></div>
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
 <p class="lede">What we collect, why, and how to get it deleted.</p>
</div></section>
<section class="sec"><div class="wrap"><div class="prose">
 <p><span class="ph">[DRAFT: Dan to approve]</span> Last updated <span class="ph">[DATE OF APPROVAL]</span>.</p>
 <h2>Who we are</h2><p>TW Results is run by Daniel Cooper, trading as TW Results, based in Derby. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
 <h2>What the form collects</h2><p>Your name, trade or business, phone number or email, your message and whether you want a free Google check. We use it only to reply and, if you become a client, to do the work. We don&rsquo;t sell it or pass it on.</p>
 <h2>Who processes it</h2><p>The form is sent through Formspree, which passes it to our email. Our email runs on Google Workspace.</p>
 <h2>Analytics</h2><p>If you click Accept on the cookie bar, we use Google Analytics 4 to count visits. It doesn&rsquo;t load unless you accept.</p>
 <h2>How long we keep it</h2><p>Enquiries that don&rsquo;t turn into work are deleted after <span class="ph">[RETENTION PERIOD: Dan to confirm]</span>. Client records are kept as long as the law requires for tax and accounts.</p>
 <h2>Your rights</h2><p>You can ask to see, correct or delete your details. Email <a href="mailto:{EMAIL}">{EMAIL}</a>. You can also complain to the Information Commissioner&rsquo;s Office at <a href="https://ico.org.uk">ico.org.uk</a>.</p>
</div></div></section>
"""

notfound = f"""
<section class="page-hero"><div class="wrap">
 <h1>That page doesn&rsquo;t exist.</h1>
 <p class="lede">It may have moved, or the link was wrong.</p>
 <div class="cta"><a class="btn" href="./">Go to the home page</a><a class="link" href="contact/#check">Get a free Google check</a></div>
</div></section>
"""

ORG = org_schema()
PAGES = [
    ("", "index.html", 0, "Local SEO for Trades in Derby | TW Results",
     "Get found on Google. Get more work. Local SEO, Google Maps and websites for trades in Derby and the East Midlands. Free Google check.",
     home, [ORG, faq_schema()], None),
    ("what-we-do/", "what-we-do/index.html", 1, "Local SEO & Websites for Trades, Derby | TW Results",
     "Google Business Profile and local SEO, website fixes and new websites for tradespeople in Derby and the East Midlands. Plain English.",
     wwd, [ORG, crumbs_schema(WWD_CRUMBS)], "what-we-do/"),
    ("results/", "results/index.html", 1, "Local SEO Case Study, Derby | TW Results",
     "Case study: Eaton Embroidery, a Derby embroidery business, #2 on Google Maps for 'embroidery Derby' on 10/09/2026 and 07/10/2026.",
     results, [ORG, crumbs_schema(RES_CRUMBS)], "results/"),
    ("about-dan/", "about-dan/index.html", 1, "About Dan Cooper, Local SEO Derby | TW Results",
     "Dan Cooper runs TW Results from Derby, helping trades get found on Google. No account managers: you deal with Dan, every time.",
     about, [ORG, crumbs_schema(ABOUT_CRUMBS), {"@context": "https://schema.org", "@type": "Person", "@id": SITE + "/about-dan/#dan", "name": "Dan Cooper", "jobTitle": "Founder", "worksFor": {"@id": SITE + "/#business"}, "email": EMAIL}], "about-dan/"),
    ("contact/", "contact/index.html", 1, "Free Google Check for Trades, Derby | TW Results",
     "Ask for a free Google check. Trades in Derby and the East Midlands: send the form or call Dan. We'll call you back within one working day.",
     contact, [ORG, crumbs_schema(CON_CRUMBS)], "contact/"),
    ("privacy/", "privacy/index.html", 1, "Privacy | TW Results",
     "How TW Results handles the details you send through the enquiry form, and how analytics cookies are used.",
     privacy, None, None),
    ("404.html", "404.html", 0, "Page not found | TW Results",
     "That page doesn't exist. Go to the TW Results home page or ask for a free Google check.", notfound, None, None),
]

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
