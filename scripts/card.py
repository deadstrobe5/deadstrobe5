"""Builds card.svg from the live numbers on afonso-ribeiro.pages.dev."""
import re, urllib.request

SITE = "https://afonso-ribeiro.pages.dev"
req = urllib.request.Request(SITE, headers={"User-Agent": "Mozilla/5.0 (profile-card)"})
html = urllib.request.urlopen(req, timeout=30).read().decode()
n = [int(x) for x in re.findall(r'data-count="(\d+)"', html)]
# Order on the site: tokens (avg, max, year), $ (avg, max, year), commits (avg, max, year)
tok, usd, com = n[0:3], n[3:6], n[6:9]

def short(v):
    for d, s in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if v >= d:
            return f"{v / d:.1f}".rstrip("0").rstrip(".") + s
    return str(v)

stats = [
    ("Tokens burned per year", short(tok[2])),
    ("Tokens burned on the worst day", short(tok[1])),
    ("Same thing at API prices, per year", f"${usd[2]:,}"),
    ("Commits per year", f"{com[2]:,}"),
    ("Most commits in one day", f"{com[1]:,}"),
]
h = 60 + 30 * len(stats)
rows = "".join(
    f'<text x="25" y="{75 + 30*i}" class="l">{k}</text>'
    f'<text x="425" y="{75 + 30*i}" class="v" text-anchor="end">{v}</text>'
    for i, (k, v) in enumerate(stats))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="{h}" viewBox="0 0 450 {h}">
<style>.t{{font:600 17px 'Segoe UI',Ubuntu,sans-serif;fill:#d97757}}.l{{font:400 14px 'Segoe UI',Ubuntu,sans-serif;fill:#c9d1d9}}.v{{font:700 14px 'Segoe UI',Ubuntu,sans-serif;fill:#f0f6fc}}</style>
<rect x="0.5" y="0.5" width="449" height="{h-1}" rx="6" fill="#0d1117" stroke="#30363d"/>
<text x="25" y="38" class="t">What the token predictor has been up to</text>{rows}
</svg>'''
open("card.svg", "w").write(svg)
print(stats)
