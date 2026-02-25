#!/usr/bin/env python3
"""GitHub Profile Dashboard v6 — macOS Native

- macOS dark-mode window chrome with traffic lights
- Panel-based layout with rounded corners and subtle borders
- Claude brand colors as accent on native macOS dark palette
- System font stack + monospace for code only
- Clean metric cards, no retro terminal elements
"""

import os, re, requests, random
from datetime import datetime, timezone, timedelta
from html import escape as esc
from math import pi

USERNAME = "bigmacfive"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
W, H = 850, 680
F = "-apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif"
FM = "'SF Mono', 'Menlo', 'Courier New', monospace"

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

C = {
    "win_bg":  "#1a1512",  "titlebar": "#2a2219",
    "panel":   "#221c17",  "panel_bdr": "#3d3028",  "hover": "#2d2520",
    "txt":     "#F5E6D3",  "txt2":     "#9B8672",   "txt3": "#6b5c4d",
    "accent":  "#D97757",  "peach":    "#E8A87C",   "cream": "#F5E6D3",
    "terra":   "#C4703E",
    "body":    "#D97757",  "hi":       "#E8A87C",   "dark": "#1A1410",
    "blush":   "#F0A88C",
    "tl_r":    "#ff5f57",  "tl_y":     "#febc2e",   "tl_g": "#28c840",
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
      @keyframes blink {{ 0%,92%{{opacity:1}} 93%,97%{{opacity:0}} 98%{{opacity:1}} }}
      @keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-5px)}} }}
    </style>
    <linearGradient id="grd" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"><animate attributeName="stop-color" values="#D97757;#E8A87C;#F5E6D3;#C4703E;#D97757" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="50%"><animate attributeName="stop-color" values="#E8A87C;#F5E6D3;#C4703E;#D97757;#E8A87C" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="100%"><animate attributeName="stop-color" values="#F5E6D3;#C4703E;#D97757;#E8A87C;#F5E6D3" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <linearGradient id="hpg"><stop offset="0%" stop-color="#D97757"/><stop offset="100%" stop-color="#E8A87C"/></linearGradient>
    <linearGradient id="xpg"><stop offset="0%" stop-color="#C4703E"/><stop offset="100%" stop-color="#D97757"/></linearGradient>
    <clipPath id="win"><rect width="{W}" height="{H}" rx="12"/></clipPath>
  </defs>'''


def svg_panel(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{C["panel"]}" rx="10" stroke="{C["panel_bdr"]}" stroke-width="0.5"/>')


def svg_panel_header(x, y, title):
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="11" '
            f'fill="{C["txt2"]}" font-weight="600" letter-spacing="0.5">{title}</text>')


def svg_titlebar():
    return (
        # Title bar background
        f'<rect x="0" y="0" width="{W}" height="38" fill="{C["titlebar"]}" clip-path="url(#win)"/>'
        # Bottom edge
        f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{C["panel_bdr"]}" stroke-width="0.5"/>'
        # Traffic lights
        f'<circle cx="32" cy="19" r="6" fill="{C["tl_r"]}"/>'
        f'<circle cx="52" cy="19" r="6" fill="{C["tl_y"]}"/>'
        f'<circle cx="72" cy="19" r="6" fill="{C["tl_g"]}"/>'
        # Window title
        f'<text x="{W//2}" y="23" font-family="{F}" font-size="13" '
        f'fill="{C["txt2"]}" text-anchor="middle" font-weight="500">'
        f'bigmacfive — GitHub Dashboard</text>'
    )


def svg_pet(bx, by, ps=8):
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
    for _ in range(10):
        x, y = bx + random.randint(-8, w + 8), by + random.randint(-8, h + 8)
        r = round(random.uniform(0.8, 2.0), 1)
        dur = round(random.uniform(2, 4), 1)
        begin = round(random.uniform(0, 5), 1)
        col = random.choice(["#D97757", "#E8A87C", "#F5E6D3", "#C4703E"])
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.7;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</circle>')
    return "\n    ".join(parts)


def svg_pet_panel(stats):
    """Pet panel: pixel art + level + HP/XP bars."""
    px, py, pw, ph = 16, 50, 180, 170
    pet_x = px + (pw - 16 * 8) // 2  # center 128px pet in 180px panel
    pet_y = py + 14
    pet = svg_pet(pet_x, pet_y, ps=8)
    sparkles = svg_sparkles(pet_x - 4, pet_y - 4, 128, 104)
    pet_bot = pet_y + 13 * 8  # 104px tall

    commits = stats["commits"]
    hp_w = int(min(commits / max(commits, 1000), 1.0) * 100)
    xp_w = int(min(stats["streak"] / 30, 1.0) * 100)

    return (
        svg_panel(px, py, pw, ph)
        + f'<g class="pet">{pet}</g>'
        + sparkles
        # Level badge
        + f'<text x="{px + pw//2}" y="{pet_bot + 16}" font-family="{F}" font-size="10" '
          f'fill="{C["accent"]}" text-anchor="middle" font-weight="600">LV.{stats["years"]}</text>'
        # HP bar
        + f'<text x="{px + 14}" y="{pet_bot + 34}" font-family="{F}" font-size="8" fill="{C["accent"]}">HP</text>'
        + f'<rect x="{px + 34}" y="{pet_bot + 26}" width="100" height="8" fill="{C["panel_bdr"]}" rx="4"/>'
        + f'<rect x="{px + 34}" y="{pet_bot + 26}" width="{hp_w}" height="8" fill="url(#hpg)" rx="4">'
          f'<animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/></rect>'
        # XP bar
        + f'<text x="{px + 14}" y="{pet_bot + 48}" font-family="{F}" font-size="8" fill="{C["peach"]}">XP</text>'
        + f'<rect x="{px + 34}" y="{pet_bot + 40}" width="100" height="8" fill="{C["panel_bdr"]}" rx="4"/>'
        + f'<rect x="{px + 34}" y="{pet_bot + 40}" width="{xp_w}" height="8" fill="url(#xpg)" rx="4"/>'
    )


def svg_stat_card(x, y, value, label, color, sub_label, pct, delay):
    """Single macOS-style metric card."""
    bar_w = int(min(pct, 1.0) * 220)
    return (
        # Large value
        f'<text x="{x}" y="{y + 20}" font-family="{F}" font-size="20" '
        f'fill="{C["txt"]}" font-weight="700" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay}s" fill="freeze"/>'
        f'{value}</text>'
        # Label
        + f'<text x="{x + 230}" y="{y + 20}" font-family="{F}" font-size="11" '
          f'fill="{C["txt2"]}" text-anchor="end">{label}</text>'
        # Progress bar
        + f'<rect x="{x}" y="{y + 28}" width="230" height="3" fill="{C["panel_bdr"]}" rx="1.5"/>'
        + f'<rect x="{x}" y="{y + 28}" width="{bar_w}" height="3" fill="{color}" rx="1.5" opacity="0">'
          f'<animate attributeName="opacity" from="0" to="0.8" dur="0.8s" begin="{delay + 0.2}s" fill="freeze"/>'
          f'</rect>'
        # Sub-label
        + f'<text x="{x}" y="{y + 44}" font-family="{F}" font-size="9" fill="{C["txt3"]}">{sub_label}</text>'
    )


def svg_stats_panel(stats):
    """Overview panel with 3 metric cards."""
    px, py, pw, ph = 206, 50, 280, 170
    ix, iy = px + 14, py + 14  # inner origin

    header = svg_panel_header(ix, iy + 10, "Overview")

    card1 = svg_stat_card(ix, iy + 20, f'{stats["commits"]:,}', "commits",
                          C["accent"], f'★ {stats["stars"]}  stars', min(stats["commits"] / 2000, 1.0), 0.2)
    card2 = svg_stat_card(ix, iy + 70, f'{stats["streak"]}d', "streak",
                          C["peach"], f'{stats["repos"]} repos', min(stats["streak"] / 30, 1.0), 0.5)
    card3 = svg_stat_card(ix, iy + 120, str(stats["followers"]), "followers",
                          C["cream"], f'joined {stats["years"]}y ago', min(stats["followers"] / 100, 1.0), 0.8)

    return svg_panel(px, py, pw, ph) + header + card1 + card2 + card3


def heatmap_color(n):
    if n == 0: return "#211A14"
    if n <= 2: return "#4A2C1A"
    if n <= 5: return "#7A4528"
    if n <= 9: return "#B85F35"
    return "#D97757"


def svg_heatmap_panel(weeks):
    """Contribution heatmap panel."""
    px, py, pw, ph = 496, 50, 338, 170
    ix, iy = px + 14, py + 14

    header = svg_panel_header(ix, iy + 10, "Contributions")

    recent = weeks[-18:] if weeks else []
    cs, gap = 8, 2
    grid_x = ix + 4
    grid_y = iy + 22
    rects = []
    for wi, wk in enumerate(recent):
        for di, day in enumerate(wk["contributionDays"]):
            x = grid_x + wi * (cs + gap)
            y = grid_y + di * (cs + gap)
            rects.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'fill="{heatmap_color(day["contributionCount"])}" rx="2"/>')

    # Legend
    leg_y = grid_y + 7 * (cs + gap) + 6
    legend = (
        f'<text x="{grid_x}" y="{leg_y + 8}" font-family="{F}" font-size="8" fill="{C["txt3"]}">less</text>'
        f'<rect x="{grid_x + 26}" y="{leg_y}" width="8" height="8" fill="#211A14" rx="1.5"/>'
        f'<rect x="{grid_x + 36}" y="{leg_y}" width="8" height="8" fill="#4A2C1A" rx="1.5"/>'
        f'<rect x="{grid_x + 46}" y="{leg_y}" width="8" height="8" fill="#7A4528" rx="1.5"/>'
        f'<rect x="{grid_x + 56}" y="{leg_y}" width="8" height="8" fill="#B85F35" rx="1.5"/>'
        f'<rect x="{grid_x + 66}" y="{leg_y}" width="8" height="8" fill="#D97757" rx="1.5"/>'
        f'<text x="{grid_x + 78}" y="{leg_y + 8}" font-family="{F}" font-size="8" fill="{C["txt3"]}">more</text>'
    )

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(rects) + legend


def svg_collab_panel(ratio):
    """AI Collaboration panel."""
    px, py, pw, ph = 16, 230, 818, 76
    ix, iy = px + 14, py + 14

    header = svg_panel_header(ix, iy + 10, "AI Collaboration")

    total = ratio["total"]
    if total == 0:
        empty = (f'<text x="{ix}" y="{iy + 36}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">No commit data available</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    human_pct = ratio["human"] / total * 100
    ai_pct = ratio["ai"] / total * 100
    bar_w = pw - 28
    bar_x = ix
    bar_y = iy + 20
    bar_h = 14

    segments = [("Human", C["peach"], ratio["human"])]
    for tool, count in sorted(ratio["tools"].items(), key=lambda x: x[1], reverse=True):
        segments.append((tool, AI_COLORS.get(tool, C["txt3"]), count))

    parts = [
        svg_panel(px, py, pw, ph),
        header,
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{C["panel_bdr"]}" rx="7"/>',
    ]

    # Segments
    cx = bar_x
    for i, (name, color, count) in enumerate(segments):
        seg_w = int(count / total * bar_w)
        if i == len(segments) - 1:
            seg_w = bar_w - (cx - bar_x)
        if seg_w < 1:
            continue
        parts.append(
            f'<rect x="{cx}" y="{bar_y}" width="{seg_w}" height="{bar_h}" fill="{color}" opacity="0.85" rx="0">'
            f'<animate attributeName="width" from="0" to="{seg_w}" dur="0.8s" begin="0.3s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1"/></rect>')
        cx += seg_w

    # Border overlay
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
                 f'fill="none" stroke="{C["panel_bdr"]}" stroke-width="0.5" rx="7"/>')

    # Percentage on bar
    if human_pct > 15:
        parts.append(
            f'<text x="{bar_x + int(ratio["human"]/total*bar_w/2)}" y="{bar_y + 11}" '
            f'text-anchor="middle" font-family="{F}" font-size="9" fill="{C["dark"]}" '
            f'font-weight="600">{human_pct:.0f}%</text>')
    if ai_pct > 10:
        ai_cx = bar_x + int(ratio["human"]/total*bar_w) + int(ratio["ai"]/total*bar_w/2)
        parts.append(
            f'<text x="{ai_cx}" y="{bar_y + 11}" text-anchor="middle" '
            f'font-family="{F}" font-size="9" fill="{C["dark"]}" font-weight="600">{ai_pct:.0f}%</text>')

    # Legend
    lx = ix
    leg_y = bar_y + bar_h + 14
    for name, color, count in segments:
        pct = count / total * 100
        parts.append(
            f'<circle cx="{lx + 4}" cy="{leg_y - 3}" r="4" fill="{color}"/>'
            f'<text x="{lx + 13}" y="{leg_y + 1}" font-family="{F}" font-size="10" '
            f'fill="{C["txt"]}">{name} <tspan fill="{C["txt2"]}">{pct:.0f}%</tspan></text>')
        lx += max(len(name) * 8 + 60, 120)

    return "\n    ".join(parts)


def svg_commits_panel(events):
    """Recent Commits panel."""
    px, py, pw, ph = 16, 316, 818, 190
    ix, iy = px + 14, py + 14

    header = svg_panel_header(ix, iy + 10, "Recent Commits")

    if not events:
        empty = (f'<text x="{ix}" y="{iy + 38}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">No recent public commits</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    rows = []
    for i, ev in enumerate(events):
        ry = iy + 22 + i * 32
        sha = ev["sha"]
        msg = esc(ev["msg"][:52])
        t = reltime(ev["date"])
        repo = esc(ev["repo"][:16])
        rows.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{0.3 + i * 0.15:.2f}s" fill="freeze"/>'
            # Row background
            f'<rect x="{ix}" y="{ry}" width="{pw - 28}" height="28" fill="{C["hover"]}" rx="6" opacity="0.4"/>'
            # SHA
            f'<text x="{ix + 10}" y="{ry + 18}" font-family="{FM}" font-size="11" fill="{C["accent"]}">{sha}</text>'
            # Repo
            f'<text x="{ix + 80}" y="{ry + 18}" font-family="{F}" font-size="10" fill="{C["txt2"]}">{repo}</text>'
            # Message
            f'<text x="{ix + 200}" y="{ry + 18}" font-family="{F}" font-size="11" fill="{C["txt"]}">{msg}</text>'
            # Time
            f'<text x="{ix + pw - 44}" y="{ry + 18}" font-family="{F}" font-size="9" '
            f'fill="{C["txt3"]}" text-anchor="end">{t}</text>'
            f'</g>')

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(rows)


def svg_langs_panel(langs):
    """Languages panel."""
    px, py, pw, ph = 16, 516, 818, 104
    ix, iy = px + 14, py + 14

    header = svg_panel_header(ix, iy + 10, "Languages")

    if not langs:
        empty = (f'<text x="{ix}" y="{iy + 36}" font-family="{F}" font-size="10" '
                 f'fill="{C["txt3"]}">Add METRICS_TOKEN secret for private repo data</text>')
        return svg_panel(px, py, pw, ph) + header + empty

    bars = []
    for i, (name, color, pct) in enumerate(langs[:6]):
        col, row = i // 3, i % 3
        lx = ix + col * 390
        ly = iy + 22 + row * 24
        bw = max(int(pct * 1.6), 3)
        bars.append(
            f'<circle cx="{lx + 5}" cy="{ly + 7}" r="4.5" fill="{color}"/>'
            f'<text x="{lx + 16}" y="{ly + 11}" font-family="{F}" font-size="10" fill="{C["txt"]}">{name[:14]}</text>'
            f'<rect x="{lx + 120}" y="{ly + 1}" width="150" height="10" fill="{C["panel_bdr"]}" rx="5"/>'
            f'<rect x="{lx + 120}" y="{ly + 1}" width="{bw}" height="10" fill="{color}" rx="5"/>'
            f'<text x="{lx + 278}" y="{ly + 11}" font-family="{F}" font-size="10" fill="{C["txt2"]}">{pct:.1f}%</text>')

    return svg_panel(px, py, pw, ph) + header + "\n      ".join(bars)


def svg_footer():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f'<text x="{W - 20}" y="{H - 12}" font-family="{F}" font-size="9" '
        f'fill="{C["txt3"]}" text-anchor="end">Updated {now}</text>'
    )


# ══════════════════════════ ASSEMBLE ══════════════════════════

def generate_svg(stats, events, ai_ratio):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {svg_defs()}

  <!-- Window -->
  <rect width="{W}" height="{H}" fill="{C['win_bg']}" rx="12"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="url(#grd)" stroke-width="1.5" rx="11"/>

  <!-- Title bar -->
  {svg_titlebar()}

  <!-- Row 1: Pet | Stats | Heatmap -->
  {svg_pet_panel(stats)}
  {svg_stats_panel(stats)}
  {svg_heatmap_panel(stats["weeks"])}

  <!-- Row 2: AI Collaboration -->
  {svg_collab_panel(ai_ratio)}

  <!-- Row 3: Recent Commits -->
  {svg_commits_panel(events)}

  <!-- Row 4: Languages -->
  {svg_langs_panel(stats["langs"])}

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
