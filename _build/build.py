#!/usr/bin/env python3
"""Builds the TW Results static site into the repo root.
Run:  python3 _build/build.py            (preview build: noindex + Disallow-all robots)
      python3 _build/build.py --live     (launch build: indexable, robots allows all, 404 base = /)
"""
import json, os, sys, html

LIVE = "--live" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://twresults.com"
LASTMOD = "2026-10-18"
PREVIEW_BASE = "/twresults-preview/"

PHONE = '<span class="ph">[TWR PHONE: giffgaff number to come]</span>'
TEL = "tel:[TWR PHONE E.164]"
TOWNS = '<span class="ph">[SERVICE AREA TOWNS]</span>'
EMAIL = "dan@twresults.com"
H1_HOME = "The top 3 on Google get over half the clicks. For your trade, in your area, that's your competitors. We fix that."
SUBLINE = "Get found on Google. Get more work."
CLOSE = "Your competitors are getting your customers. We fix that."

NAV = [("what-we-do/", "What we do"), ("eaton-embroidery/", "Eaton Embroidery"), ("about-dan/", "About Dan"), ("contact/", "Contact")]

WM = '<span class="tw">TW</span> <span class="rs">| Results</span>'

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
        "description": "TW Results helps tradespeople in Derby and the East Midlands get found on Google Maps and in search, fixes websites so they bring in calls, and builds simple websites for trades.",
        "founder": {"@type": "Person", "name": "Dan Cooper"},
        "address": {"@type": "PostalAddress", "addressLocality": "Derby", "addressCountry": "GB"},
        "areaServed": [{"@type": "City", "name": "Derby"}, {"@type": "AdministrativeArea", "name": "East Midlands"}, "[SERVICE AREA TOWNS]"],
        "knowsAbout": ["Local SEO", "Google Business Profile optimisation", "Google Maps listings", "Websites for tradespeople", "Online reviews"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Getting you found on Google Maps and in search", "serviceType": "Google listing and local search work for trades"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Fixing your website so it brings in calls", "serviceType": "Website improvements for trades"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "A simple website if you haven't got one", "serviceType": "Websites for tradespeople"}}]},
    }

FAQ = [
    ("Can you guarantee I'll be number one?", "No. Nobody honest can. What we do is the work that Google rewards, and we show you where you stand every month."),
    ("How long does it take?", "It depends on your trade, your area and who you're up against. We won't promise a timescale we can't back up. You'll see your position in a report every month."),
    ("I'm too busy for this.", "That's the point. We do the work. You answer the phone."),
    ("I tried this before and it did nothing.", "Ask them what they actually did. We tell you exactly what we're doing each month and show you the result, good or bad."),
    ("I already have a website. Can you work with it?", "Yes, in most cases, whoever built it."),
    ("I only have a Facebook page.", "Then you need a simple website. We build those."),
    ("Do I get tied into a long contract?", "[DIRECTOR/DAN TO CONFIRM]"),
    ("Who do I actually talk to?", "Dan. Every time."),
]

def ph_text(s):
    """Escape text and wrap any [PLACEHOLDER] in a visible marker."""
    import re
    s = html.escape(s, quote=False)
    return re.sub(r"(\[[A-Z][^\]]*\])", r'<span class="ph">\1</span>', s)

def page(slug, title, desc, body, schema=None, depth=1, current=None, og_title=None):
    p = "../" * depth
    canon = SITE + "/" + slug
    base = ""
    if slug == "404.html":
        base = '<base href="%s">' % ("/" if LIVE else PREVIEW_BASE)
        p = ""
    robots = "" if LIVE else '<meta name="robots" content="noindex, nofollow">\n'
    navli = "".join('<li><a href="%s%s"%s>%s</a></li>' % (p, u, ' aria-current="page"' if u == current else "", t) for u, t in NAV)
    sch = ""
    for s in (schema or []):
        sch += '<script type="application/ld+json">%s</script>\n' % json.dumps(s, ensure_ascii=False, separators=(",", ":"))
    ogt = og_title or title
    foot_links = "".join('<li><a href="%s%s">%s</a></li>' % (p, u, t) for u, t in [("", "Home")] + NAV + [("privacy/", "Privacy")])
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#121F45">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TW Results">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{html.escape(ogt)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="TW | Results. Get found on Google. Get more work.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(ogt)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og-image.png">
<link rel="icon" href="{p}favicon.ico" sizes="32x32">
<link rel="icon" href="{p}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/apple-touch-icon.png">
<link rel="preload" href="{p}assets/fonts/arimo-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/site.css?v=1">
{sch}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
 <div class="wrap">
  <a class="wm" href="{p or './'}" aria-label="TW Results home">{WM}</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <nav class="nav" id="nav" aria-label="Main"><ul>{navli}</ul></nav>
  <a class="btn btn-p" href="{TEL}">Call Dan</a>
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
    <p class="foot-tag">{SUBLINE}</p>
   </div>
   <div>
    <h2>Pages</h2>
    <ul>{foot_links}</ul>
   </div>
   <div>
    <h2>Get hold of Dan</h2>
    <p>Call Dan: <a href="{TEL}">{PHONE}</a></p>
    <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p>Covering Derby and {TOWNS}</p>
   </div>
  </div>
  <div class="legal"><p>&copy; 2026 TW Results. Daniel Cooper trading as TW Results.</p></div>
 </div>
</footer>
<div class="callbar on-navy"><a class="btn" href="{TEL}">Call Dan</a></div>
<div class="cookie" id="cookie" hidden role="region" aria-label="Cookies">
 <div class="wrap"><p>Can we use analytics cookies to see how the site is used? <a href="{p}privacy/">Privacy</a></p>
 <div class="btns" style="margin:0"><button class="btn btn-p" type="button" data-consent="yes">Accept</button><button class="btn btn-s" type="button" data-consent="no">Reject</button></div></div>
</div>
<script src="{p}assets/site.js?v=1" defer></script>
</body>
</html>
"""

def ctas(second="Send a message", depth=1):
    p = "../" * depth
    return f'<div class="btns"><a class="btn btn-p" href="{TEL}">Call Dan</a><a class="btn btn-s" href="{p}contact/#message">{second}</a></div>'

MAP_SVG = """<svg viewBox="0 0 400 150" preserveAspectRatio="xMidYMid slice" width="100%" height="100%" aria-hidden="true" focusable="false" style="position:absolute;inset:0">
<g fill="none" stroke="#FFFFFF" stroke-width="9"><path d="M-10 108 L140 92 L250 120 L410 84"/><path d="M90 -10 L120 160"/><path d="M300 -10 L262 160"/></g>
<g fill="none" stroke="#FFFFFF" stroke-width="4"><path d="M-10 40 L180 52 L410 30"/><path d="M190 52 L205 160"/><path d="M350 30 L370 160"/></g>
<g fill="none" stroke="#B4C8EA" stroke-width="1.5"><path d="M-10 75 C80 70 160 140 260 70 S380 60 410 64"/></g>
<g font-family="Arimo,Arial,sans-serif" font-weight="700" font-size="13">
<g transform="translate(70 66)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">A</text></g>
<g transform="translate(232 98)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">B</text></g>
<g transform="translate(330 48)"><rect x="-11" y="-11" width="22" height="22" fill="#121F45"/><text x="0" y="5" fill="#FFFFFF" text-anchor="middle">C</text></g>
<g transform="translate(160 124)"><rect x="-11" y="-11" width="22" height="22" fill="#FFFFFF" stroke="#121F45" stroke-width="1.5" stroke-dasharray="3 2"/><text x="0" y="5" fill="#121F45" text-anchor="middle">?</text></g>
</g></svg>"""

def serp():
    rows = ""
    for n, name in [("1", "Competitor A"), ("2", "Competitor B"), ("3", "Competitor C")]:
        rows += f'<li><span class="n">{n}</span><span><span class="nm">{name}</span><span class="bar"></span><span class="bar s"></span></span><span class="call">Call</span></li>'
    rows += '<li class="you"><span class="n">4</span><span><span class="nm">You?</span><span class="bar s"></span></span><span class="call">No call</span></li>'
    return f"""<figure class="serp-fig" style="margin:0">
 <div class="serp" role="img" aria-label="A mock Google Maps result for a trade near me. Three competitors fill the top three places. Your business is fourth, out of sight.">
  <div class="serp-q"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="7.5" cy="7.5" r="5.5" fill="none" stroke="#121F45" stroke-width="2"/><path d="M11.6 11.6 L16 16" stroke="#121F45" stroke-width="2"/></svg><span><span id="trade">plasterer</span> near me</span></div>
  <div class="serp-map">{MAP_SVG}</div>
  <ol>{rows}</ol>
 </div>
 <figcaption class="serp-note">Illustration. Most people ring one of the first three.</figcaption>
</figure>"""

def faq_html():
    return "".join(f"<details><summary>{html.escape(q)}</summary><p>{ph_text(a)}</p></details>" for q, a in FAQ)

def faq_schema():
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

SERVICES = [
    ("Get you found on Google Maps and in search.", "We set up and look after your Google listing, help you get more reviews, post every week and get you listed on the other directories that matter."),
    ("Fix your website so it brings in calls.", "Clear wording, a fast site, pages for your services and towns, and a call button on every page."),
    ("A simple website if you haven't got one.", "A Facebook page isn't enough. We build a straightforward site that does the job."),
]
JOBS = [
    ("Day 1", "We check where you show up today and who's ahead of you. You get a straight answer."),
    ("Week 1", "Your Google listing and website basics get sorted."),
    ("Monthly", "Weekly posts, photos, review replies, a check on where you rank and a one-page report so you can see it for yourself."),
]
TRADES = ["Plumbers", "Electricians", "Builders", "Plasterers", "Roofers", "Joiners and carpenters", "Heating engineers", "Painters and decorators", "Landscapers", "Tilers", "Kitchen and bathroom fitters", "Locksmiths"]

def rows_html(items):
    return '<ol class="rows">' + "".join(f'<li><span class="num" aria-hidden="true">{i}</span><h3>{h}</h3><p>{t}</p></li>' for i, (h, t) in enumerate(items, 1)) + "</ol>"

def sheet_html():
    lis = "".join(f'<li><span class="when">{w}</span><p>{t}</p></li>' for w, t in JOBS)
    return f'<div class="sheet"><div class="sheet-head"><span>Job sheet: how it works</span><span>TW | Results</span></div><ol>{lis}</ol><div class="sheet-foot">You answer the phone. We do the rest.</div></div>'

def ledger(num, label, inner, cls="sec"):
    return f'<section class="{cls}"><div class="wrap"><div class="ledger"><p class="tag"><b>{num}</b>{label}</p><div>{inner}</div></div></div></section>'

def ee_shot(date, depth=1):
    return f'<figure style="margin:0"><div class="ph-box shot">[EE SCREENSHOT {date}]<br>Google Maps results for &lsquo;embroidery Derby&rsquo;, dated</div><figcaption class="cap">Google Maps results for &lsquo;embroidery Derby&rsquo;, checked {date}.</figcaption></figure>'

# ---------------- Home ----------------
home = f"""
<section class="hero" aria-labelledby="h1">
 <div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
  <div class="hero-grid">
   <div>
    <h1 id="h1"><span>The top 3 on Google get over half the clicks.</span> <span>For your trade, in your area, that's your competitors.</span> <span class="fix">We fix that.</span></h1>
    <p class="sub">{SUBLINE}</p>
    {ctas(depth=0).replace('../','')}
    <p class="src">Source: Backlinko, 2025</p>
   </div>
   {serp()}
  </div>
 </div></div>
</section>
{ledger("01", "The problem", '<h2>Three names. One phone call.</h2><p class="statement">When someone needs a plasterer, they search, they look at the first three names, and they ring one. If you&rsquo;re not in those three, you don&rsquo;t get the call. It doesn&rsquo;t matter how good your work is.</p>')}
{ledger("02", "What we do", '<h2>Three things. Done properly.</h2>' + rows_html(SERVICES) + '<a class="more" href="what-we-do/">What we do, in full</a>', cls="sec pale")}
{ledger("03", "Who it&rsquo;s for", '<h2>Built for trades who are good at the job but hard to find.</h2><p class="lede">If you&rsquo;re a plumber, electrician or builder in Derby or anywhere in the East Midlands, and the work comes from word of mouth while the firm down the road gets the Google calls, this is for you.</p><ul class="trades">' + "".join(f"<li>{t}</li>" for t in TRADES) + '</ul>')}
{ledger("04", "How it works", '<h2>No mystery. Here&rsquo;s the job sheet.</h2>' + sheet_html(), cls="sec pale")}
<section class="sec navy on-navy" aria-labelledby="proof-h">
 <div class="wrap"><div class="ledger"><p class="tag"><b>05</b>Proof</p><div>
  <h2 id="proof-h">Proof, with dates.</h2>
  <div class="proof-grid">
   <div>
    <p class="big" aria-hidden="true">#2</p>
    <dl class="dates"><div><dt>Started tracking</dt><dd>10/09/2026: #2</dd></div><div><dt>Checked</dt><dd>07/10/2026: still #2</dd></div></dl>
    <p style="margin-top:1.5rem">We started with a business in our own group. Eaton Embroidery ranks #2 in the Google map results for &lsquo;Embroidery Derby&rsquo;. It was #2 when we started tracking on 10/09/2026 and still #2 on 07/10/2026. We&rsquo;re documenting the work as we go.</p>
    <a class="more" href="eaton-embroidery/">Read the case study</a>
   </div>
   {ee_shot("07/10/2026")}
  </div>
 </div></div></div>
</section>
{ledger("06", "Who you deal with", '<div class="person"><div class="ph-box head-ph">[HEADSHOT]<br>Dan, plain wall or outdoors</div><div><h2>No account managers. No call centre.</h2><p class="lede">You deal with me, Dan. No account managers, no call centre. If something won&rsquo;t work for your business, I&rsquo;ll tell you before you spend anything.</p><a class="more" href="about-dan/">About Dan</a></div></div>', cls="sec pale")}
{ledger("07", "Straight answers", '<h2>Questions trades ask us.</h2><div class="faq">' + faq_html() + '</div>')}
<section class="sec navy on-navy close" aria-labelledby="close-h">
 <div class="wrap"><h2 id="close-h">{CLOSE}</h2><p class="lede">Call Dan for a straight answer on where you stand on Google today.</p>{ctas(depth=0).replace('../','')}</div>
</section>
"""

# ---------------- What we do ----------------
svc_detail = [
    ("Get you found on Google Maps and in search.",
     "When someone types &lsquo;electrician near me&rsquo; or &lsquo;builder Derby&rsquo;, Google shows a map and three businesses. This is the work that gets you into that spot and keeps you there. It&rsquo;s what agencies call local SEO and Google Business Profile optimisation. We just call it getting you found.",
     ["Your Google listing set up properly: the right categories, services, service area, hours and photos", "Help getting more reviews from real customers, and replies to the ones you get", "A post on your listing every week", "Your business listed, with the same details, on the other directories that matter", "A check on where you rank, every month"],
     "Answer a few questions at the start, send us photos of your work when you have them, and ask happy customers for a review."),
    ("Fix your website so it brings in calls.",
     "Plenty of trade websites look fine but don&rsquo;t make the phone ring. They&rsquo;re slow, they don&rsquo;t say what you do or where, and the number&rsquo;s hard to find. We fix that, whoever built it.",
     ["Clear wording that says what you do and where you work", "A fast site that works on a phone", "Pages for your services and the towns you cover, so Google can match you to those searches", "A call button on every page", "The behind-the-scenes basics Google looks for"],
     "Tell us what work you want more of, and check the wording before it goes live."),
    ("A simple website if you haven&rsquo;t got one.",
     "A Facebook page isn&rsquo;t enough. Google needs a proper website to send people to, and customers want to see you&rsquo;re a real business. We build a straightforward site that does the job.",
     ["A clean, fast website for your trade, built to be found on Google", "Your services, the areas you cover, photos of your work and a call button", "A contact form that comes straight to your email", "Set up in your name, so you own it"],
     "Send us your logo if you have one, some photos and a list of your services."),
]
def svc_section(i, h, intro, gets, you):
    lis = "".join(f"<li>{g}</li>" for g in gets)
    return ledger(f"0{i}", "Service", f'<h2>{h}</h2><p class="lede">{intro}</p><h3 style="font-size:1.15rem;margin:2rem 0 .75rem">What you get</h3><ul class="plain">{lis}</ul><h3 style="font-size:1.15rem;margin:1.75rem 0 .75rem">What you do</h3><p>{you} That&rsquo;s it.</p>', cls="sec pale" if i % 2 == 0 else "sec")

wwd = f"""
<section class="hero page-hero"><div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
 <h1>What we do</h1>
 <p class="lede">Three things. Done properly. Explained in plain English.</p>
 <p>We work with plumbers, electricians, builders and other trades in Derby and across the East Midlands. We start by looking at where you stand, then tell you straight what&rsquo;s worth doing.</p>
</div></div></section>
{"".join(svc_section(i, *s) for i, s in enumerate(svc_detail, 1))}
{ledger("04", "How it works", '<h2>The job sheet.</h2>' + sheet_html(), cls="sec pale")}
<section class="sec navy on-navy close"><div class="wrap"><h2>Want to know where you stand? Call Dan.</h2>{ctas()}</div></section>
"""

# ---------------- Eaton Embroidery ----------------
ee = f"""
<section class="hero page-hero"><div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
 <h1>Eaton Embroidery: our first case study</h1>
 <p class="lede">Eaton Embroidery is a Derby embroidery business in the same group as TW Results. It&rsquo;s our first case study, and we&rsquo;re documenting it as we go, with dates, good or bad.</p>
</div></div></section>
<section class="sec navy on-navy"><div class="wrap"><div class="ledger"><p class="tag"><b>01</b>The fact</p><div><h2 class="vh">The fact</h2>
 <div class="proof-grid"><div>
  <p class="big" aria-hidden="true">#2</p>
  <p class="big-cap">#2 in the Google map results for &lsquo;Embroidery Derby&rsquo;.</p>
  <dl class="dates"><div><dt>Baseline</dt><dd>10/09/2026: #2</dd></div><div><dt>Checked</dt><dd>07/10/2026: still #2</dd></div></dl>
 </div><div><p class="lede">#2 in the Google map results for &lsquo;Embroidery Derby&rsquo;. Baseline 10/09/2026: #2. Checked 07/10/2026: still #2.</p><p>That&rsquo;s a position held, not a climb. Holding a top-three spot matters: it&rsquo;s where the calls come from. The job now is to keep it and to win more searches.</p></div></div>
</div></div></div></section>
{ledger("02", "Screenshots", '<h2>See it for yourself.</h2><p>Dated screenshots of the Google Maps results, taken on the days we checked.</p><div class="shots">' + ee_shot("10/09/2026") + ee_shot("07/10/2026") + '</div>')}
{ledger("03", "What we&rsquo;re working on", '<h2>The monthly work.</h2><ul class="plain"><li>Keeping the Google listing complete and up to date</li><li>A post on the listing every week</li><li>New photos of finished work</li><li>Replies to every review</li><li>Website fixes so the pages match what people search for</li><li>A monthly check on where the business ranks</li></ul>', cls="sec pale")}
{ledger("04", "Updates", '<h2>The log.</h2><p>New results get added here every month, good or bad.</p><ol class="log"><li><time datetime="2026-09-10">10/09/2026</time><p>Started tracking. #2 in the Google map results for &lsquo;Embroidery Derby&rsquo;.</p></li><li><time datetime="2026-10-07">07/10/2026</time><p>Checked again. Still #2 for &lsquo;Embroidery Derby&rsquo;.</p></li></ol>')}
<section class="sec navy on-navy close"><div class="wrap"><h2>{CLOSE}</h2>{ctas()}</div></section>
"""

# ---------------- About Dan ----------------
about = f"""
<section class="hero page-hero"><div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
 <div class="person about">
  <div class="ph-box head-ph">[HEADSHOT]<br>One photo of Dan. Plain wall or outdoors.</div>
  <div>
   <h1>About Dan</h1>
   <p class="lede">I&rsquo;m Dan Cooper. I run TW Results from Derby. I work with trade businesses that are good at the job but hard to find on Google. I keep it simple: find out what&rsquo;s wrong, fix it, show you the result.</p>
   <p><span class="ph">[DAN TO ADD 1 TO 2 LINES OF REAL BACKGROUND]</span></p>
   <p class="sig">Dan Cooper, TW Results</p>
   {ctas()}
  </div>
 </div>
</div></div></section>
{ledger("01", "How I work", '<h2>You deal with me. Every time.</h2><ul class="plain"><li>No account managers, no call centre.</li><li>If something won&rsquo;t work for your business, I&rsquo;ll tell you before you spend anything.</li><li>Every month you see what I did and where you stand, good or bad.</li></ul>')}
"""

# ---------------- Contact ----------------
contact = f"""
<section class="hero page-hero"><div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
 <div class="contact-grid">
  <div>
   <h1>Call Dan</h1>
   <a class="phone-big" href="{TEL}">{PHONE}</a>
   <p><a href="mailto:{EMAIL}" style="font-weight:700;font-size:1.2rem">{EMAIL}</a></p>
   <dl class="facts">
    <div><dt>Covering</dt><dd>Covering Derby and {TOWNS}.</dd></div>
    <div><dt>Meetings</dt><dd>By appointment. <span class="ph">[ADDRESS: Chellaston, Derby, by appointment, awaiting approval]</span></dd></div>
    <div><dt>Who you&rsquo;ll speak to</dt><dd>Dan. Every time.</dd></div>
   </dl>
  </div>
  <div id="message">
   <h2 style="font-size:clamp(1.5rem,2.6vw,2.1rem)">{CLOSE}</h2>
   <p>Send a message and Dan will get back to you.</p>
   <form id="enquiry" action="[FORM ENDPOINT]" method="POST" novalidate>
    <p class="hp" aria-hidden="true"><label for="website">Leave this empty</label><input id="website" name="website" tabindex="-1" autocomplete="off"></p>
    <input type="hidden" name="_subject" value="New enquiry from twresults.com">
    <div class="f"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required></div>
    <div class="f"><label for="business">Business and trade</label><input id="business" name="business" autocomplete="organization" required placeholder="e.g. Smith Plastering, plasterer"></div>
    <div class="f"><label for="phone">Phone</label><input id="phone" name="phone" type="tel" autocomplete="tel" required></div>
    <div class="f"><label for="town">Town</label><input id="town" name="town" autocomplete="address-level2" required></div>
    <div class="f"><label for="problem">What&rsquo;s not working? <span class="opt">(optional)</span></label><textarea id="problem" name="problem"></textarea></div>
    <p class="consent">By sending this you agree we can use these details to reply to you. See our <a href="../privacy/">privacy notice</a>.</p>
    <button class="btn btn-p" type="submit">Send to Dan</button>
    <p class="form-msg" id="form-msg" role="status" tabindex="-1"></p>
   </form>
  </div>
 </div>
</div></div></section>
"""

# ---------------- Privacy ----------------
privacy = f"""
<section class="sec"><div class="wrap"><div class="prose">
 <h1 style="font-size:clamp(2.2rem,4vw,3.2rem);margin-bottom:1rem">Privacy</h1>
 <p class="lede">Plain English: what we collect, why, and how to get it deleted.</p>
 <p><span class="ph">[DRAFT: Dan to approve]</span> Last updated <span class="ph">[DATE OF APPROVAL]</span>.</p>
 <h2>Who we are</h2><p>TW Results is run by Daniel Cooper, trading as TW Results, based in Derby. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
 <h2>What the contact form collects</h2><p>Your name, your business and trade, your phone number, your town and anything you write in the message box. We use it only to reply to you and, if you become a client, to do the work you&rsquo;ve asked for. We don&rsquo;t sell it or pass it on for marketing.</p>
 <h2>Who processes it</h2><p>The form is sent through <span class="ph">[FORM SERVICE: Formspree or Web3Forms]</span>, which passes it to our email. Our email runs on Google Workspace.</p>
 <h2>Analytics</h2><p>If you click Accept on the cookie bar, we use Google Analytics 4 to see how many people visit and which pages they use. It doesn&rsquo;t load unless you accept. If you click Reject, nothing is set. You can change your mind by clearing this site&rsquo;s data in your browser.</p>
 <h2>How long we keep it</h2><p>Enquiries that don&rsquo;t turn into work are deleted after <span class="ph">[RETENTION PERIOD: Dan to confirm]</span>. Client records are kept for as long as the law requires for tax and accounts.</p>
 <h2>Your rights</h2><p>You can ask to see the details we hold about you, ask us to correct them or ask us to delete them. Email <a href="mailto:{EMAIL}">{EMAIL}</a>. If you&rsquo;re unhappy with how we&rsquo;ve handled your data, you can complain to the Information Commissioner&rsquo;s Office at <a href="https://ico.org.uk">ico.org.uk</a>.</p>
</div></div></section>
"""

notfound = f"""
<section class="hero page-hero"><div class="wrap"><div class="card"><span class="c3"></span><span class="c4"></span>
 <h1>That page doesn&rsquo;t exist.</h1>
 <p class="lede">It may have moved, or the link was wrong.</p>
 <div class="btns"><a class="btn btn-p" href="{TEL}">Call Dan</a><a class="btn btn-s" href="./">Go to the home page</a></div>
</div></div></section>
"""

PAGES = [
    ("", "index.html", 0, "Get found on Google. Get more work. | TW Results, Derby",
     "Plumbers, electricians, builders and other trades in Derby and the East Midlands: we get you found on Google Maps and in search, and build websites that bring in calls. Talk to Dan.",
     home, [org_schema(), faq_schema()], None),
    ("what-we-do/", "what-we-do/index.html", 1, "Google Maps, local SEO and websites for trades | TW Results, Derby",
     "Local SEO and Google Business Profile work for tradespeople in Derby and the East Midlands, plus website fixes and simple websites that bring in calls. Plain English, no jargon.",
     wwd, [org_schema()], "what-we-do/"),
    ("eaton-embroidery/", "eaton-embroidery/index.html", 1, "Eaton Embroidery case study: #2 on Google Maps in Derby | TW Results",
     "Our first case study: Eaton Embroidery, #2 in the Google map results for 'Embroidery Derby' on 10/09/2026 and still #2 on 07/10/2026. Documented as we go.",
     ee, None, "eaton-embroidery/"),
    ("about-dan/", "about-dan/index.html", 1, "About Dan Cooper | TW Results, Derby",
     "Dan Cooper runs TW Results from Derby, helping trade businesses that are good at the job but hard to find on Google. You deal with Dan, every time.",
     about, None, "about-dan/"),
    ("contact/", "contact/index.html", 1, "Call Dan | TW Results, Derby",
     "Call Dan or send a message. TW Results helps trades across Derby and the East Midlands get found on Google and get more work.",
     contact, None, "contact/"),
    ("privacy/", "privacy/index.html", 1, "Privacy | TW Results",
     "How TW Results handles the details you send through the contact form, and how analytics cookies are used.",
     privacy, None, None),
    ("404.html", "404.html", 0, "Page not found | TW Results",
     "That page doesn't exist. Go to the TW Results home page or call Dan.", notfound, None, None),
]

for slug, out, depth, title, desc, body, schema, cur in PAGES:
    if depth == 1:
        body = body.replace('href="what-we-do/"', 'href="../what-we-do/"').replace('href="eaton-embroidery/"', 'href="../eaton-embroidery/"').replace('href="about-dan/"', 'href="../about-dan/"')
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page(slug, title, desc, body, schema, depth, cur, og_title=(SUBLINE + " | TW Results") if slug == "" else None))

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
