"""UK GDPR privacy notice: single source for the privacy page (HTML) and the Markdown draft.
Each section is (heading, [blocks]); a block is a string (paragraph) or a list (bullets).
Inline markup: **bold** and [link text](url). Placeholders in [CAPS] are shown as visible markers."""

EMAIL = "dan@twresults.com"
INTRO = "[DRAFT: Dan to approve] Last updated [DATE OF APPROVAL]."
LEDE = "This notice explains what personal data I collect through this website and when you contact me, why, and what your rights are."

SECTIONS = [
    ("Who I am", [
        "Daniel Cooper trading as TW Results (&ldquo;TW Results&rdquo;, &ldquo;I&rdquo;, &ldquo;me&rdquo;) is the controller of your personal data.",
        ["Address: Derby, by appointment",
         f"Email: [{EMAIL}](mailto:{EMAIL})",
         "{ICO_LINE}"],
    ]),
    ("What I collect", [
        ["**The enquiry form:** your name, your trade or business, your phone number or email address, and your message (optional).",
         "If you contact me, I only keep your details and message so I can reply to you.",
         "**If you become a client:** the details I need to do the work and invoice you.",
         "**Analytics:** how the site is used (pages visited, rough location, device type), but only if you click Accept on the cookie bar. See Cookies below.",
         "**Website hosting:** the host keeps server logs, which include your IP address, when you visit."],
        "I don&rsquo;t sell your details, add you to marketing lists or make automated decisions about you.",
    ]),
    ("Why I use it, and the lawful basis", [
        ["**Replying to your enquiry and running your free Google check:** legitimate interests (answering a business enquiry you sent me), or steps you&rsquo;ve asked me to take before entering into a contract.",
         "**Doing the work if you become a client:** contract.",
         "**Keeping business and tax records:** legal obligation.",
         "**Counting visits with Google Analytics:** consent. You can withdraw it at any time (see Cookies)."],
    ]),
    ("Who processes it for me", [
        "These companies process data on my behalf, under their data processing terms:",
        ["**Formspree** (handles the enquiry form and sends it to my email). Formspree is based in the United States, so your form details are transferred there. Formspree says it relies on Standard Contractual Clauses (SCCs) for these transfers. [LEGAL CHECK: transfer safeguard per Formspree DPA, checked 20/10/2026]",
         "**Google Workspace** (my email). Data may be processed outside the UK. Google uses the UK Extension to the EU-US Data Privacy Framework and standard contractual clauses.",
         "**Google Analytics 4** (visit statistics, only after you click Accept). Google Analytics 4 doesn&rsquo;t log or store IP addresses; it uses them briefly to work out a rough location and then discards them. The same Google transfer safeguards apply.",
         "**GitHub Pages** (website hosting, GitHub Inc., United States). GitHub keeps server logs, including visitors&rsquo; IP addresses, for security. GitHub uses the UK Extension to the EU-US Data Privacy Framework and standard contractual clauses."],
    ]),
    ("How long I keep it", [
        ["**Enquiries that don&rsquo;t lead to work:** 12 months, then deleted.",
         "**Client records:** 6 years from the end of the tax year they relate to, as HMRC requires.",
         "**Analytics data:** 14 months.",
         "**Server logs:** kept by GitHub under its own policy."],
    ]),
    ("Cookies", [
        "The site sets no cookies unless you click Accept on the cookie bar. If you do, Google Analytics 4 sets the cookies <code>_ga</code> and <code>_ga_&lt;ID&gt;</code>, which last up to 2 years, to count visits. If you click Reject, Google Analytics doesn&rsquo;t load.",
        "Your choice is saved in your browser&rsquo;s local storage (not a cookie) so the bar doesn&rsquo;t keep coming back. To change it, use the button below or clear this site&rsquo;s data in your browser.",
        "{COOKIE_BUTTON}",
    ]),
    ("Your rights", [
        "You have the right to:",
        ["see the personal data I hold about you",
         "have it corrected if it&rsquo;s wrong",
         "have it deleted",
         "restrict how I use it",
         "object to how I use it, including where I rely on legitimate interests",
         "have it sent to you or another organisation, where I rely on consent or a contract",
         "withdraw consent at any time, where I rely on consent"],
        f"To use any of these rights, email [{EMAIL}](mailto:{EMAIL}). I&rsquo;ll reply within one month.",
        "If you&rsquo;re unhappy with how I&rsquo;ve handled your data, you can complain to the Information Commissioner&rsquo;s Office at [ico.org.uk](https://ico.org.uk) or on 0303 123 1113. I&rsquo;d appreciate the chance to put it right first, so please contact me before you go to the ICO.",
    ]),
    ("Changes to this notice", [
        "If anything changes, I&rsquo;ll update this page. The date shows the latest version. Last updated [DATE OF APPROVAL].",
    ]),
]

import re, html as _h

def _inline_html(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return re.sub(r"(\[[A-Z][^\]]*\])", r'<span class="ph">\1</span>', t)

def _ico_line(ico):
    """ico: None = hide the line (e.g. exempt); "pending" = visible [ICO REG NO: pending]; anything else = the number."""
    if ico is None: return None
    return "ICO registration number: " + ("[ICO REG NO: pending]" if ico == "pending" else ico)

def _sections(ico):
    out = []
    for h, blocks in SECTIONS:
        nb = []
        for b in blocks:
            if isinstance(b, list):
                b = [(_ico_line(ico) if x == "{ICO_LINE}" else x) for x in b]
                b = [x for x in b if x is not None]
            nb.append(b)
        out.append((h, nb))
    return out

def to_html(cookie_button, ico="pending"):
    out = [f'<p>{_inline_html(INTRO)}</p>', f'<p class="lede">{LEDE}</p>']
    for h, blocks in _sections(ico):
        out.append(f"<h2>{h}</h2>")
        for b in blocks:
            if isinstance(b, list):
                out.append("<ul>" + "".join(f"<li>{_inline_html(x)}</li>" for x in b) + "</ul>")
            elif b == "{COOKIE_BUTTON}":
                out.append(cookie_button)
            else:
                out.append(f"<p>{_inline_html(b)}</p>")
    return "\n ".join(out)

def to_markdown(ico="pending"):
    def md(t):
        t = _h.unescape(re.sub(r"</?code>", "`", t))
        return t
    out = ["# Privacy notice: TW Results (DRAFT)", "", md(INTRO), "", md(LEDE), ""]
    for h, blocks in _sections(ico):
        out += [f"## {h}", ""]
        for b in blocks:
            if isinstance(b, list):
                out += [f"- {md(x)}" for x in b] + [""]
            elif b == "{COOKIE_BUTTON}":
                out += ["(On the website: a \"Change my cookie choice\" button.)", ""]
            else:
                out += [md(b), ""]
    return "\n".join(out)
