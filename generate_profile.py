#!/usr/bin/env python3
"""GitHub Profile Dashboard v3 — Neon Terminal

Features:
- Animated rainbow gradient border
- Circular progress rings with draw-in animation
- Pixel art pet with float + blink + sparkle particles
- Contribution heatmap (real data)
- Commit log with staggered fade-in + git branch line
- Language bars with glow
- Animated wave footer
- CRT scan line
"""

import os, requests, random
from datetime import datetime, timezone, timedelta
from html import escape as esc
from math import pi

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
W, H = 800, 440

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

C = {
    "body": "#39d353", "hi": "#7ee787", "dark": "#0d1117",
    "bg": "#0d1117", "srf": "#010409", "bdr": "#21262d",
    "accent": "#1f6feb", "green": "#39d353", "orange": "#f78166",
    "purple": "#bc8cff", "txt": "#e6edf3", "dim": "#6e7681",
    "tbar": "#161b22",
}
F = "'Courier New', monospace"


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

    days = sorted([d for w in cal["weeks"] for d in w["contributionDays"]],
                  key=lambda d: d["date"], reverse=True)
    streak, today = 0, datetime.now(timezone.utc).date()
    for day in days:
        exp = today - timedelta(days=streak)
        if datetime.fromisoformat(day["date"]).date() == exp and day["contributionCount"] > 0:
            streak += 1
        elif datetime.fromisoformat(day["date"]).date() < exp:
            break

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


# ══════════════════════════ SVG COMPONENTS ══════════════════════════

def svg_defs():
    return f'''<defs>
    <style>
      .eye  {{ animation: blink 4s step-end infinite; }}
      .pet  {{ animation: float 3s ease-in-out infinite; }}
      @keyframes blink  {{ 0%,92% {{ opacity:1 }} 93%,97% {{ opacity:0 }} 98% {{ opacity:1 }} }}
      @keyframes float  {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-5px) }} }}
    </style>
    <!-- animated gradient border -->
    <linearGradient id="grd" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"><animate attributeName="stop-color" values="{C['green']};{C['accent']};{C['purple']};{C['orange']};{C['green']}" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="50%"><animate attributeName="stop-color" values="{C['accent']};{C['purple']};{C['orange']};{C['green']};{C['accent']}" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="100%"><animate attributeName="stop-color" values="{C['purple']};{C['orange']};{C['green']};{C['accent']};{C['purple']}" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <!-- glow filters -->
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="glow2"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <!-- bar gradients -->
    <linearGradient id="hpg"><stop offset="0%" stop-color="#39d353"/><stop offset="100%" stop-color="#7ee787"/></linearGradient>
    <linearGradient id="xpg"><stop offset="0%" stop-color="#1f6feb"/><stop offset="100%" stop-color="#79c0ff"/></linearGradient>
  </defs>'''


def svg_pet(bx, by, ps=8):
    px = []
    for ry, row in enumerate(PET):
        for cx, cell in enumerate(row):
            if cell == 0: continue
            x, y = bx + cx * ps, by + ry * ps
            col = {1: C["body"], 2: C["dark"], 3: C["hi"]}[cell]
            cls = ' class="eye"' if cell in (2, 3) else ""
            px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{col}"{cls}/>')
    return "\n      ".join(px)


def svg_sparkles(bx, by, w, h):
    random.seed(42)
    parts = []
    for _ in range(10):
        x = bx + random.randint(-10, w + 10)
        y = by + random.randint(-10, h + 10)
        r = random.choice([1, 1.5, 2])
        dur = round(random.uniform(2, 4), 1)
        begin = round(random.uniform(0, 4), 1)
        col = random.choice([C["green"], C["hi"], C["accent"]])
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</circle>')
    return "\n    ".join(parts)


def svg_ring(cx, cy, r, pct, color, value, label, delay=0):
    circ = 2 * pi * r
    offset = circ * (1 - min(pct, 1.0))
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#21262d" stroke-width="5" fill="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="5" fill="none" '
        f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" '
        f'stroke-linecap="round" transform="rotate(-90 {cx} {cy})" filter="url(#glow2)">'
        f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{offset:.1f}" '
        f'dur="1.5s" begin="{delay}s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        f'</circle>'
        f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="{F}" '
        f'font-size="13" fill="{C["txt"]}" font-weight="bold" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay+0.8}s" fill="freeze"/>'
        f'{value}</text>'
        f'<text x="{cx}" y="{cy+r+16}" text-anchor="middle" font-family="{F}" '
        f'font-size="8" fill="{C["dim"]}">{label}</text>')


def heatmap_color(n):
    if n == 0: return "#161b22"
    if n <= 2: return "#0e4429"
    if n <= 5: return "#006d32"
    if n <= 9: return "#26a641"
    return "#39d353"


def svg_heatmap(weeks, bx, by, cs=7, gap=2):
    recent = weeks[-20:] if weeks else []
    rects = []
    for wi, wk in enumerate(recent):
        for di, day in enumerate(wk["contributionDays"]):
            x = bx + wi * (cs + gap)
            y = by + di * (cs + gap)
            col = heatmap_color(day["contributionCount"])
            rects.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="{col}" rx="1.5"/>')
    return "\n      ".join(rects)


def svg_commits(events, x, y):
    if not events:
        return (f'<text x="{x}" y="{y+14}" font-family="{F}" '
                f'font-size="9" fill="{C["dim"]}" opacity="0.4">'
                f'[ no recent public commits ]</text>')
    rows = []
    for i, ev in enumerate(events):
        ly = y + i * 22
        sha, msg, t = ev["sha"], esc(ev["msg"][:44]), reltime(ev["date"])
        repo = esc(ev["repo"][:14])
        # git branch line
        rows.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{0.5 + i*0.2:.1f}s" fill="freeze"/>'
            f'<rect x="{x-6}" y="{ly}" width="3" height="20" fill="{C["orange"]}" rx="1"/>'
            f'<circle cx="{x-5}" cy="{ly+10}" r="4" fill="{C["srf"]}" stroke="{C["orange"]}" stroke-width="1.5"/>'
            f'<rect x="{x+6}" y="{ly+1}" width="732" height="18" fill="{C["tbar"]}" rx="3" opacity="0.35"/>'
            f'<text x="{x+12}" y="{ly+13}" font-family="{F}" font-size="9">'
            f'<tspan fill="{C["orange"]}">{sha}</tspan>'
            f'<tspan fill="{C["dim"]}">  {repo}  </tspan>'
            f'<tspan fill="{C["txt"]}">{msg}</tspan></text>'
            f'<text x="766" y="{ly+13}" font-family="{F}" font-size="8" fill="{C["dim"]}" text-anchor="end">{t}</text>'
            f'</g>')
    return "\n      ".join(rows)


def svg_langs(langs, x, y):
    if not langs:
        return (f'<text x="{x}" y="{y+10}" font-family="{F}" '
                f'font-size="8" fill="{C["dim"]}" opacity="0.4">'
                f'[ add METRICS_TOKEN for private repo data ]</text>')
    bars = []
    for i, (name, color, pct) in enumerate(langs[:6]):
        col, row = i // 3, i % 3
        lx, ly = x + col * 370, y + row * 18
        bw = max(int(pct * 1.3), 2)
        bars.append(
            f'<circle cx="{lx+4}" cy="{ly+5}" r="3" fill="{color}"/>'
            f'<text x="{lx+12}" y="{ly+9}" font-family="{F}" font-size="8" fill="{C["txt"]}">{name[:12]}</text>'
            f'<rect x="{lx+105}" y="{ly}" width="130" height="9" fill="#21262d" rx="4"/>'
            f'<rect x="{lx+105}" y="{ly}" width="{bw}" height="9" fill="{color}" rx="4" filter="url(#glow2)"/>'
            f'<text x="{lx+242}" y="{ly+9}" font-family="{F}" font-size="8" fill="{C["dim"]}">{pct:.1f}%</text>')
    return "\n      ".join(bars)


def svg_wave():
    return (
        '<g opacity="0.3">'
        '<path fill="#0e4429">'
        '<animate attributeName="d" dur="8s" repeatCount="indefinite" values="'
        'M0,420 C80,412 160,428 240,418 C320,408 400,425 480,418 C560,411 640,426 720,418 C760,414 780,420 800,416 L800,440 L0,440 Z;'
        'M0,418 C80,425 160,410 240,420 C320,428 400,412 480,422 C560,428 640,414 720,422 C760,425 780,416 800,420 L800,440 L0,440 Z;'
        'M0,420 C80,412 160,428 240,418 C320,408 400,425 480,418 C560,411 640,426 720,418 C760,414 780,420 800,416 L800,440 L0,440 Z'
        '"/></path>'
        '<path fill="#006d32">'
        '<animate attributeName="d" dur="6s" repeatCount="indefinite" values="'
        'M0,425 C120,418 240,430 360,422 C480,414 600,428 720,422 L800,424 L800,440 L0,440 Z;'
        'M0,422 C120,430 240,416 360,426 C480,430 600,418 720,426 L800,420 L800,440 L0,440 Z;'
        'M0,425 C120,418 240,430 360,422 C480,414 600,428 720,422 L800,424 L800,440 L0,440 Z'
        '"/></path>'
        '</g>')


# ══════════════════════════ ASSEMBLE ══════════════════════════

def generate_svg(stats, events):
    commits = stats["commits"]
    hp_w = int(min(commits / max(commits, 1000), 1.0) * 108)
    xp_w = int(min(stats["streak"] / 30, 1.0) * 108)

    # ring percentages
    c_pct = min(commits / 2000, 1.0) if commits else 0
    s_pct = min(stats["streak"] / 30, 1.0)
    f_pct = min(stats["followers"] / 100, 1.0)

    defs = svg_defs()
    pet = svg_pet(40, 58, ps=8)
    sparkles = svg_sparkles(30, 48, 110, 90)
    ring1 = svg_ring(220, 100, 32, c_pct, C["green"], f'{commits:,}', "commits", 0.2)
    ring2 = svg_ring(310, 100, 32, s_pct, C["accent"], f'{stats["streak"]}d', "streak", 0.5)
    ring3 = svg_ring(400, 100, 32, f_pct, C["purple"], str(stats["followers"]), "followers", 0.8)
    heatmap = svg_heatmap(stats["weeks"], 470, 62)
    commit_log = svg_commits(events, 34, 218)
    lang_bars = svg_langs(stats["langs"], 34, 365)
    wave = svg_wave()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {defs}

  <!-- ═══ SHELL ═══ -->
  <rect width="{W}" height="{H}" fill="{C['bg']}" rx="12"/>
  <!-- animated gradient border -->
  <rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="url(#grd)" stroke-width="1.5" rx="11"/>

  <!-- screen -->
  <rect x="12" y="12" width="776" height="416" fill="{C['srf']}" rx="6"/>
  <rect x="12" y="12" width="776" height="416" fill="none" stroke="url(#grd)" stroke-width="0.5" rx="6" opacity="0.15"/>

  <!-- ═══ TITLE BAR ═══ -->
  <rect x="12" y="12" width="776" height="26" fill="{C['tbar']}" rx="6"/>
  <rect x="12" y="30" width="776" height="8" fill="{C['tbar']}"/>
  <circle cx="30" cy="25" r="4.5" fill="#ff5f57"/>
  <circle cx="48" cy="25" r="4.5" fill="#febc2e"/>
  <circle cx="66" cy="25" r="4.5" fill="#28c840"/>
  <text x="400" y="29" font-family="{F}" font-size="11" fill="{C['dim']}" text-anchor="middle">bigmacfive@github ~ dashboard.sh</text>

  <!-- ═══════════════ UPPER: PET + RINGS + HEATMAP ═══════════════ -->

  <!-- pixel pet (animated) -->
  <g class="pet">{pet}</g>
  <!-- sparkle particles -->
  {sparkles}
  <!-- pet label -->
  <text x="88" y="140" font-family="{F}" font-size="8" fill="{C['green']}" text-anchor="middle" filter="url(#glow)">&#9670; LV.{stats['years']} &#9670;</text>
  <!-- HP -->
  <text x="30" y="158" font-family="{F}" font-size="7" fill="{C['green']}">HP</text>
  <rect x="48" y="150" width="110" height="7" fill="#21262d" rx="3"/>
  <rect x="48" y="150" width="{hp_w}" height="7" fill="url(#hpg)" rx="3">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/>
  </rect>
  <!-- XP -->
  <text x="30" y="170" font-family="{F}" font-size="7" fill="{C['accent']}">XP</text>
  <rect x="48" y="162" width="110" height="7" fill="#21262d" rx="3"/>
  <rect x="48" y="162" width="{xp_w}" height="7" fill="url(#xpg)" rx="3"/>

  <!-- rings: commits / streak / followers -->
  {ring1}
  {ring2}
  {ring3}

  <!-- stats labels under rings -->
  <text x="220" y="150" text-anchor="middle" font-family="{F}" font-size="7" fill="{C['dim']}">stars {stats['stars']}</text>
  <text x="310" y="150" text-anchor="middle" font-family="{F}" font-size="7" fill="{C['dim']}">repos {stats['repos']}</text>
  <text x="400" y="150" text-anchor="middle" font-family="{F}" font-size="7" fill="{C['dim']}">joined {stats['years']}y</text>

  <!-- divider -->
  <line x1="450" y1="44" x2="450" y2="180" stroke="{C['bdr']}" stroke-width="0.5" opacity="0.5"/>

  <!-- CONTRIBUTION HEATMAP -->
  <text x="470" y="54" font-family="{F}" font-size="9" fill="{C['green']}" filter="url(#glow2)">contributions</text>
  {heatmap}
  <!-- legend -->
  <text x="470" y="145" font-family="{F}" font-size="6" fill="{C['dim']}">less</text>
  <rect x="492" y="138" width="7" height="7" fill="#161b22" rx="1"/>
  <rect x="501" y="138" width="7" height="7" fill="#0e4429" rx="1"/>
  <rect x="510" y="138" width="7" height="7" fill="#006d32" rx="1"/>
  <rect x="519" y="138" width="7" height="7" fill="#26a641" rx="1"/>
  <rect x="528" y="138" width="7" height="7" fill="#39d353" rx="1"/>
  <text x="539" y="145" font-family="{F}" font-size="6" fill="{C['dim']}">more</text>

  <!-- ═══ HORIZONTAL DIVIDER ═══ -->
  <line x1="28" y1="185" x2="772" y2="185" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="3,3"/>

  <!-- ═══════════════ COMMIT LOG ═══════════════ -->
  <text x="28" y="203" font-family="{F}" font-size="10" fill="{C['orange']}" filter="url(#glow)">$ git log --oneline</text>
  <!-- cursor -->
  <rect x="200" y="193" width="7" height="12" fill="{C['green']}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>
  {commit_log}

  <!-- ═══ HORIZONTAL DIVIDER ═══ -->
  <line x1="28" y1="345" x2="772" y2="345" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="3,3"/>

  <!-- ═══════════════ LANGUAGES ═══════════════ -->
  <text x="28" y="360" font-family="{F}" font-size="10" fill="{C['green']}" filter="url(#glow)">$ tokei --sort code</text>
  {lang_bars}

  <!-- ═══ FOOTER ═══ -->
  <line x1="12" y1="410" x2="788" y2="410" stroke="{C['bdr']}" stroke-width="0.4"/>

  <!-- tamagotchi buttons -->
  <circle cx="345" cy="425" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="345" y="428" font-family="{F}" font-size="6" fill="{C['dim']}" text-anchor="middle">A</text>
  <circle cx="400" cy="425" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="400" y="428" font-family="{F}" font-size="6" fill="{C['dim']}" text-anchor="middle">B</text>
  <circle cx="455" cy="425" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="455" y="428" font-family="{F}" font-size="6" fill="{C['dim']}" text-anchor="middle">C</text>

  <!-- animated wave -->
  {wave}

  <!-- CRT scan line -->
  <rect width="{W}" height="2" fill="white" opacity="0.012">
    <animateTransform attributeName="transform" type="translate" from="0 -2" to="0 {H}" dur="8s" repeatCount="indefinite"/>
  </rect>

  <!-- timestamp -->
  <text x="772" y="432" font-family="{F}" font-size="6" fill="{C['bdr']}" text-anchor="end">{now}</text>
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
    print(f"Generated profile.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
