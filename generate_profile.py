#!/usr/bin/env python3
"""Tamagotchi-style GitHub Profile Card Generator"""

import os, sys, requests
from datetime import datetime, timezone, timedelta

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Pixel art pet  (10 wide × 8 tall)
# 0=transparent  1=body(green)  2=eye(dark)
PET = [
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 2, 2, 1, 2, 2, 1, 0],
    [0, 1, 1, 2, 2, 1, 2, 2, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 2, 1, 2, 2, 1, 2, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
]


def query(q, variables=None):
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": q, "variables": variables or {}},
        headers={"Authorization": f"bearer {TOKEN}"},
        timeout=30,
    )
    if resp.status_code != 200:
        return None
    return resp.json().get("data")


def fetch_stats():
    q = """
    query($login: String!) {
      user(login: $login) {
        name login createdAt
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
        contributionsCollection {
          totalCommitContributions
          contributionCalendar {
            weeks { contributionDays { contributionCount date } }
          }
        }
      }
    }
    """
    data = query(q, {"login": USERNAME})
    if not data or not data.get("user"):
        return _default()

    u = data["user"]

    # streak
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
              for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"], reverse=True)
    streak, today = 0, datetime.now(timezone.utc).date()
    for day in days:
        expected = today - timedelta(days=streak)
        d = datetime.fromisoformat(day["date"]).date()
        if d == expected and day["contributionCount"] > 0:
            streak += 1
        elif d < expected:
            break

    # languages
    lang_data = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo.get("stargazerCount", 0)
        for edge in (repo.get("languages") or {}).get("edges") or []:
            n, c, s = edge["node"]["name"], edge["node"].get("color") or "#888", edge["size"]
            if n not in lang_data:
                lang_data[n] = {"size": 0, "color": c}
            lang_data[n]["size"] += s

    total_sz = sum(v["size"] for v in lang_data.values())
    langs = sorted(lang_data.items(), key=lambda x: x[1]["size"], reverse=True)[:5]
    langs = [(n, i["color"], i["size"] / total_sz * 100) for n, i in langs] if total_sz else []

    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    years = (datetime.now(timezone.utc) - created).days // 365

    return {
        "commits": u["contributionsCollection"]["totalCommitContributions"],
        "streak": streak,
        "followers": u["followers"]["totalCount"],
        "stars": stars,
        "repos": u["repositories"]["totalCount"],
        "years": years,
        "langs": langs,
    }


def _default():
    return {"commits": 0, "streak": 0, "followers": 0, "stars": 0, "repos": 0, "years": 0, "langs": []}


def render_pet(bx, by, ps=9):
    parts = []
    for ry, row in enumerate(PET):
        for cx, cell in enumerate(row):
            if cell == 0:
                continue
            color = "#39d353" if cell == 1 else "#0d1117"
            x, y = bx + cx * ps, by + ry * ps
            parts.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{color}"/>')
    return "\n  ".join(parts)


def render_langs(langs, x, y):
    if not langs:
        return f'<text x="{x}" y="{y+10}" font-family="monospace" font-size="8" fill="#484f58" opacity="0.5">[ add METRICS_TOKEN secret for language data ]</text>'
    parts = []
    for i, (name, color, pct) in enumerate(langs[:4]):
        ly = y + i * 16
        bw = int(pct * 1.5)
        parts.append(
            f'<text x="{x}" y="{ly+9}" font-family="monospace" font-size="8" fill="#6e7681">{name[:12]}</text>'
            f'\n  <rect x="{x+105}" y="{ly}" width="150" height="8" fill="#21262d" rx="3"/>'
            f'\n  <rect x="{x+105}" y="{ly}" width="{bw}" height="8" fill="{color}" rx="3"/>'
            f'\n  <text x="{x+260}" y="{ly+9}" font-family="monospace" font-size="8" fill="#6e7681">{pct:.1f}%</text>'
        )
    return "\n  ".join(parts)


def generate_svg(s):
    W, H = 480, 280
    commits, streak, followers = s["commits"], s["streak"], s["followers"]
    stars, repos, years, langs = s["stars"], s["repos"], s["years"], s["langs"]

    hp_w = int(min(commits / max(commits, 1000), 1.0) * 140)
    pet = render_pet(46, 52, ps=9)
    lang_bars = render_langs(langs, 240, 182)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>@import url('https://fonts.googleapis.com/css2?family=VT323&amp;display=swap');</style>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="clip"><rect x="18" y="18" width="444" height="240" rx="6"/></clipPath>
  </defs>

  <!-- shell -->
  <rect width="{W}" height="{H}" fill="#0d1117" rx="12"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#21262d" stroke-width="1.5" rx="11.5"/>

  <!-- screen -->
  <rect x="18" y="18" width="444" height="240" fill="#010409" rx="6"/>
  <rect x="18" y="18" width="444" height="240" fill="none" stroke="#1f6feb" stroke-width="0.8" rx="6" opacity="0.4"/>

  <!-- title bar -->
  <rect x="18" y="18" width="444" height="24" fill="#161b22" rx="6"/>
  <rect x="18" y="34" width="444" height="8" fill="#161b22"/>
  <circle cx="34" cy="30" r="4.5" fill="#ff5f57"/>
  <circle cx="50" cy="30" r="4.5" fill="#febc2e"/>
  <circle cx="66" cy="30" r="4.5" fill="#28c840"/>
  <text x="240" y="34" font-family="monospace" font-size="10" fill="#484f58" text-anchor="middle">bigmacfive — profile.sh</text>

  <!-- pixel pet -->
  {pet}

  <!-- pet level -->
  <text x="91" y="148" font-family="monospace" font-size="8" fill="#39d353" text-anchor="middle" filter="url(#glow)">&#9670; LV.{years} &#9670;</text>

  <!-- HP bar -->
  <text x="46" y="164" font-family="monospace" font-size="8" fill="#39d353">HP</text>
  <rect x="63" y="155" width="140" height="8" fill="#21262d" rx="3"/>
  <rect x="63" y="155" width="{hp_w}" height="8" fill="#39d353" rx="3" filter="url(#glow)"/>

  <!-- divider -->
  <line x1="218" y1="44" x2="218" y2="250" stroke="#21262d" stroke-width="1"/>

  <!-- stats -->
  <text x="236" y="58" font-family="monospace" font-size="10" fill="#39d353" filter="url(#glow)">$ cat stats</text>
  <text x="236" y="78"  font-family="monospace" font-size="9" fill="#6e7681">commits  <tspan fill="#e6edf3">{commits}</tspan></text>
  <text x="236" y="95"  font-family="monospace" font-size="9" fill="#6e7681">streak   <tspan fill="#e6edf3">{streak}d</tspan></text>
  <text x="236" y="112" font-family="monospace" font-size="9" fill="#6e7681">followers<tspan fill="#e6edf3"> {followers}</tspan></text>
  <text x="236" y="129" font-family="monospace" font-size="9" fill="#6e7681">stars    <tspan fill="#e6edf3"> {stars}</tspan></text>
  <text x="236" y="146" font-family="monospace" font-size="9" fill="#6e7681">repos    <tspan fill="#e6edf3"> {repos}</tspan></text>
  <text x="236" y="163" font-family="monospace" font-size="9" fill="#6e7681">joined   <tspan fill="#e6edf3"> {years}yr ago</tspan></text>

  <!-- lang header -->
  <line x1="236" y1="173" x2="460" y2="173" stroke="#21262d" stroke-width="1"/>
  <text x="236" y="182" font-family="monospace" font-size="10" fill="#39d353" filter="url(#glow)">$ cat langs</text>

  <!-- language bars -->
  {lang_bars}

  <!-- horizontal divider above footer -->
  <line x1="18" y1="258" x2="462" y2="258" stroke="#21262d" stroke-width="1"/>

  <!-- cursor blink -->
  <rect x="448" y="243" width="5" height="9" fill="#39d353">
    <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/>
  </rect>

  <!-- footer buttons (Tamagotchi) -->
  <circle cx="140" cy="270" r="7" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="140" y="274" font-family="monospace" font-size="7" fill="#484f58" text-anchor="middle">A</text>
  <circle cx="240" cy="270" r="7" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="240" y="274" font-family="monospace" font-size="7" fill="#484f58" text-anchor="middle">B</text>
  <circle cx="340" cy="270" r="7" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="340" y="274" font-family="monospace" font-size="7" fill="#484f58" text-anchor="middle">C</text>

  <!-- timestamp -->
  <text x="459" y="277" font-family="monospace" font-size="7" fill="#21262d" text-anchor="end">updated {today}</text>
</svg>"""


def main():
    print(f"Fetching stats for {USERNAME}...")
    stats = fetch_stats()
    print(f"Stats fetched: commits={stats['commits']}, streak={stats['streak']}, langs={len(stats['langs'])}")
    svg = generate_svg(stats)
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated profile.svg")


if __name__ == "__main__":
    main()
