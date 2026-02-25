#!/usr/bin/env python3
"""GitHub Profile Dashboard v7 — Legend of Zelda Retro RPG

- NES/SNES Zelda-inspired dark dungeon palette
- Pixel art heart containers in HUD bar
- Rupee counter for stars
- RPG status screen for stats
- "World Map" contribution heatmap
- "Quest Log" commit history
- "Inventory" language items
- "Companions" AI collab party
- Pixel-beveled panel borders
- Triforce decorations
"""

import os, re, requests, random
from datetime import datetime, timezone, timedelta
from html import escape as esc
from math import pi

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
W, H = 850, 700
F = "'Courier New', 'Courier', monospace"

# ── Hero Pixel Art (same shape, Zelda-green palette) ──
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

# ── Pixel Heart (5×5 grid) ──
HEART = [
    [0,1,0,1,0],
    [1,1,1,1,1],
    [1,1,1,1,1],
    [0,1,1,1,0],
    [0,0,1,0,0],
]

# ── Zelda Dungeon Palette ──
C = {
    "bg":       "#0b0e14",  # Dungeon black-blue
    "panel":    "#101820",  # Dark panel
    "panel_hi": "#1a2a38",  # Panel highlight (top-left bevel)
    "bdr":      "#2a5a30",  # Zelda green border
    "bdr_hi":   "#4aaa50",  # Bright green border highlight
    "gold":     "#f8d830",  # Triforce gold
    "gold2":    "#c8a820",  # Dark gold
    "heart":    "#e83030",  # Heart red
    "heart_e":  "#401818",  # Empty heart
    "rupee":    "#40b8f0",  # Rupee blue
    "green":    "#38e850",  # Hyrule bright green
    "green2":   "#208830",  # Dark green
    "txt":      "#e0dcc8",  # Parchment text
    "txt2":     "#88a878",  # Muted green text
    "txt3":     "#4a6848",  # Dark muted
    "body":     "#38e850",  # Hero body green
    "hi":       "#80ff98",  # Hero highlight
    "dark":     "#0b1810",  # Hero dark
    "blush":    "#ff9080",  # Hero blush
}

AI_PATTERNS = {
    "Claude": r"Co-[Aa]uthored-[Bb]y:.*Claude.*@anthropic\.com",
    "Cursor": r"Co-[Aa]uthored-[Bb]y:.*[Cc]ursor",
    "Copilot": r"Co-[Aa]uthored-[Bb]y:.*[Cc]opilot",
}
AI_COLORS = {"Claude": "#b870ff", "Cursor": "#40b8f0", "Copilot": "#e0dcc8"}
AI_NAMES = {"Claude": "Navi", "Cursor": "Tatl", "Copilot": "Ciela"}


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
      .hero {{ animation: float 3s ease-in-out infinite; }}
      .cursor {{ animation: cursor 1s step-end infinite; }}
      @keyframes blink {{ 0%,92%{{opacity:1}} 93%,97%{{opacity:0}} 98%{{opacity:1}} }}
      @keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-4px)}} }}
      @keyframes cursor {{ 0%,49%{{opacity:1}} 50%,100%{{opacity:0}} }}
    </style>
    <linearGradient id="hpg"><stop offset="0%" stop-color="{C['heart']}"/><stop offset="100%" stop-color="#ff6060"/></linearGradient>
    <linearGradient id="mpg"><stop offset="0%" stop-color="#2080e0"/><stop offset="100%" stop-color="#60b0ff"/></linearGradient>
    <linearGradient id="triforce" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{C['gold']}"/><stop offset="100%" stop-color="{C['gold2']}"/>
    </linearGradient>
  </defs>'''


def svg_zelda_border():
    """Double-line pixel border like NES Zelda text boxes."""
    return (
        # Outer border
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{C["bg"]}" rx="2"/>'
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" fill="none" '
        f'stroke="{C["bdr"]}" stroke-width="3" rx="1"/>'
        # Inner border (double-line effect)
        f'<rect x="7" y="7" width="{W-14}" height="{H-14}" fill="none" '
        f'stroke="{C["bdr"]}" stroke-width="1" rx="1"/>'
    )


def svg_panel(x, y, w, h):
    """Beveled pixel panel like SNES Zelda menus."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["panel"]}" '
        f'stroke="{C["bdr"]}" stroke-width="1.5" rx="2"/>'
        # Top-left bevel highlight
        f'<line x1="{x+3}" y1="{y+3}" x2="{x+w-3}" y2="{y+3}" '
        f'stroke="{C["panel_hi"]}" stroke-width="1" opacity="0.6"/>'
        f'<line x1="{x+3}" y1="{y+3}" x2="{x+3}" y2="{y+h-3}" '
        f'stroke="{C["panel_hi"]}" stroke-width="1" opacity="0.4"/>'
    )


def svg_section_header(x, y, title):
    """Gold Zelda-style section title."""
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="11" '
            f'fill="{C["gold"]}" letter-spacing="2">{title}</text>')


def svg_pixel_heart(x, y, filled=True, ps=3):
    """Draw a single pixel heart."""
    col = C["heart"] if filled else C["heart_e"]
    rects = []
    for ry, row in enumerate(HEART):
        for cx, cell in enumerate(row):
            if cell:
                rects.append(f'<rect x="{x+cx*ps}" y="{y+ry*ps}" width="{ps}" height="{ps}" fill="{col}"/>')
    return "".join(rects)


def svg_rupee(x, y, size=10):
    """Small pixel rupee diamond."""
    s = size
    return (
        f'<polygon points="{x+s//2},{y} {x+s},{y+s//2} {x+s//2},{y+s} {x},{y+s//2}" '
        f'fill="{C["rupee"]}" opacity="0.9"/>'
        f'<line x1="{x+s//2}" y1="{y+1}" x2="{x+s//2}" y2="{y+s-1}" '
        f'stroke="#80d8ff" stroke-width="1" opacity="0.4"/>'
    )


def svg_triforce(x, y, size=12):
    """Tiny triforce decoration."""
    s = size
    h = int(s * 0.866)
    return (
        # Top triangle
        f'<polygon points="{x+s//2},{y} {x+s*3//4},{y+h//2} {x+s//4},{y+h//2}" fill="url(#triforce)" opacity="0.7"/>'
        # Bottom-left
        f'<polygon points="{x+s//4},{y+h//2} {x+s//2},{y+h} {x},{y+h}" fill="url(#triforce)" opacity="0.7"/>'
        # Bottom-right
        f'<polygon points="{x+s*3//4},{y+h//2} {x+s},{y+h} {x+s//2},{y+h}" fill="url(#triforce)" opacity="0.7"/>'
    )


def svg_hud(stats):
    """Top HUD bar: hearts + title + rupees."""
    hud_y = 12
    parts = []

    # Hearts (5 total, filled based on commits/2000)
    filled = min(int(stats["commits"] / 400) + (1 if stats["commits"] > 0 else 0), 5)
    hx = 22
    for i in range(5):
        parts.append(svg_pixel_heart(hx + i * 20, hud_y, filled=(i < filled)))

    # Title
    parts.append(
        f'<text x="{W//2}" y="{hud_y + 12}" font-family="{F}" font-size="13" '
        f'fill="{C["gold"]}" text-anchor="middle" letter-spacing="3">'
        f'BIGMACFIVE\'S QUEST</text>')

    # Triforce decorations flanking title
    parts.append(svg_triforce(W//2 - 120, hud_y + 1, 12))
    parts.append(svg_triforce(W//2 + 108, hud_y + 1, 12))

    # Rupee counter (stars)
    parts.append(svg_rupee(W - 80, hud_y, 12))
    parts.append(
        f'<text x="{W - 62}" y="{hud_y + 12}" font-family="{F}" font-size="12" '
        f'fill="{C["txt"]}">{stats["stars"]:>3}</text>')

    # HUD divider
    parts.append(
        f'<line x1="12" y1="38" x2="{W-12}" y2="38" stroke="{C["bdr"]}" stroke-width="1"/>')

    return "\n    ".join(parts)


def svg_pet(bx, by, ps=8):
    """Hero pixel art in Zelda green."""
    color_map = {1: C["body"], 2: C["dark"], 3: C["hi"], 4: C["blush"]}
    px = []
    for ry, row in enumerate(PET):
        for cx, cell in enumerate(row):
            if cell == 0:
                continue
            x, y = bx + cx * ps, by + ry * ps
            col = color_map[cell]
            cls = ' class="eye"' if cell in (2, 3) and 3 <= ry <= 4 else ""
            px.append(f'<rect x="{x}" y="{y}" width="{ps}" height="{ps}" fill="{col}"{cls}/>')
    return "\n      ".join(px)


def svg_sparkles(bx, by, w, h):
    random.seed(42)
    parts = []
    for _ in range(8):
        x, y = bx + random.randint(-6, w + 6), by + random.randint(-6, h + 6)
        r = round(random.uniform(0.8, 1.8), 1)
        dur = round(random.uniform(2, 4), 1)
        begin = round(random.uniform(0, 5), 1)
        col = random.choice([C["green"], C["hi"], C["gold"], "#80ff98"])
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</circle>')
    return "\n    ".join(parts)


def svg_hero_panel(stats):
    """Hero panel: pixel art + level + HP/MP bars."""
    px, py, pw, ph = 16, 48, 180, 180
    pet_x = px + (pw - 16 * 8) // 2
    pet_y = py + 12
    pet_bot = pet_y + 13 * 8

    commits = stats["commits"]
    hp_w = int(min(commits / max(commits, 1000), 1.0) * 100)
    mp_w = int(min(stats["streak"] / 30, 1.0) * 100)

    return (
        svg_panel(px, py, pw, ph)
        + f'<g class="hero">{svg_pet(pet_x, pet_y, 8)}</g>'
        + svg_sparkles(pet_x - 4, pet_y - 4, 128, 104)
        # Level badge
        + f'<text x="{px + pw//2}" y="{pet_bot + 16}" font-family="{F}" font-size="10" '
          f'fill="{C["gold"]}" text-anchor="middle" letter-spacing="1">- LV.{stats["years"]} -</text>'
        # HP bar
        + f'<text x="{px + 12}" y="{pet_bot + 32}" font-family="{F}" font-size="8" fill="{C["heart"]}">HP</text>'
        + f'<rect x="{px + 34}" y="{pet_bot + 24}" width="104" height="8" fill="{C["heart_e"]}" rx="1"/>'
        + f'<rect x="{px + 34}" y="{pet_bot + 24}" width="{hp_w}" height="8" fill="url(#hpg)" rx="1">'
          f'<animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/></rect>'
        # MP bar (magic power = streak)
        + f'<text x="{px + 12}" y="{pet_bot + 46}" font-family="{F}" font-size="8" fill="{C["rupee"]}">MP</text>'
        + f'<rect x="{px + 34}" y="{pet_bot + 38}" width="104" height="8" fill="#102040" rx="1"/>'
        + f'<rect x="{px + 34}" y="{pet_bot + 38}" width="{mp_w}" height="8" fill="url(#mpg)" rx="1"/>'
    )


def svg_status_panel(stats):
    """RPG Status screen with dotted stat lines."""
    px, py, pw, ph = 206, 48, 284, 180
    ix, iy = px + 14, py + 14

    header = svg_section_header(ix, iy + 10, "STATUS")

    stat_lines = [
        ("COMMITS", f'{stats["commits"]:,}', C["green"]),
        ("STREAK", f'{stats["streak"]}d', C["rupee"]),
        ("FOLLOWERS", str(stats["followers"]), C["gold"]),
        ("REPOS", str(stats["repos"]), C["txt"]),
        ("JOINED", f'{stats["years"]}y ago', C["txt2"]),
    ]

    rows = []
    for i, (label, value, color) in enumerate(stat_lines):
        ry = iy + 28 + i * 26
        # Dotted line between label and value
        dots = "." * (20 - len(label) - len(value))
        rows.append(
            f'<text x="{ix}" y="{ry}" font-family="{F}" font-size="11" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" '
            f'begin="{0.2 + i * 0.12:.2f}s" fill="freeze"/>'
            f'<tspan fill="{C["txt2"]}">{label}</tspan>'
            f'<tspan fill="{C["txt3"]}">{dots}</tspan>'
            f'<tspan fill="{color}">{value}</tspan></text>')

    # Fun flavor text
    flavor = (f'<text x="{ix}" y="{iy + 168}" font-family="{F}" font-size="8" '
              f'fill="{C["txt3"]}" font-style="italic">'
              f'&quot;It\'s dangerous to code alone!&quot;</text>')

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(rows) + flavor


def heatmap_color(n):
    if n == 0: return "#0a1a10"
    if n <= 2: return "#0d3b1e"
    if n <= 5: return "#1a6b34"
    if n <= 9: return "#2aaa4a"
    return "#3de868"


def svg_worldmap_panel(weeks):
    """World Map: contribution heatmap in Zelda greens."""
    px, py, pw, ph = 500, 48, 334, 180
    ix, iy = px + 14, py + 14

    header = svg_section_header(ix, iy + 10, "WORLD MAP")

    recent = weeks[-18:] if weeks else []
    cs, gap = 8, 2
    gx, gy = ix + 4, iy + 22
    rects = []
    for wi, wk in enumerate(recent):
        for di, day in enumerate(wk["contributionDays"]):
            x = gx + wi * (cs + gap)
            y = gy + di * (cs + gap)
            rects.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'fill="{heatmap_color(day["contributionCount"])}" rx="1"/>')

    # Legend
    leg_y = gy + 7 * (cs + gap) + 8
    legend = (
        f'<text x="{gx}" y="{leg_y + 8}" font-family="{F}" font-size="7" fill="{C["txt3"]}">safe</text>'
        f'<rect x="{gx + 26}" y="{leg_y}" width="8" height="8" fill="#0a1a10" rx="1"/>'
        f'<rect x="{gx + 36}" y="{leg_y}" width="8" height="8" fill="#0d3b1e" rx="1"/>'
        f'<rect x="{gx + 46}" y="{leg_y}" width="8" height="8" fill="#1a6b34" rx="1"/>'
        f'<rect x="{gx + 56}" y="{leg_y}" width="8" height="8" fill="#2aaa4a" rx="1"/>'
        f'<rect x="{gx + 66}" y="{leg_y}" width="8" height="8" fill="#3de868" rx="1"/>'
        f'<text x="{gx + 78}" y="{leg_y + 8}" font-family="{F}" font-size="7" fill="{C["txt3"]}">dungeon</text>'
    )

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(rects) + legend


def svg_companions_panel(ratio):
    """Companions (AI Collab) panel - party members."""
    px, py, pw, ph = 16, 238, 818, 78
    ix, iy = px + 14, py + 14

    header = svg_section_header(ix, iy + 10, "COMPANIONS")

    total = ratio["total"]
    if total == 0:
        empty = (f'<text x="{ix}" y="{iy + 36}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">No companions have joined your party yet...</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    human_pct = ratio["human"] / total * 100
    ai_pct = ratio["ai"] / total * 100
    bar_w = pw - 28
    bar_x, bar_y, bar_h = ix, iy + 20, 14

    segments = [("Hero", C["green"], ratio["human"])]
    for tool, count in sorted(ratio["tools"].items(), key=lambda x: x[1], reverse=True):
        name = AI_NAMES.get(tool, tool)
        segments.append((name, AI_COLORS.get(tool, C["txt3"]), count))

    parts = [svg_panel(px, py, pw, ph), header,
             f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="#0a1a10" rx="2"/>']

    cx = bar_x
    for i, (name, color, count) in enumerate(segments):
        seg_w = int(count / total * bar_w)
        if i == len(segments) - 1:
            seg_w = bar_w - (cx - bar_x)
        if seg_w < 1:
            continue
        parts.append(
            f'<rect x="{cx}" y="{bar_y}" width="{seg_w}" height="{bar_h}" fill="{color}" opacity="0.8" rx="0">'
            f'<animate attributeName="width" from="0" to="{seg_w}" dur="0.8s" begin="0.3s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1"/></rect>')
        cx += seg_w

    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
                 f'fill="none" stroke="{C["bdr"]}" stroke-width="1" rx="2"/>')

    # Percentage on bar
    if human_pct > 15:
        parts.append(
            f'<text x="{bar_x + int(ratio["human"]/total*bar_w/2)}" y="{bar_y + 11}" '
            f'text-anchor="middle" font-family="{F}" font-size="8" fill="{C["dark"]}" '
            f'font-weight="bold">{human_pct:.0f}%</text>')
    if ai_pct > 10:
        ai_cx = bar_x + int(ratio["human"]/total*bar_w) + int(ratio["ai"]/total*bar_w/2)
        parts.append(
            f'<text x="{ai_cx}" y="{bar_y + 11}" text-anchor="middle" '
            f'font-family="{F}" font-size="8" fill="{C["dark"]}" font-weight="bold">{ai_pct:.0f}%</text>')

    # Legend
    lx = ix
    leg_y = bar_y + bar_h + 14
    for name, color, count in segments:
        pct = count / total * 100
        parts.append(
            f'<rect x="{lx}" y="{leg_y - 7}" width="8" height="8" fill="{color}" rx="1"/>'
            f'<text x="{lx + 12}" y="{leg_y + 1}" font-family="{F}" font-size="9" '
            f'fill="{C["txt"]}">{name} <tspan fill="{C["txt2"]}">{pct:.0f}%</tspan></text>')
        lx += max(len(name) * 8 + 55, 110)

    return "\n    ".join(parts)


def svg_questlog_panel(events):
    """Quest Log: commit history as quest entries."""
    px, py, pw, ph = 16, 326, 818, 190
    ix, iy = px + 14, py + 14

    header = svg_section_header(ix, iy + 10, "QUEST LOG")

    if not events:
        empty = (f'<text x="{ix}" y="{iy + 38}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">No quests recorded yet...</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    rows = []
    for i, ev in enumerate(events):
        ry = iy + 24 + i * 30
        sha = ev["sha"]
        msg = esc(ev["msg"][:48])
        t = reltime(ev["date"])
        repo = esc(ev["repo"][:14])
        rows.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{0.3 + i * 0.15:.2f}s" fill="freeze"/>'
            # Quest marker
            f'<text x="{ix}" y="{ry + 14}" font-family="{F}" font-size="11" fill="{C["green"]}">&#9656;</text>'
            # SHA
            f'<text x="{ix + 16}" y="{ry + 14}" font-family="{F}" font-size="10" fill="{C["gold"]}">{sha}</text>'
            # Repo
            f'<text x="{ix + 80}" y="{ry + 14}" font-family="{F}" font-size="9" fill="{C["txt3"]}">{repo}</text>'
            # Message
            f'<text x="{ix + 200}" y="{ry + 14}" font-family="{F}" font-size="10" fill="{C["txt"]}">{msg}</text>'
            # Time
            f'<text x="{ix + pw - 44}" y="{ry + 14}" font-family="{F}" font-size="9" '
            f'fill="{C["txt3"]}" text-anchor="end">{t}</text>'
            # Separator dot line
            f'<line x1="{ix}" y1="{ry + 22}" x2="{ix + pw - 28}" y2="{ry + 22}" '
            f'stroke="{C["bdr"]}" stroke-width="0.5" stroke-dasharray="2,4" opacity="0.3"/>'
            f'</g>')

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(rows)


def svg_inventory_panel(langs):
    """Inventory: languages as item boxes."""
    px, py, pw, ph = 16, 526, 818, 108
    ix, iy = px + 14, py + 14

    header = svg_section_header(ix, iy + 10, "INVENTORY")

    if not langs:
        empty = (f'<text x="{ix}" y="{iy + 38}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">No items found. Add METRICS_TOKEN to unlock!</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    items = []
    for i, (name, color, pct) in enumerate(langs[:6]):
        col, row = i % 3, i // 3
        bx = ix + col * 260
        by = iy + 22 + row * 38
        bw, bh = 240, 32

        items.append(
            # Item box
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{C["panel"]}" '
            f'stroke="{C["bdr"]}" stroke-width="1" rx="2"/>'
            # Top-left bevel
            f'<line x1="{bx+2}" y1="{by+2}" x2="{bx+bw-2}" y2="{by+2}" '
            f'stroke="{C["panel_hi"]}" stroke-width="0.5" opacity="0.4"/>'
            # Color dot (item icon)
            f'<rect x="{bx + 8}" y="{by + 8}" width="16" height="16" fill="{color}" rx="2" opacity="0.9"/>'
            f'<rect x="{bx + 10}" y="{by + 10}" width="5" height="5" fill="white" opacity="0.3" rx="1"/>'
            # Name
            f'<text x="{bx + 30}" y="{by + 20}" font-family="{F}" font-size="10" '
            f'fill="{C["txt"]}">{name[:12]}</text>'
            # Percentage
            f'<text x="{bx + bw - 10}" y="{by + 20}" font-family="{F}" font-size="10" '
            f'fill="{C["txt2"]}" text-anchor="end">{pct:.1f}%</text>'
        )

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(items)


def svg_footer():
    """Game saved footer with Zelda flair."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    fy = H - 36
    return (
        # Divider
        f'<line x1="16" y1="{fy}" x2="{W-16}" y2="{fy}" stroke="{C["bdr"]}" stroke-width="0.5"/>'
        # Save icon (floppy/book)
        f'<text x="28" y="{fy + 20}" font-family="{F}" font-size="10" fill="{C["green"]}">'
        f'&#9654; GAME SAVED</text>'
        # Blinking cursor
        f'<rect x="150" y="{fy + 10}" width="7" height="12" fill="{C["green"]}" class="cursor"/>'
        # Timestamp
        f'<text x="{W - 22}" y="{fy + 20}" font-family="{F}" font-size="9" '
        f'fill="{C["txt3"]}" text-anchor="end">{now} UTC</text>'
        # Secret message
        f'<text x="{W//2}" y="{fy + 20}" font-family="{F}" font-size="7" '
        f'fill="{C["txt3"]}" text-anchor="middle" opacity="0.4">'
        f'SECRET TO EVERYBODY</text>'
    )


# ══════════════════════════ ASSEMBLE ══════════════════════════

def generate_svg(stats, events, ai_ratio):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {svg_defs()}

  <!-- Zelda double-line border -->
  {svg_zelda_border()}

  <!-- HUD: Hearts + Title + Rupees -->
  {svg_hud(stats)}

  <!-- Row 1: Hero | Status | World Map -->
  {svg_hero_panel(stats)}
  {svg_status_panel(stats)}
  {svg_worldmap_panel(stats["weeks"])}

  <!-- Row 2: Companions (AI Collab) -->
  {svg_companions_panel(ai_ratio)}

  <!-- Row 3: Quest Log (Commits) -->
  {svg_questlog_panel(events)}

  <!-- Row 4: Inventory (Languages) -->
  {svg_inventory_panel(stats["langs"])}

  <!-- Footer -->
  {svg_footer()}
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
