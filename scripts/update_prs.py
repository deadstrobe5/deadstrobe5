"""Rewrites the merged-PR table in README.md from the GitHub search API."""
import json, os, re, subprocess

USER = "deadstrobe5"
SKIP_OWNERS = {USER.lower(), "tribalkit"}

def gh(*args):
    return json.loads(subprocess.check_output(["gh", *args], text=True))

prs = gh("search", "prs", "--author", USER, "--merged", "--limit", "200",
         "--json", "repository,number,title,url,closedAt")
rows, stars = [], {}
for pr in prs:
    repo = pr["repository"]["nameWithOwner"]
    if repo.split("/")[0].lower() in SKIP_OWNERS:
        continue
    if repo not in stars:
        stars[repo] = gh("api", f"repos/{repo}")["stargazers_count"]
    rows.append((stars[repo], repo, pr))

rows.sort(key=lambda r: (-r[0], r[2]["closedAt"]))
lines = ["| Project | ★ | Change |", "|---|---:|---|"]
for st, repo, pr in rows:
    title = pr["title"].replace("|", "\\|").lstrip("⚡ ").strip()
    lines.append(f"| [{repo}](https://github.com/{repo}) | {st:,} | [{title}]({pr['url']}) |")
table = "\n".join(lines) if rows else "_None yet._"

path = "README.md"
text = open(path).read()
new = re.sub(r"(<!-- PRS:START -->).*?(<!-- PRS:END -->)",
             lambda m: f"{m.group(1)}\n{table}\n{m.group(2)}", text, flags=re.S)
if new != text:
    open(path, "w").write(new)
