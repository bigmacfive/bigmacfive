#!/usr/bin/env python3
"""Tamagotchi-style GitHub Profile Dashboard Generator v2

Generates an animated profile.svg with:
- Pixel art pet (bouncing + blinking)
- Stats panel
- Contribution heatmap (real data)
- Recent commit log (staggered fade-in)
- Language bars
- CRT scan line effect
"""

import os, requests
from datetime import datetime, timezone, timedelta
from html import escape as esc

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
W, H = 800, 430

# ── Pixel Art Pet (12×9)  0=clear 1=body 2=eye 3=highlight ──
PET = [
    [0,0,0,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,1,0,0],
    [0,1,1,2,2,1,1,2,2,1,1,0],
    [0,1,1,3,2,1,1,3,2,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,2,1,2,2,2,2,1,2,1,0],
    [0,0,1,1,1,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,1,1,1,0,0],
    [0,0,1,0,0,1,1,0,0,1,0,0],
]

C = {  # color palette
    "body": "#39d353", "hi": "#7ee787", "dark": "#0d1117",
    "bg": "#0d1117", "srf": "#010409", "bdr": "#21262d",
    "accent": "#1f6feb", "green": "#39d353", "orange": "#f78166",
    "txt": "#e6edf3", "dim": "#6e7681", "tbar": "#161b22",
}


# ══════════════════════════ DATA FETCHING ══════════════════════════

def gql(query, variables=None):
    r = requests.post("https://api.github.com/graphql",
                      json={"query": query, "variables": variables or {}},
                      headers={"Authorization": f"bearer {TOKEN}"}, timeout=30)
    return r.json().get("data") if r.ok else None


def fetch_stats():
    data = gql("""
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
    }""", {"login": USERNAME})

    if not data or not data.get("user"):
        return _empty()
    u = data["user"]
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]

    # streak
    days = sorted(
        [d for w in cal["weeks"] for d in w["contributionDays"]],
        key=lambda d: d["date"], reverse=True)
    streak, today = 0, datetime.now(timezone.utc).date()
    for day in days:
        exp = today - timedelta(days=streak)
        if datetime.fromisoformat(day["date"]).date() == exp and day["contributionCount"] > 0:
            streak += 1
        elif datetime.fromisoformat(day["date"]).date() < exp:
            break

    # languages
    ld, stars = {}, 0
    for repo in u["repositories"]["nodes"]:
        stars += repo.get("stargazerCount", 0)
        for e in (repo.get("languages") or {}).get("edges") or []:
            n, c, s = e["node"]["name"], e["node"].get("color") or "#888", e["size"]
            ld.setdefault(n, {"s": 0, "c": c})["s"] += s
    ts = sum(v["s"] for v in ld.values())
    langs = [(n, i["c"], i["s"]/ts*100) for n, i in
             sorted(ld.items(), key=lambda x: x[1]["s"], reverse=True)[:6]] if ts else []

    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    years = (datetime.now(timezone.utc) - created).days // 365

    return {"commits": cc["totalCommitContributions"], "streak": streak,
            "followers": u["followers"]["totalCount"], "stars": stars,
            "repos": u["repositories"]["totalCount"], "years": years,
            "langs": langs, "weeks": cal["weeks"]}


def _empty():
    return {"commits": 0, "streak": 0, "followers": 0, "stars": 0,
            "repos": 0, "years": 0, "langs": [], "weeks": []}


def fetch_events():
    r = requests.get(f"https://api.github.com/users/{USERNAME}/events/public",
                     headers={"Authorization": f"token {TOKEN}"},
                     params={"per_page": 30}, timeout=30)
    if not r.ok:
        return []
    commits, seen = [], set()
    for ev in r.json():
        if ev.get("type") != "PushEvent":
            continue
        dt = datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
        repo = ev["repo"]["name"].split("/")[-1]
        for c in ev.get("payload", {}).get("commits", []):
            sha = c["sha"][:7]
            if sha not in seen:
                seen.add(sha)
                commits.append({"sha": sha, "msg": c["message"].split("\n")[0],
                                "date": dt, "repo": repo})
    return commits[:5]


def reltime(dt):
    d = (datetime.now(timezone.utc) - dt).days
    if d == 0: return "today"
    if d < 7: return f"{d}d ago"
    if d < 30: return f"{d//7}w ago"
    return f"{d//30}mo ago"


# ══════════════════════════ SVG RENDERERS ══════════════════════════

def svg_pet(bx, by, ps=8):
    px = []
    for ry, row in enumerate(PET):
        for cx, cell in enumerate(row):
            if cell == 0: continue
            x, y = bx + cx * ps, by + ry * ps
            if cell == 1:
                px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{C["body"]}"/>')
            elif cell == 2:
                px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{C["dark"]}" class="eye"/>')
            elif cell == 3:
                px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{C["hi"]}" class="eye"/>')
    return "\n      ".join(px)


def heatmap_color(n):
    if n == 0: return "#161b22"
    if n <= 2: return "#0e4429"
    if n <= 5: return "#006d32"
    if n <= 9: return "#26a641"
    return "#39d353"


def svg_heatmap(weeks, bx, by, cs=8, gap=2):
    recent = weeks[-18:] if weeks else []
    rects = []
    for wi, wk in enumerate(recent):
        for di, day in enumerate(wk["contributionDays"]):
            x = bx + wi * (cs + gap)
            y = by + di * (cs + gap)
            col = heatmap_color(day["contributionCount"])
            rects.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'fill="{col}" rx="1.5"/>')
    return "\n      ".join(rects)


def svg_commits(events, x, y):
    if not events:
        return (f'<text x="{x}" y="{y+14}" font-family="\'Courier New\', monospace" '
                f'font-size="9" fill="{C["dim"]}" opacity="0.4">'
                f'[ no recent public commits ]</text>')
    rows = []
    for i, ev in enumerate(events):
        ly = y + i * 22
        sha = ev["sha"]
        msg = esc(ev["msg"][:44])
        t = reltime(ev["date"])
        repo = esc(ev["repo"][:14])
        rows.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{0.3 + i*0.15:.2f}s" fill="freeze"/>'
            f'<rect x="{x-4}" y="{ly}" width="740" height="18" fill="{C["tbar"]}" rx="3" opacity="0.3"/>'
            f'<text x="{x}" y="{ly+13}" font-family="\'Courier New\', monospace" font-size="9">'
            f'<tspan fill="{C["orange"]}">{sha}</tspan>'
            f'<tspan fill="{C["dim"]}">  {repo:14s} </tspan>'
            f'<tspan fill="{C["txt"]}">{msg}</tspan>'
            f'</text>'
            f'<text x="760" y="{ly+13}" font-family="\'Courier New\', monospace" '
            f'font-size="8" fill="{C["dim"]}" text-anchor="end">{t}</text>'
            f'</g>')
    return "\n      ".join(rows)


def svg_langs(langs, x, y):
    if not langs:
        return (f'<text x="{x}" y="{y+10}" font-family="\'Courier New\', monospace" '
                f'font-size="8" fill="{C["dim"]}" opacity="0.4">'
                f'[ add METRICS_TOKEN for private repo data ]</text>')
    bars = []
    for i, (name, color, pct) in enumerate(langs[:6]):
        col = i // 3
        row = i % 3
        lx = x + col * 370
        ly = y + row * 18
        bw = max(int(pct * 1.3), 2)
        bars.append(
            f'<text x="{lx}" y="{ly+10}" font-family="\'Courier New\', monospace" '
            f'font-size="8" fill="{C["dim"]}">{name[:12]}</text>'
            f'\n      <rect x="{lx+100}" y="{ly+1}" width="130" height="8" fill="#21262d" rx="3"/>'
            f'\n      <rect x="{lx+100}" y="{ly+1}" width="{bw}" height="8" fill="{color}" rx="3"/>'
            f'\n      <text x="{lx+236}" y="{ly+10}" font-family="\'Courier New\', monospace" '
            f'font-size="8" fill="{C["dim"]}">{pct:.1f}%</text>')
    return "\n      ".join(bars)


# ══════════════════════════ MAIN SVG ASSEMBLY ══════════════════════════

def generate_svg(stats, events):
    commits = stats["commits"]
    hp_w = int(min(commits / max(commits, 1000), 1.0) * 110)
    xp_w = int(min(stats["streak"] / 30, 1.0) * 110)
    pet = svg_pet(40, 58, ps=8)
    heatmap = svg_heatmap(stats["weeks"], 420, 72)
    commit_log = svg_commits(events, 34, 230)
    lang_bars = svg_langs(stats["langs"], 34, 356)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      .eye {{ animation: blink 4s step-end infinite; }}
      .pet {{ animation: float 3s ease-in-out infinite; }}
      .hp  {{ animation: pulse 3s ease-in-out infinite; }}
      @keyframes blink  {{ 0%,92% {{ opacity:1 }} 93%,97% {{ opacity:0 }} 98% {{ opacity:1 }} }}
      @keyframes float  {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-5px) }} }}
      @keyframes pulse  {{ 0%,100% {{ opacity:.85 }} 50% {{ opacity:1 }} }}
    </style>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="hpg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#39d353"/><stop offset="100%" stop-color="#7ee787"/>
    </linearGradient>
    <linearGradient id="xpg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#1f6feb"/><stop offset="100%" stop-color="#79c0ff"/>
    </linearGradient>
  </defs>

  <!-- ═══ SHELL ═══ -->
  <rect width="{W}" height="{H}" fill="{C['bg']}" rx="12"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{C['bdr']}" stroke-width="1" rx="11"/>

  <!-- ═══ SCREEN ═══ -->
  <rect x="14" y="14" width="772" height="402" fill="{C['srf']}" rx="6"/>
  <rect x="14" y="14" width="772" height="402" fill="none" stroke="{C['accent']}" stroke-width="0.5" rx="6" opacity="0.25"/>

  <!-- ═══ TITLE BAR ═══ -->
  <rect x="14" y="14" width="772" height="26" fill="{C['tbar']}" rx="6"/>
  <rect x="14" y="32" width="772" height="8" fill="{C['tbar']}"/>
  <circle cx="32" cy="27" r="4.5" fill="#ff5f57"/>
  <circle cx="50" cy="27" r="4.5" fill="#febc2e"/>
  <circle cx="68" cy="27" r="4.5" fill="#28c840"/>
  <text x="400" y="31" font-family="'Courier New', monospace" font-size="11" fill="{C['dim']}" text-anchor="middle">bigmacfive — dashboard.sh</text>

  <!-- ═══════════════════ UPPER SECTION ═══════════════════ -->

  <!-- PIXEL PET (animated) -->
  <g class="pet">
    {pet}
  </g>
  <text x="88" y="142" font-family="'Courier New', monospace" font-size="8" fill="{C['green']}" text-anchor="middle" filter="url(#glow)">&#9670; LV.{stats['years']} &#9670;</text>

  <!-- HP bar -->
  <text x="30" y="161" font-family="'Courier New', monospace" font-size="8" fill="{C['green']}">HP</text>
  <rect x="50" y="152" width="112" height="8" fill="#21262d" rx="3"/>
  <rect x="50" y="152" width="{hp_w}" height="8" fill="url(#hpg)" rx="3" class="hp"/>

  <!-- XP bar -->
  <text x="30" y="177" font-family="'Courier New', monospace" font-size="8" fill="#58a6ff">XP</text>
  <rect x="50" y="168" width="112" height="8" fill="#21262d" rx="3"/>
  <rect x="50" y="168" width="{xp_w}" height="8" fill="url(#xpg)" rx="3"/>

  <!-- STATS PANEL -->
  <text x="195" y="58" font-family="'Courier New', monospace" font-size="10" fill="{C['green']}" filter="url(#glow)">$ neofetch</text>
  <text x="195" y="80"  font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  commits  <tspan fill="{C['txt']}">{commits:,}</tspan></text>
  <text x="195" y="98"  font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  streak   <tspan fill="{C['txt']}">{stats['streak']}d</tspan></text>
  <text x="195" y="116" font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  followers<tspan fill="{C['txt']}"> {stats['followers']}</tspan></text>
  <text x="195" y="134" font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  stars    <tspan fill="{C['txt']}"> {stats['stars']}</tspan></text>
  <text x="195" y="152" font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  repos    <tspan fill="{C['txt']}"> {stats['repos']}</tspan></text>
  <text x="195" y="170" font-family="'Courier New', monospace" font-size="10" fill="{C['dim']}">  joined   <tspan fill="{C['txt']}"> {stats['years']}y ago</tspan></text>

  <!-- vertical divider -->
  <line x1="400" y1="46" x2="400" y2="190" stroke="{C['bdr']}" stroke-width="0.5"/>

  <!-- CONTRIBUTION HEATMAP -->
  <text x="420" y="58" font-family="'Courier New', monospace" font-size="10" fill="{C['green']}" filter="url(#glow)">$ contributions --graph</text>
  {heatmap}
  <!-- heatmap legend -->
  <text x="420" y="152" font-family="'Courier New', monospace" font-size="7" fill="{C['dim']}">less</text>
  <rect x="446" y="143" width="8" height="8" fill="#161b22" rx="1"/>
  <rect x="457" y="143" width="8" height="8" fill="#0e4429" rx="1"/>
  <rect x="468" y="143" width="8" height="8" fill="#006d32" rx="1"/>
  <rect x="479" y="143" width="8" height="8" fill="#26a641" rx="1"/>
  <rect x="490" y="143" width="8" height="8" fill="#39d353" rx="1"/>
  <text x="502" y="152" font-family="'Courier New', monospace" font-size="7" fill="{C['dim']}">more</text>

  <!-- ═══ DIVIDER ═══ -->
  <line x1="30" y1="195" x2="770" y2="195" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="4,4"/>

  <!-- ═══════════════════ COMMIT LOG ═══════════════════ -->
  <text x="30" y="218" font-family="'Courier New', monospace" font-size="10" fill="{C['orange']}" filter="url(#glow)">$ git log --oneline -5</text>

  <!-- blinking cursor -->
  <rect x="232" y="208" width="7" height="12" fill="{C['green']}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>

  <!-- commit entries (staggered fade-in) -->
  <g>
    {commit_log}
  </g>

  <!-- ═══ DIVIDER ═══ -->
  <line x1="30" y1="345" x2="770" y2="345" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="4,4"/>

  <!-- ═══════════════════ LANGUAGES ═══════════════════ -->
  <text x="30" y="340" font-family="'Courier New', monospace" font-size="10" fill="{C['green']}" filter="url(#glow)">$ wc -l --by-language</text>
  {lang_bars}

  <!-- ═══ FOOTER ═══ -->
  <line x1="14" y1="402" x2="786" y2="402" stroke="{C['bdr']}" stroke-width="0.5"/>

  <!-- tamagotchi buttons -->
  <circle cx="330" cy="416" r="7" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="330" y="420" font-family="'Courier New', monospace" font-size="7" fill="{C['dim']}" text-anchor="middle">A</text>
  <circle cx="400" cy="416" r="7" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="400" y="420" font-family="'Courier New', monospace" font-size="7" fill="{C['dim']}" text-anchor="middle">B</text>
  <circle cx="470" cy="416" r="7" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="470" y="420" font-family="'Courier New', monospace" font-size="7" fill="{C['dim']}" text-anchor="middle">C</text>

  <!-- scan line effect (CRT) -->
  <rect width="{W}" height="2" fill="white" opacity="0.015" rx="0">
    <animateTransform attributeName="transform" type="translate" from="0 -2" to="0 {H}" dur="8s" repeatCount="indefinite"/>
  </rect>

  <!-- timestamp -->
  <text x="770" y="420" font-family="'Courier New', monospace" font-size="7" fill="{C['bdr']}" text-anchor="end">{now}</text>
</svg>'''


# ══════════════════════════ MAIN ══════════════════════════

def main():
    print(f"Fetching stats for {USERNAME}...")
    stats = fetch_stats()
    print(f"  commits={stats['commits']} streak={stats['streak']} "
          f"langs={len(stats['langs'])} weeks={len(stats['weeks'])}")

    print("Fetching recent events...")
    events = fetch_events()
    print(f"  {len(events)} recent commits found")

    svg = generate_svg(stats, events)
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated profile.svg")


if __name__ == "__main__":
    main()
