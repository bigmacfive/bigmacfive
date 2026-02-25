#!/usr/bin/env python3
"""GitHub Profile Dashboard v5.1 — Claude Theme (Readability)

- Card 850×620: generous vertical spacing
- Bigger fonts, taller rows, wider padding between sections
- Claude brand palette: warm coral, peach, cream on dark
"""

import os, re, requests, random
from datetime import datetime, timezone, timedelta
from html import escape as esc
from math import pi

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
W, H = 850, 620
F = "'Courier New', monospace"

# ── Pixel Pet: 16×13  0=clear 1=body 2=eye 3=highlight 4=blush ──
PET = [
    [0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,2,2,1,1,1,1,2,2,1,1,1,0],
    [0,1,1,1,3,2,1,1,1,1,3,2,1,1,1,0],
    [0,1,1,4,1,1,1,1,1,1,1,1,4,1,1,0],
    [0,1,1,1,1,2,1,1,1,1,2,1,1,1,1,0],
    [0,1,1,1,1,1,2,2,2,2,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0],
]

# ── Claude Brand Palette ──
C = {
    "body": "#D97757",   # Claude coral — pet body
    "hi": "#E8A87C",     # Peach — highlights
    "dark": "#1A1410",   # Warm black — dark elements
    "blush": "#F0A88C",  # Soft blush
    "bg": "#1A1410",     # Warm dark background
    "srf": "#100D09",    # Warm surface
    "bdr": "#3D3028",    # Warm border
    "accent": "#E8A87C", # Peach accent
    "green": "#D97757",  # Claude coral (primary)
    "orange": "#C4703E", # Deep terracotta
    "purple": "#F5E6D3", # Cream
    "txt": "#F5E6D3",    # Cream text
    "dim": "#9B8672",    # Warm muted
    "tbar": "#211A14",   # Warm title bar
}

AI_PATTERNS = {
    "Claude": r"Co-[Aa]uthored-[Bb]y:.*Claude.*@anthropic\.com",
    "Cursor": r"Co-[Aa]uthored-[Bb]y:.*[Cc]ursor",
    "Copilot": r"Co-[Aa]uthored-[Bb]y:.*[Cc]opilot",
}
AI_COLORS = {"Claude": "#D97757", "Cursor": "#E8A87C", "Copilot": "#F5E6D3"}


# ══════════════════════════ DATA ══════════════════════════

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


def fetch_ai_ratio():
    """Scan commits across repos for AI co-author signatures."""
    data = gql("""
    query($login: String!) {
      user(login: $login) {
        repositories(first: 30, ownerAffiliations: OWNER, isFork: false,
                     orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100) { nodes { message } }
                }
              }
            }
          }
        }
      }
    }""", {"login": USERNAME})
    if not data or not data.get("user"):
        return {"total": 0, "ai": 0, "human": 0, "tools": {}}

    total, ai_total, tools = 0, 0, {}
    for repo in data["user"]["repositories"]["nodes"]:
        ref = repo.get("defaultBranchRef")
        if not ref or not ref.get("target"):
            continue
        for commit in ref["target"].get("history", {}).get("nodes", []):
            total += 1
            msg = commit.get("message", "")
            for tool, pat in AI_PATTERNS.items():
                if re.search(pat, msg):
                    tools[tool] = tools.get(tool, 0) + 1
                    ai_total += 1
                    break
    return {"total": total, "ai": ai_total, "human": total - ai_total, "tools": tools}


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


# ══════════════════════════ SVG PARTS ══════════════════════════

def svg_defs():
    return f'''<defs>
    <style>
      .eye {{ animation: blink 4s step-end infinite; }}
      .pet {{ animation: float 3s ease-in-out infinite; }}
      @keyframes blink {{ 0%,92% {{ opacity:1 }} 93%,97% {{ opacity:0 }} 98% {{ opacity:1 }} }}
      @keyframes float {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-6px) }} }}
    </style>
    <linearGradient id="grd" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"><animate attributeName="stop-color" values="#D97757;#E8A87C;#F5E6D3;#C4703E;#D97757" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="50%"><animate attributeName="stop-color" values="#E8A87C;#F5E6D3;#C4703E;#D97757;#E8A87C" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="100%"><animate attributeName="stop-color" values="#F5E6D3;#C4703E;#D97757;#E8A87C;#F5E6D3" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="glow2"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="hpg"><stop offset="0%" stop-color="#D97757"/><stop offset="100%" stop-color="#E8A87C"/></linearGradient>
    <linearGradient id="xpg"><stop offset="0%" stop-color="#C4703E"/><stop offset="100%" stop-color="#D97757"/></linearGradient>
  </defs>'''


def svg_pet(bx, by, ps=9):
    color_map = {1: C["body"], 2: C["dark"], 3: C["hi"], 4: C["blush"]}
    px = []
    for ry, row in enumerate(PET):
        for cx, cell in enumerate(row):
            if cell == 0: continue
            x, y = bx + cx * ps, by + ry * ps
            col = color_map[cell]
            cls = ' class="eye"' if cell in (2, 3) and 3 <= ry <= 4 else ""
            px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{col}"{cls}/>')
    return "\n      ".join(px)


def svg_sparkles(bx, by, w, h):
    random.seed(42)
    parts = []
    for _ in range(12):
        x, y = bx + random.randint(-12, w+12), by + random.randint(-12, h+12)
        r = round(random.uniform(1, 2.5), 1)
        dur = round(random.uniform(2, 4), 1)
        begin = round(random.uniform(0, 5), 1)
        col = random.choice(["#D97757", "#E8A87C", "#F5E6D3", "#C4703E"])
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</circle>')
    return "\n    ".join(parts)


def svg_ring(cx, cy, r, pct, color, value, label, delay=0):
    circ = 2 * pi * r
    off = circ * (1 - min(pct, 1.0))
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{C["bdr"]}" stroke-width="5" fill="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="5" fill="none" '
        f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" '
        f'stroke-linecap="round" transform="rotate(-90 {cx} {cy})" filter="url(#glow2)">'
        f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{off:.1f}" '
        f'dur="1.5s" begin="{delay}s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        f'</circle>'
        f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="{F}" '
        f'font-size="16" fill="{C["txt"]}" font-weight="bold" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay+0.8}s" fill="freeze"/>'
        f'{value}</text>'
        f'<text x="{cx}" y="{cy+r+18}" text-anchor="middle" font-family="{F}" '
        f'font-size="10" fill="{C["dim"]}">{label}</text>')


def svg_collab(ratio, x, y, width):
    """AI collaboration ratio segmented bar."""
    total = ratio["total"]
    if total == 0:
        return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="12" fill="{C["green"]}" '
                f'filter="url(#glow2)">$ collab --ratio</text>'
                f'<text x="{x}" y="{y+26}" font-family="{F}" font-size="10" fill="{C["dim"]}" '
                f'opacity="0.4">[ scanning commits... ]</text>')

    human_pct = ratio["human"] / total * 100
    ai_pct = ratio["ai"] / total * 100

    # build segments: human first, then each tool
    segments = [("Human", "#E8A87C", ratio["human"])]
    for tool, count in sorted(ratio["tools"].items(), key=lambda x: x[1], reverse=True):
        segments.append((tool, AI_COLORS.get(tool, C["dim"]), count))

    bar_y = y + 18
    bar_h = 18
    parts = [
        f'<text x="{x}" y="{y}" font-family="{F}" font-size="12" fill="{C["green"]}" '
        f'filter="url(#glow2)">$ collab --ratio</text>',
        f'<rect x="{x}" y="{bar_y}" width="{width}" height="{bar_h}" fill="{C["bdr"]}" rx="8"/>',
    ]

    # draw segments
    cx = x
    for i, (name, color, count) in enumerate(segments):
        seg_w = int(count / total * width)
        if i == len(segments) - 1:
            seg_w = width - (cx - x)
        if seg_w < 1:
            continue
        parts.append(
            f'<rect x="{cx}" y="{bar_y}" width="{seg_w}" height="{bar_h}" fill="{color}" '
            f'opacity="0.85" rx="0">'
            f'<animate attributeName="width" from="0" to="{seg_w}" dur="1s" '
            f'begin="0.3s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
            f'</rect>')
        cx += seg_w

    # rounded corners overlay
    parts.append(
        f'<rect x="{x}" y="{bar_y}" width="{width}" height="{bar_h}" fill="none" '
        f'stroke="{C["bdr"]}" stroke-width="1" rx="8"/>')

    # percentage labels on bar
    if human_pct > 15:
        parts.append(
            f'<text x="{x + int(ratio["human"]/total*width/2)}" y="{bar_y + 13}" '
            f'text-anchor="middle" font-family="{F}" font-size="10" fill="{C["dark"]}" '
            f'font-weight="bold">{human_pct:.0f}%</text>')
    if ai_pct > 10:
        ai_center = x + int(ratio["human"]/total*width) + int(ratio["ai"]/total*width/2)
        parts.append(
            f'<text x="{ai_center}" y="{bar_y + 13}" text-anchor="middle" '
            f'font-family="{F}" font-size="10" fill="{C["dark"]}" font-weight="bold">'
            f'{ai_pct:.0f}%</text>')

    # legend dots below bar
    lx = x
    legend_y = bar_y + bar_h + 18
    for name, color, count in segments:
        pct = count / total * 100
        parts.append(
            f'<circle cx="{lx + 5}" cy="{legend_y - 3}" r="4.5" fill="{color}"/>'
            f'<text x="{lx + 15}" y="{legend_y + 1}" font-family="{F}" font-size="10" '
            f'fill="{C["txt"]}">{name} <tspan fill="{C["dim"]}">{pct:.0f}%</tspan></text>')
        lx += max(len(name) * 8 + 70, 130)

    return "\n    ".join(parts)


def heatmap_color(n):
    if n == 0: return "#211A14"
    if n <= 2: return "#4A2C1A"
    if n <= 5: return "#7A4528"
    if n <= 9: return "#B85F35"
    return "#D97757"


def svg_heatmap(weeks, bx, by, cs=8, gap=2):
    recent = weeks[-18:] if weeks else []
    rects = []
    for wi, wk in enumerate(recent):
        for di, day in enumerate(wk["contributionDays"]):
            x, y = bx + wi * (cs + gap), by + di * (cs + gap)
            rects.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'fill="{heatmap_color(day["contributionCount"])}" rx="2"/>')
    return "\n      ".join(rects)


def svg_commits(events, x, y):
    if not events:
        return (f'<text x="{x}" y="{y+16}" font-family="{F}" font-size="11" '
                f'fill="{C["dim"]}" opacity="0.4">[ no recent public commits ]</text>')
    rows = []
    for i, ev in enumerate(events):
        ly = y + i * 28
        sha, msg, t = ev["sha"], esc(ev["msg"][:48]), reltime(ev["date"])
        repo = esc(ev["repo"][:14])
        rows.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{0.5 + i*0.18:.2f}s" fill="freeze"/>'
            f'<rect x="{x-6}" y="{ly}" width="3" height="26" fill="{C["orange"]}" rx="1"/>'
            f'<circle cx="{x-5}" cy="{ly+13}" r="5" fill="{C["srf"]}" stroke="{C["orange"]}" stroke-width="1.5"/>'
            f'<rect x="{x+8}" y="{ly+1}" width="748" height="24" fill="{C["tbar"]}" rx="4" opacity="0.3"/>'
            f'<text x="{x+16}" y="{ly+17}" font-family="{F}" font-size="11">'
            f'<tspan fill="{C["orange"]}">{sha}</tspan>'
            f'<tspan fill="{C["dim"]}">  {repo}  </tspan>'
            f'<tspan fill="{C["txt"]}">{msg}</tspan></text>'
            f'<text x="800" y="{ly+17}" font-family="{F}" font-size="10" '
            f'fill="{C["dim"]}" text-anchor="end">{t}</text>'
            f'</g>')
    return "\n      ".join(rows)


def svg_langs(langs, x, y):
    if not langs:
        return (f'<text x="{x}" y="{y+12}" font-family="{F}" font-size="10" '
                f'fill="{C["dim"]}" opacity="0.4">[ add METRICS_TOKEN for private repo data ]</text>')
    bars = []
    for i, (name, color, pct) in enumerate(langs[:6]):
        col, row = i // 3, i % 3
        lx, ly = x + col * 390, y + row * 24
        bw = max(int(pct * 1.6), 3)
        bars.append(
            f'<circle cx="{lx+5}" cy="{ly+7}" r="4.5" fill="{color}"/>'
            f'<text x="{lx+16}" y="{ly+12}" font-family="{F}" font-size="10" fill="{C["txt"]}">{name[:14]}</text>'
            f'<rect x="{lx+120}" y="{ly}" width="150" height="12" fill="{C["bdr"]}" rx="5"/>'
            f'<rect x="{lx+120}" y="{ly}" width="{bw}" height="12" fill="{color}" rx="5" filter="url(#glow2)"/>'
            f'<text x="{lx+278}" y="{ly+12}" font-family="{F}" font-size="10" fill="{C["dim"]}">{pct:.1f}%</text>')
    return "\n      ".join(bars)


def svg_wave():
    return (
        '<g opacity="0.3">'
        '<path fill="#3D2415"><animate attributeName="d" dur="8s" repeatCount="indefinite" values="'
        f'M0,{H-30} C100,{H-38} 200,{H-22} 300,{H-30} C400,{H-38} 500,{H-20} 600,{H-30} '
        f'C700,{H-38} 750,{H-25} {W},{H-30} L{W},{H} L0,{H} Z;'
        f'M0,{H-25} C100,{H-18} 200,{H-35} 300,{H-25} C400,{H-18} 500,{H-35} 600,{H-25} '
        f'C700,{H-18} 750,{H-30} {W},{H-25} L{W},{H} L0,{H} Z;'
        f'M0,{H-30} C100,{H-38} 200,{H-22} 300,{H-30} C400,{H-38} 500,{H-20} 600,{H-30} '
        f'C700,{H-38} 750,{H-25} {W},{H-30} L{W},{H} L0,{H} Z'
        '"/></path>'
        '<path fill="#5A3520"><animate attributeName="d" dur="5s" repeatCount="indefinite" values="'
        f'M0,{H-20} C140,{H-14} 280,{H-26} 420,{H-20} C560,{H-14} 700,{H-26} {W},{H-18} '
        f'L{W},{H} L0,{H} Z;'
        f'M0,{H-18} C140,{H-26} 280,{H-12} 420,{H-20} C560,{H-26} 700,{H-14} {W},{H-22} '
        f'L{W},{H} L0,{H} Z;'
        f'M0,{H-20} C140,{H-14} 280,{H-26} 420,{H-20} C560,{H-14} 700,{H-26} {W},{H-18} '
        f'L{W},{H} L0,{H} Z'
        '"/></path>'
        '</g>')


# ══════════════════════════ ASSEMBLE ══════════════════════════

def generate_svg(stats, events, ai_ratio):
    commits = stats["commits"]
    hp_w = int(min(commits / max(commits, 1000), 1.0) * 118)
    xp_w = int(min(stats["streak"] / 30, 1.0) * 118)
    c_pct = min(commits / 2000, 1.0) if commits else 0
    s_pct = min(stats["streak"] / 30, 1.0)
    f_pct = min(stats["followers"] / 100, 1.0)

    defs = svg_defs()
    pet = svg_pet(30, 54, ps=9)
    sparkles = svg_sparkles(24, 46, 156, 130)
    ring1 = svg_ring(250, 100, 36, c_pct, "#D97757", f'{commits:,}', "commits", 0.2)
    ring2 = svg_ring(350, 100, 36, s_pct, "#E8A87C", f'{stats["streak"]}d', "streak", 0.5)
    ring3 = svg_ring(450, 100, 36, f_pct, "#F5E6D3", str(stats["followers"]), "followers", 0.8)
    heatmap = svg_heatmap(stats["weeks"], 510, 64)
    collab = svg_collab(ai_ratio, 32, 234, 786)
    commit_log = svg_commits(events, 40, 324)
    lang_bars = svg_langs(stats["langs"], 40, 538)
    wave = svg_wave()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # pet bottom y
    pet_bot = 54 + 13 * 9  # = 171

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {defs}

  <!-- ═══ SHELL ═══ -->
  <rect width="{W}" height="{H}" fill="{C['bg']}" rx="14"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="url(#grd)" stroke-width="1.5" rx="13"/>

  <!-- screen -->
  <rect x="12" y="12" width="{W-24}" height="{H-24}" fill="{C['srf']}" rx="6"/>
  <rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="url(#grd)" stroke-width="0.4" rx="6" opacity="0.12"/>

  <!-- ═══ TITLE BAR ═══ -->
  <rect x="12" y="12" width="{W-24}" height="28" fill="{C['tbar']}" rx="6"/>
  <rect x="12" y="32" width="{W-24}" height="8" fill="{C['tbar']}"/>
  <circle cx="30" cy="26" r="5" fill="#D97757"/>
  <circle cx="50" cy="26" r="5" fill="#E8A87C"/>
  <circle cx="70" cy="26" r="5" fill="#F5E6D3"/>
  <text x="{W//2}" y="30" font-family="{F}" font-size="12" fill="{C['dim']}" text-anchor="middle">bigmacfive@github ~ dashboard.sh</text>

  <!-- ═══════════════ UPPER: PET + RINGS + HEATMAP ═══════════════ -->

  <!-- pixel pet -->
  <g class="pet">{pet}</g>
  {sparkles}
  <text x="{30+72}" y="{pet_bot+16}" font-family="{F}" font-size="11" fill="{C['green']}" text-anchor="middle" filter="url(#glow)">&#9670; LV.{stats['years']} &#9670;</text>

  <!-- HP -->
  <text x="30" y="{pet_bot+32}" font-family="{F}" font-size="9" fill="{C['green']}">HP</text>
  <rect x="52" y="{pet_bot+23}" width="120" height="9" fill="{C['bdr']}" rx="4"/>
  <rect x="52" y="{pet_bot+23}" width="{hp_w}" height="9" fill="url(#hpg)" rx="4">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/>
  </rect>
  <!-- XP -->
  <text x="30" y="{pet_bot+46}" font-family="{F}" font-size="9" fill="{C['accent']}">XP</text>
  <rect x="52" y="{pet_bot+37}" width="120" height="9" fill="{C['bdr']}" rx="4"/>
  <rect x="52" y="{pet_bot+37}" width="{xp_w}" height="9" fill="url(#xpg)" rx="4"/>

  <!-- stat rings -->
  {ring1}
  {ring2}
  {ring3}
  <text x="250" y="160" text-anchor="middle" font-family="{F}" font-size="9" fill="{C['dim']}">stars {stats['stars']}</text>
  <text x="350" y="160" text-anchor="middle" font-family="{F}" font-size="9" fill="{C['dim']}">repos {stats['repos']}</text>
  <text x="450" y="160" text-anchor="middle" font-family="{F}" font-size="9" fill="{C['dim']}">joined {stats['years']}y</text>

  <!-- divider -->
  <line x1="490" y1="46" x2="490" y2="200" stroke="{C['bdr']}" stroke-width="0.5" opacity="0.4"/>

  <!-- heatmap -->
  <text x="510" y="56" font-family="{F}" font-size="11" fill="{C['green']}" filter="url(#glow2)">contributions</text>
  {heatmap}
  <text x="510" y="144" font-family="{F}" font-size="8" fill="{C['dim']}">less</text>
  <rect x="534" y="136" width="8" height="8" fill="#211A14" rx="1.5"/>
  <rect x="544" y="136" width="8" height="8" fill="#4A2C1A" rx="1.5"/>
  <rect x="554" y="136" width="8" height="8" fill="#7A4528" rx="1.5"/>
  <rect x="564" y="136" width="8" height="8" fill="#B85F35" rx="1.5"/>
  <rect x="574" y="136" width="8" height="8" fill="#D97757" rx="1.5"/>
  <text x="586" y="144" font-family="{F}" font-size="8" fill="{C['dim']}">more</text>

  <!-- ═══ DIVIDER ═══ -->
  <line x1="28" y1="218" x2="822" y2="218" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="3,3"/>

  <!-- ═══════════════ AI COLLAB RATIO ═══════════════ -->
  {collab}

  <!-- ═══ DIVIDER ═══ -->
  <line x1="28" y1="302" x2="822" y2="302" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="3,3"/>

  <!-- ═══════════════ COMMIT LOG ═══════════════ -->
  <text x="32" y="320" font-family="{F}" font-size="12" fill="{C['orange']}" filter="url(#glow)">$ git log --oneline</text>
  <rect x="235" y="309" width="8" height="14" fill="{C['green']}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>
  {commit_log}

  <!-- ═══ DIVIDER ═══ -->
  <line x1="28" y1="520" x2="822" y2="520" stroke="{C['bdr']}" stroke-width="0.5" stroke-dasharray="3,3"/>

  <!-- ═══════════════ LANGUAGES ═══════════════ -->
  <text x="32" y="536" font-family="{F}" font-size="12" fill="{C['green']}" filter="url(#glow)">$ tokei --sort code</text>
  {lang_bars}

  <!-- ═══ FOOTER ═══ -->
  <line x1="12" y1="{H-28}" x2="{W-12}" y2="{H-28}" stroke="{C['bdr']}" stroke-width="0.3"/>
  <circle cx="{W//2-55}" cy="{H-14}" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="{W//2-55}" y="{H-11}" font-family="{F}" font-size="7" fill="{C['dim']}" text-anchor="middle">A</text>
  <circle cx="{W//2}" cy="{H-14}" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="{W//2}" y="{H-11}" font-family="{F}" font-size="7" fill="{C['dim']}" text-anchor="middle">B</text>
  <circle cx="{W//2+55}" cy="{H-14}" r="6" fill="{C['tbar']}" stroke="{C['bdr']}" stroke-width="1"/>
  <text x="{W//2+55}" y="{H-11}" font-family="{F}" font-size="7" fill="{C['dim']}" text-anchor="middle">C</text>

  {wave}

  <!-- CRT scan line -->
  <rect width="{W}" height="2" fill="#F5E6D3" opacity="0.008">
    <animateTransform attributeName="transform" type="translate" from="0 -2" to="0 {H}" dur="8s" repeatCount="indefinite"/>
  </rect>

  <text x="822" y="{H-8}" font-family="{F}" font-size="8" fill="{C['bdr']}" text-anchor="end">{now}</text>
</svg>'''


# ══════════════════════════ MAIN ══════════════════════════

def main():
    print(f"Fetching data for {USERNAME}...")
    stats = fetch_stats()
    print(f"  commits={stats['commits']} streak={stats['streak']} "
          f"langs={len(stats['langs'])} weeks={len(stats['weeks'])}")

    events = fetch_events()
    print(f"  {len(events)} recent commits")

    ai_ratio = fetch_ai_ratio()
    print(f"  AI ratio: {ai_ratio['ai']}/{ai_ratio['total']} "
          f"({', '.join(f'{k}:{v}' for k,v in ai_ratio['tools'].items()) or 'none'})")

    svg = generate_svg(stats, events, ai_ratio)
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated profile.svg ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
