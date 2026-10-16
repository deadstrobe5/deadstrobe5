"""Builds card.svg with live numbers from the GitHub API."""
import json, subprocess

USER = "deadstrobe5"
MIN_STARS = 50  # skip uni group projects and toy repos
MINE = {USER.lower(), "tribalkit"}

def gh(*a):
    return json.loads(subprocess.check_output(["gh", *a], text=True))

merged = gh("search", "prs", "--author", USER, "--merged", "--limit", "500", "--json", "repository")
ext = [p["repository"]["nameWithOwner"] for p in merged
       if p["repository"]["nameWithOwner"].split("/")[0].lower() not in MINE]
star = {r: gh("api", f"repos/{r}")["stargazers_count"] for r in set(ext)}
ext = [r for r in ext if star[r] >= MIN_STARS]
repos = sorted(set(ext))
stars = sum(star[r] for r in repos)
q = """query($u:String!){user(login:$u){contributionsCollection{
  totalCommitContributions restrictedContributionsCount totalPullRequestContributions}}}"""
c = gh("api", "graphql", "-f", f"query={q}", "-F", f"u={USER}")["data"]["user"]["contributionsCollection"]
commits = c["totalCommitContributions"] + c["restrictedContributionsCount"]

stats = [
    ("PRs merged into other people's repos", f"{len(ext)}"),
    ("Projects contributed to", f"{len(repos)}"),
    ("Combined ★ of those projects", f"{stars:,}"),
    ("Contributions in the last year", f"{commits:,}"),
    ("Total PRs opened in the last year", f"{c['totalPullRequestContributions']:,}"),
]
h = 60 + 30 * len(stats)
rows = "".join(
    f'<text x="25" y="{75 + 30*i}" class="l">{k}</text>'
    f'<text x="425" y="{75 + 30*i}" class="v" text-anchor="end">{v}</text>'
    for i, (k, v) in enumerate(stats))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="{h}" viewBox="0 0 450 {h}">
<style>.t{{font:600 17px 'Segoe UI',Ubuntu,sans-serif;fill:#58a6ff}}.l{{font:400 14px 'Segoe UI',Ubuntu,sans-serif;fill:#c9d1d9}}.v{{font:700 14px 'Segoe UI',Ubuntu,sans-serif;fill:#f0f6fc}}</style>
<rect x="0.5" y="0.5" width="449" height="{h-1}" rx="6" fill="#0d1117" stroke="#30363d"/>
<text x="25" y="38" class="t">What the token predictor has been up to</text>{rows}
</svg>'''
open("card.svg", "w").write(svg)
print(stats)
