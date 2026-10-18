"""Word counts per page. 'main' = all text in <main>. 'visible' = main minus collapsed FAQ answers and [PLACEHOLDER] / photo-placeholder text."""
import re, html, os
PAGES = ["index.html", "what-we-do/index.html", "results/index.html", "about-dan/index.html", "contact/index.html", "privacy/index.html", "404.html"]
def words(t): return len(re.findall(r"[A-Za-z0-9£#][^\s]*", html.unescape(re.sub(r"<[^>]+>", " ", t))))
for f in PAGES:
    if not os.path.exists(f): continue
    s = open(f).read(); m = re.search(r"<main[^>]*>(.*)</main>", s, re.S).group(1)
    m = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", "", m, flags=re.S)
    v = re.sub(r"(</summary>).*?(</details>)", r"\1\2", m, flags=re.S)
    v = re.sub(r'<figure class="photo.*?</figure>|<div class="photo.*?</div>|<span class="ph">.*?</span>', "", v, flags=re.S)
    print(f"{f}\tmain {words(m)}\tvisible {words(v)}")
