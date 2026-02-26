#!/usr/bin/env python3
"""GitHub Profile Dashboard v10 — The Legend of Zelda: A Link to the Past

Authentic ALttP game screen — large, readable, beautiful.
- Bigger Link sprite (ps=6), larger fonts (8-14px)
- Spacious layout with thick panel borders
- CRT scanline overlay, gradient panel backgrounds
- CSS-only animations (GitHub SVG compatible)
"""

import json, os, random, urllib.request, urllib.error
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
USERNAME = "bigmacfive"
TOKEN = os.getenv("GITHUB_TOKEN", "")
W, H = 850, 880
FONT = "'Press Start 2P', 'Courier New', monospace"
random.seed(42)

# ═══════════════════════════════════════════════════════════════
# ALttP COLOR PALETTE
# ═══════════════════════════════════════════════════════════════
C = {
    # Background & panels
    "bg":        "#080810",
    "panel":     "#0e1a24",
    "panel_hi":  "#162030",
    "panel_top": "#1a2840",
    "border":    "#0d9263",
    "border_hi": "#4aba91",
    "border_lo": "#06553a",
    "gold":      "#d4ce46",
    "gold_hi":   "#f0ea80",
    "gold_dark": "#8a7a20",
    # HUD
    "heart":     "#d03030",
    "heart_hi":  "#f06868",
    "heart_e":   "#281818",
    "rupee":     "#40b8f0",
    "key":       "#d4ce46",
    # Text
    "text":      "#e8eef4",
    "text_dim":  "#6a9068",
    "text_dark": "#3a5838",
    "title":     "#4aba91",
    "green":     "#38e850",
    # Greens (heatmap)
    "g0":        "#101820",
    "g1":        "#0d5030",
    "g2":        "#0d9263",
    "g3":        "#38c878",
    "g4":        "#80ff98",
    # Link sprite
    "cap":       "#1a8a1e",
    "cap_hi":    "#38c848",
    "hair":      "#e8b830",
    "skin":      "#f0b878",
    "eyes":      "#183018",
    "tunic":     "#28a038",
    "tunic_hi":  "#48c858",
    "belt":      "#886030",
    "boots":     "#604020",
    # Misc
    "magic":     "#4090ff",
    "blush":     "#ff9080",
    "white":     "#ffffff",
    "cursor":    "#e8eef4",
}

# ═══════════════════════════════════════════════════════════════
# PIXEL ART SPRITES
# ═══════════════════════════════════════════════════════════════

# Link (16×16, ALttP front-facing)
# 0=transparent, 1=cap, 2=cap_hi, 3=hair, 4=skin, 5=eyes,
# 6=tunic, 7=tunic_hi, 8=belt, 9=boots, 10=blush
LINK = [
    [0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,1,2,2,2,2,1,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
    [0,0,0,3,3,1,1,1,1,1,1,3,3,0,0,0],
    [0,0,3,3,4,4,4,4,4,4,4,4,3,3,0,0],
    [0,0,3,4,4,5,4,4,4,4,5,4,4,3,0,0],
    [0,0,0,4,4,4,4,4,4,4,4,4,4,0,0,0],
    [0,0,0,0,4,4,10,4,4,10,4,4,0,0,0],
    [0,0,0,0,0,6,6,6,6,6,6,0,0,0,0,0],
    [0,0,0,0,6,7,6,6,6,6,7,6,0,0,0,0],
    [0,0,0,6,6,6,8,8,8,8,6,6,6,0,0,0],
    [0,0,0,6,6,6,6,6,6,6,6,6,6,0,0,0],
    [0,0,0,0,0,6,6,0,0,6,6,0,0,0,0,0],
    [0,0,0,0,0,4,4,0,0,4,4,0,0,0,0,0],
    [0,0,0,0,9,9,9,0,0,9,9,9,0,0,0,0],
]
LINK_COLORS = {
    1: C["cap"], 2: C["cap_hi"], 3: C["hair"], 4: C["skin"],
    5: C["eyes"], 6: C["tunic"], 7: C["tunic_hi"], 8: C["belt"],
    9: C["boots"], 10: C["blush"],
}

# Heart (7×7)
HEART = [
    [0,1,1,0,1,1,0],
    [1,2,1,1,1,2,1],
    [1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1],
    [0,1,1,1,1,1,0],
    [0,0,1,1,1,0,0],
    [0,0,0,1,0,0,0],
]

# Triforce (5×3)
TRIFORCE = [
    [0,0,1,0,0],
    [0,1,1,1,0],
    [1,1,1,1,1],
]

# Sword (5×14)
SWORD = [
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,1,1,1,0],
    [0,1,1,1,0],
    [1,1,2,1,1],
    [0,0,2,0,0],
    [0,0,2,0,0],
    [0,0,2,0,0],
    [0,0,3,0,0],
    [0,0,3,0,0],
]
SWORD_COLORS = {1: "#c0c8d8", 2: "#886030", 3: "#d4ce46"}

# Shield (7×8)
SHIELD = [
    [0,1,1,1,1,1,0],
    [1,2,2,2,2,2,1],
    [1,2,3,3,3,2,1],
    [1,2,3,4,3,2,1],
    [1,2,3,4,3,2,1],
    [1,2,3,3,3,2,1],
    [1,2,2,2,2,2,1],
    [0,1,1,1,1,1,0],
]
SHIELD_COLORS = {1: "#1a6b34", 2: "#28a038", 3: "#d03030", 4: "#d4ce46"}

# ═══════════════════════════════════════════════════════════════
# LANGUAGE CONFIG
# ═══════════════════════════════════════════════════════════════

LANG_SHORT = {
    "Python": "PY", "TypeScript": "TS", "JavaScript": "JS",
    "Rust": "RST", "Go": "GO", "Shell": "SH",
    "HTML": "HTML", "CSS": "CSS", "Java": "JAVA",
    "C++": "C++", "C": "C", "Ruby": "RB",
    "Swift": "SWF", "Kotlin": "KT", "Dart": "DRT",
    "Lua": "LUA", "PHP": "PHP", "Scala": "SCL",
    "Haskell": "HSK", "Elixir": "ELX", "Zig": "ZIG",
    "Vue": "VUE", "Svelte": "SVT", "SCSS": "SCSS",
}

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Rust": "#dea584", "Go": "#00ADD8", "Shell": "#89e051",
    "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219",
    "C++": "#f34b7d", "C": "#555555", "Ruby": "#701516",
    "Swift": "#F05138", "Kotlin": "#A97BFF", "Dart": "#00B4AB",
    "Lua": "#000080", "PHP": "#4F5D95", "Scala": "#c22d40",
    "Haskell": "#5e5086", "Elixir": "#6e4a7e", "Zig": "#ec915c",
    "Vue": "#41b883", "Svelte": "#ff3e00", "SCSS": "#c6538c",
}

# AI collaboration patterns
AI_PATTERNS = [
    r"(?i)co-?authored-?by:.*\b(claude|copilot|gpt|gemini|cursor|codeium|tabnine|amazon.?q)\b",
    r"(?i)\b(ai|llm|copilot|claude|gpt|cursor)\s*(assisted|generated|paired|helped)",
    r"(?i)🤖",
]
AI_NAMES = {"claude": "NAVI", "copilot": "TATL", "gpt": "TAEL", "gemini": "MIDNA",
            "cursor": "FI", "codeium": "EZLO", "tabnine": "CIELA"}
AI_COLORS = {"NAVI": "#4090ff", "TATL": "#40b8f0", "TAEL": "#c070ff",
             "MIDNA": "#38c878", "FI": "#d4ce46", "EZLO": "#0d9263", "CIELA": "#ff9080"}

# ═══════════════════════════════════════════════════════════════
# DATA FETCHING
# ═══════════════════════════════════════════════════════════════

def gql(query, variables=None):
    body = json.dumps({"query": query, **({"variables": variables} if variables else {})}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"GraphQL error: {e}")
        return {}

def fetch_stats():
    q = """query($u:String!){
      user(login:$u){
        repositories(ownerAffiliations:OWNER,first:100,orderBy:{field:STARGAZERS,direction:DESC}){
          totalCount
          nodes{stargazerCount languages(first:5,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}
        }
        followers{totalCount}
        contributionsCollection{
          totalCommitContributions
          contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}
        }
      }
    }"""
    data = gql(q, {"u": USERNAME})
    u = (data.get("data") or {}).get("user") or {}
    repos_data = u.get("repositories") or {}
    repos = repos_data.get("totalCount", 0)
    nodes = repos_data.get("nodes") or []
    stars = sum(n.get("stargazerCount", 0) for n in nodes)
    followers = (u.get("followers") or {}).get("totalCount", 0)
    cc = u.get("contributionsCollection") or {}
    commits = cc.get("totalCommitContributions", 0)
    cal = (cc.get("contributionCalendar") or {})
    total_contributions = cal.get("totalContributions", 0)
    weeks = cal.get("weeks") or []

    streak = 0
    for w in reversed(weeks):
        for d in reversed(w.get("contributionDays") or []):
            if d.get("contributionCount", 0) > 0:
                streak += 1
            else:
                if streak > 0:
                    break
        else:
            continue
        break

    lang_map = {}
    for n in nodes:
        for e in (n.get("languages") or {}).get("edges") or []:
            name = e["node"]["name"]
            lang_map[name] = lang_map.get(name, 0) + e["size"]
    total = sum(lang_map.values()) or 1
    langs = sorted(lang_map.items(), key=lambda x: -x[1])[:6]
    langs = [(name, size / total * 100) for name, size in langs]

    return {
        "repos": repos, "stars": stars, "followers": followers,
        "commits": commits, "streak": streak, "total": total_contributions,
        "langs": langs, "weeks": weeks,
    }

def fetch_events():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            events = json.loads(r.read())
    except Exception:
        return []
    result = []
    import re
    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        repo = (ev.get("repo") or {}).get("name", "").split("/")[-1]
        for cm in (ev.get("payload") or {}).get("commits") or []:
            sha = cm.get("sha", "")[:7]
            msg = cm.get("message", "").split("\n")[0][:40]
            ts = ev.get("created_at", "")
            result.append({"sha": sha, "repo": repo, "msg": msg, "ts": ts})
    return result[:5]

def fetch_ai_ratio():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=100"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            events = json.loads(r.read())
    except Exception:
        return 0, 0, {}
    import re
    total = 0
    ai_count = 0
    ai_breakdown = {}
    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        for cm in (ev.get("payload") or {}).get("commits") or []:
            total += 1
            msg = cm.get("message", "")
            for pat in AI_PATTERNS:
                m = re.search(pat, msg)
                if m:
                    ai_count += 1
                    text = msg.lower()
                    matched = False
                    for keyword, name in AI_NAMES.items():
                        if keyword in text:
                            ai_breakdown[name] = ai_breakdown.get(name, 0) + 1
                            matched = True
                            break
                    if not matched:
                        ai_breakdown["NAVI"] = ai_breakdown.get("NAVI", 0) + 1
                    break
    return total, ai_count, ai_breakdown

def reltime(iso):
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - dt
        s = int(diff.total_seconds())
        if s < 60:
            return "now"
        if s < 3600:
            return f"{s // 60}m"
        if s < 86400:
            return f"{s // 3600}h"
        d = s // 86400
        if d == 1:
            return "1d"
        if d < 30:
            return f"{d}d"
        return f"{d // 30}mo"
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════
# SVG PRIMITIVES
# ═══════════════════════════════════════════════════════════════

def svg_defs():
    return f"""<defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;display=swap');
    text {{ font-family: {FONT}; }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}
    @keyframes cursor-blink {{ 0%,49% {{ opacity:1; }} 50%,100% {{ opacity:0; }} }}
    @keyframes shimmer {{ 0% {{ opacity:0.2; }} 50% {{ opacity:0.7; }} 100% {{ opacity:0.2; }} }}
    @keyframes glow {{ 0%,100% {{ opacity:0.4; }} 50% {{ opacity:0.8; }} }}
    @keyframes pulse {{ 0%,100% {{ opacity:0.6; }} 50% {{ opacity:1; }} }}
    .float {{ animation: float 3s ease-in-out infinite; }}
    .cursor {{ animation: cursor-blink 1s step-end infinite; }}
    .shimmer {{ animation: shimmer 4s ease-in-out infinite; }}
    .glow {{ animation: glow 3s ease-in-out infinite; }}
    .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  </style>
  <linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{C['panel_top']}" />
    <stop offset="100%" stop-color="{C['panel']}" />
  </linearGradient>
  <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{C['border']}" />
    <stop offset="100%" stop-color="{C['border_hi']}" />
  </linearGradient>
  <filter id="glow-gold">
    <feGaussianBlur stdDeviation="2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scanlines" patternUnits="userSpaceOnUse" width="2" height="2">
    <rect width="2" height="1" fill="black" opacity="0.06"/>
  </pattern>
</defs>"""

def svg_pixel_grid(matrix, colors, x, y, ps=4, css_class=""):
    rects = []
    cls = f' class="{css_class}"' if css_class else ""
    if css_class:
        rects.append(f'<g{cls}>')
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val and val in colors:
                px, py_ = x + c * ps, y + r * ps
                rects.append(f'<rect x="{px}" y="{py_}" width="{ps}" height="{ps}" fill="{colors[val]}"/>')
    if css_class:
        rects.append('</g>')
    return "\n".join(rects)

def svg_pixel_heart(x, y, ps=4, filled=True):
    color = C["heart"] if filled else C["heart_e"]
    hi = C["heart_hi"] if filled else C["heart_e"]
    rects = []
    for r, row in enumerate(HEART):
        for c, val in enumerate(row):
            if val:
                px, py_ = x + c * ps, y + r * ps
                fill = hi if filled and val == 2 else color
                if not filled:
                    fill = C["heart_e"]
                rects.append(f'<rect x="{px}" y="{py_}" width="{ps}" height="{ps}" fill="{fill}"/>')
    return "\n".join(rects)

def svg_rupee(x, y, size=14):
    """Rupee gem icon."""
    s = size
    hw = s * 0.4
    return f"""<polygon points="{x+hw},{y} {x+s*0.8},{y+s*0.3} {x+s*0.8},{y+s*0.7} {x+hw},{y+s} {x},{y+s*0.7} {x},{y+s*0.3}" fill="{C['rupee']}" opacity="0.9"/>
<polygon points="{x+hw},{y} {x+hw},{y+s} {x+s*0.8},{y+s*0.7} {x+s*0.8},{y+s*0.3}" fill="{C['rupee']}" opacity="0.6"/>"""

def svg_key_icon(x, y, size=16):
    """Key icon."""
    return f"""<circle cx="{x+5}" cy="{y+5}" r="4.5" fill="none" stroke="{C['key']}" stroke-width="2"/>
<line x1="{x+9}" y1="{y+5}" x2="{x+size}" y2="{y+5}" stroke="{C['key']}" stroke-width="2"/>
<line x1="{x+14}" y1="{y+5}" x2="{x+14}" y2="{y+9}" stroke="{C['key']}" stroke-width="2"/>"""

def svg_corner(x, y, corner="tl", size=10):
    """Gold L-shaped corner ornament."""
    g = C["gold"]
    s = size
    if corner == "tl":
        return f'<path d="M{x},{y+s} L{x},{y} L{x+s},{y}" fill="none" stroke="{g}" stroke-width="2.5"/><rect x="{x-1}" y="{y-1}" width="4" height="4" fill="{g}" rx="1"/>'
    elif corner == "tr":
        return f'<path d="M{x-s},{y} L{x},{y} L{x},{y+s}" fill="none" stroke="{g}" stroke-width="2.5"/><rect x="{x-2}" y="{y-1}" width="4" height="4" fill="{g}" rx="1"/>'
    elif corner == "bl":
        return f'<path d="M{x},{y-s} L{x},{y} L{x+s},{y}" fill="none" stroke="{g}" stroke-width="2.5"/><rect x="{x-1}" y="{y-2}" width="4" height="4" fill="{g}" rx="1"/>'
    elif corner == "br":
        return f'<path d="M{x-s},{y} L{x},{y} L{x},{y-s}" fill="none" stroke="{g}" stroke-width="2.5"/><rect x="{x-2}" y="{y-2}" width="4" height="4" fill="{g}" rx="1"/>'
    return ""

def svg_panel(x, y, w, h, title=""):
    """ALttP panel: gradient bg, thick green border, gold corners, inset title."""
    parts = [
        # Gradient background
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="url(#panelGrad)"/>',
        # Outer border (thick)
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="none" stroke="{C["border_lo"]}" stroke-width="3"/>',
        # Mid border
        f'<rect x="{x+1.5}" y="{y+1.5}" width="{w-3}" height="{h-3}" rx="2" fill="none" stroke="{C["border"]}" stroke-width="1.5"/>',
        # Inner highlight (top edge glow)
        f'<rect x="{x+3}" y="{y+3}" width="{w-6}" height="{h-6}" rx="1" fill="none" stroke="{C["border_hi"]}" stroke-width="0.5" opacity="0.25"/>',
        # Gold corners
        svg_corner(x+2, y+2, "tl"),
        svg_corner(x+w-2, y+2, "tr"),
        svg_corner(x+2, y+h-2, "bl"),
        svg_corner(x+w-2, y+h-2, "br"),
    ]
    if title:
        tx = x + 18
        tw = len(title) * 8 + 16
        parts.append(f'<rect x="{tx-6}" y="{y-7}" width="{tw}" height="14" rx="2" fill="{C["bg"]}"/>')
        parts.append(f'<text x="{tx}" y="{y+4}" font-size="9" fill="{C["gold"]}" letter-spacing="1">{title}</text>')
    return "\n".join(parts)

def svg_outer_border():
    """Double border around the entire card."""
    return f"""<rect x="0" y="0" width="{W}" height="{H}" rx="6" fill="{C['bg']}"/>
<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="4" fill="none" stroke="{C['border_lo']}" stroke-width="3"/>
<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="3" fill="none" stroke="{C['border']}" stroke-width="1.5"/>
<rect x="9" y="9" width="{W-18}" height="{H-18}" rx="2" fill="none" stroke="{C['border_hi']}" stroke-width="0.5" opacity="0.3"/>
{svg_corner(4, 4, "tl", 14)}
{svg_corner(W-4, 4, "tr", 14)}
{svg_corner(4, H-4, "bl", 14)}
{svg_corner(W-4, H-4, "br", 14)}"""

def svg_scanlines():
    """CRT scanline overlay."""
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#scanlines)" rx="6"/>'

def svg_sparkles():
    """Subtle gold sparkle particles."""
    parts = []
    for _ in range(15):
        sx = random.randint(30, W - 30)
        sy = random.randint(60, H - 60)
        size = random.choice([1.5, 2, 2.5])
        delay = random.uniform(0, 6)
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="{size}" fill="{C["gold"]}" opacity="0.12" class="shimmer" style="animation-delay:{delay:.1f}s"/>')
    return "\n".join(parts)

# ═══════════════════════════════════════════════════════════════
# SVG PANELS
# ═══════════════════════════════════════════════════════════════

def svg_hud(stats):
    """Top HUD: hearts, title, rupee/key counters."""
    parts = []
    hy = 20

    # ── Hearts (5 hearts, ps=4 → 28×28 each) ──
    num_hearts = min(5, max(1, stats["streak"] // 7 + (1 if stats["streak"] > 0 else 0)))
    for i in range(5):
        filled = i < num_hearts
        parts.append(svg_pixel_heart(20 + i * 34, hy, ps=4, filled=filled))

    # ── Title (centered, large) ──
    parts.append(f'<text x="{W//2}" y="{hy + 14}" text-anchor="middle" font-size="13" fill="{C["title"]}" letter-spacing="3" filter="url(#glow-gold)">BIGMACFIVE</text>')

    # ── Rupee counter (stars) ──
    rx = W - 155
    parts.append(svg_rupee(rx, hy + 1, size=16))
    parts.append(f'<text x="{rx + 20}" y="{hy + 14}" font-size="10" fill="{C["rupee"]}">{stats["stars"]:,}</text>')

    # ── Key counter (repos) ──
    kx = W - 72
    parts.append(svg_key_icon(kx, hy + 1, size=18))
    parts.append(f'<text x="{kx + 22}" y="{hy + 14}" font-size="10" fill="{C["key"]}">{stats["repos"]}</text>')

    # ── Separator ──
    parts.append(f'<line x1="14" y1="54" x2="{W-14}" y2="54" stroke="{C["border"]}" stroke-width="1.5" opacity="0.5"/>')
    # Glow on separator
    parts.append(f'<line x1="14" y1="54" x2="{W-14}" y2="54" stroke="{C["border_hi"]}" stroke-width="0.5" opacity="0.2"/>')

    return "\n".join(parts)

def svg_equipment(stats):
    """Left panel: Link sprite + stats."""
    px, py, pw, ph = 18, 64, 270, 300
    parts = [svg_panel(px, py, pw, ph, "EQUIPMENT")]

    # ── Link sprite (ps=6, 96×96, centered) ──
    lx = px + (pw - 16 * 6) // 2
    ly = py + 18
    parts.append(svg_pixel_grid(LINK, LINK_COLORS, lx, ly, ps=6, css_class="float"))

    # ── Sword (left of Link, ps=4) ──
    sx = lx - 32
    sy = ly + 14
    parts.append(svg_pixel_grid(SWORD, SWORD_COLORS, sx, sy, ps=4))

    # ── Shield (right of Link, ps=4) ──
    shx = lx + 16 * 6 + 10
    shy = ly + 28
    parts.append(svg_pixel_grid(SHIELD, SHIELD_COLORS, shx, shy, ps=4))

    # ── Level + name ──
    cy = ly + 104
    lvl = min(99, stats["commits"] // 100 + 1)
    parts.append(f'<text x="{px + pw//2}" y="{cy}" text-anchor="middle" font-size="10" fill="{C["gold_hi"]}">LV. {lvl}</text>')
    parts.append(f'<text x="{px + pw//2}" y="{cy + 16}" text-anchor="middle" font-size="9" fill="{C["text"]}">{USERNAME.upper()}</text>')

    # ── Stats ──
    sy = py + 160
    stat_items = [
        ("ATK", stats["commits"], C["heart"]),
        ("DEF", stats["repos"], C["tunic"]),
        ("STR", stats["streak"], C["green"]),
        ("LUK", stats["stars"], C["gold"]),
        ("WIS", stats["followers"], C["magic"]),
    ]

    for i, (label, val, color) in enumerate(stat_items):
        row_y = sy + i * 24
        parts.append(f'<text x="{px + 18}" y="{row_y}" font-size="9" fill="{C["text_dim"]}">{label}</text>')
        # Dot leaders
        parts.append(f'<text x="{px + 60}" y="{row_y}" font-size="7" fill="{C["text_dark"]}" letter-spacing="3">{"·" * 12}</text>')
        # Value
        val_str = f"{val:,}" if val >= 1000 else str(val)
        parts.append(f'<text x="{px + pw - 20}" y="{row_y}" text-anchor="end" font-size="9" fill="{color}">{val_str}</text>')

    return "\n".join(parts)

def svg_dungeon_map(weeks):
    """Right panel: heatmap as dungeon map."""
    px, py, pw, ph = 300, 64, 532, 300
    parts = [svg_panel(px, py, pw, ph, "DUNGEON MAP")]

    cell = 13
    gap = 3
    step = cell + gap
    display_weeks = weeks[-22:] if len(weeks) >= 22 else weeks
    grid_w = len(display_weeks) * step
    grid_h = 7 * step
    ox = px + (pw - grid_w) // 2
    oy = py + 28

    # Day labels
    days = ["S", "M", "T", "W", "T", "F", "S"]
    for i in range(7):
        if i % 2 == 1:
            parts.append(f'<text x="{ox - 16}" y="{oy + i * step + 10}" font-size="7" fill="{C["text_dark"]}">{days[i]}</text>')

    levels = [C["g0"], C["g1"], C["g2"], C["g3"], C["g4"]]

    for wi, w in enumerate(display_weeks):
        for di, d in enumerate(w.get("contributionDays") or []):
            cnt = d.get("contributionCount", 0)
            lvl = 0 if cnt == 0 else (1 if cnt <= 2 else (2 if cnt <= 5 else (3 if cnt <= 9 else 4)))
            cx = ox + wi * step
            cy = oy + di * step
            parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2" fill="{levels[lvl]}"/>')
            if lvl > 0:
                parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2" fill="none" stroke="{C["border_hi"]}" stroke-width="0.4" opacity="0.25"/>')

    # Legend
    ly = oy + grid_h + 16
    parts.append(f'<text x="{ox}" y="{ly}" font-size="7" fill="{C["text_dark"]}">SAFE</text>')
    for i, lv in enumerate(levels):
        lx = ox + 38 + i * 18
        parts.append(f'<rect x="{lx}" y="{ly - 9}" width="13" height="13" rx="2" fill="{lv}"/>')
    parts.append(f'<text x="{ox + 38 + 5 * 18 + 2}" y="{ly}" font-size="7" fill="{C["text_dark"]}">DUNGEON</text>')

    # Month labels
    month_names = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    last_month = -1
    for wi, w in enumerate(display_weeks):
        d_list = w.get("contributionDays") or []
        if d_list:
            try:
                dt = datetime.fromisoformat(d_list[0]["date"])
                if dt.month != last_month:
                    last_month = dt.month
                    mx = ox + wi * step
                    parts.append(f'<text x="{mx}" y="{ly + 18}" font-size="7" fill="{C["text_dim"]}">{month_names[dt.month-1]}</text>')
            except Exception:
                pass

    return "\n".join(parts)

def svg_items(langs):
    """Item grid: 6 language slots, ALttP inventory style."""
    px, py, pw, ph = 18, 376, 814, 130
    parts = [svg_panel(px, py, pw, ph, "- I T E M S -")]

    num_slots = 6
    slot_w = 120
    slot_h = 94
    total_w = num_slots * slot_w + (num_slots - 1) * 12
    sox = px + (pw - total_w) // 2
    soy = py + 20

    for i in range(num_slots):
        sx = sox + i * (slot_w + 12)
        sy = soy

        if i < len(langs):
            name, pct = langs[i]
            short = LANG_SHORT.get(name, name[:4].upper())
            color = LANG_COLORS.get(name, "#7a9878")

            # Slot bg
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="3" fill="{C["panel_hi"]}"/>')
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="3" fill="none" stroke="{C["border"]}" stroke-width="1.5"/>')

            # Color swatch (big colored square as "item")
            swatch_size = 32
            swx = sx + (slot_w - swatch_size) // 2
            swy = sy + 8
            parts.append(f'<rect x="{swx}" y="{swy}" width="{swatch_size}" height="{swatch_size}" rx="4" fill="{color}" opacity="0.85"/>')
            # Inner diamond highlight
            cx_ = swx + swatch_size // 2
            cy_ = swy + swatch_size // 2
            parts.append(f'<rect x="{cx_-6}" y="{cy_-6}" width="12" height="12" rx="2" fill="white" opacity="0.15" transform="rotate(45 {cx_} {cy_})"/>')

            # Language name
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + 54}" text-anchor="middle" font-size="8" fill="{C["text"]}">{short}</text>')
            # Percentage
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + 70}" text-anchor="middle" font-size="8" fill="{color}">{pct:.1f}%</text>')

            # Small bar
            bar_w = slot_w - 20
            bar_x = sx + 10
            bar_y = sy + 78
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="4" rx="2" fill="{C["bg"]}"/>')
            fill_w = max(2, bar_w * pct / 100)
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{fill_w:.0f}" height="4" rx="2" fill="{color}" opacity="0.7"/>')
        else:
            # Empty slot
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="3" fill="{C["bg"]}"/>')
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="3" fill="none" stroke="{C["text_dark"]}" stroke-width="1" stroke-dasharray="4,4"/>')
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + slot_h//2 + 4}" text-anchor="middle" font-size="10" fill="{C["text_dark"]}">- -</text>')

    return "\n".join(parts)

def svg_quest_log(events):
    """Dialog-box quest log."""
    px, py, pw, ph = 18, 518, 814, 200
    parts = [svg_panel(px, py, pw, ph, "QUEST LOG")]

    if not events:
        parts.append(f'<text x="{px + pw//2}" y="{py + ph//2}" text-anchor="middle" font-size="9" fill="{C["text_dim"]}">NO QUESTS RECORDED...</text>')
        parts.append(f'<text x="{px + pw//2}" y="{py + ph - 16}" text-anchor="middle" font-size="10" fill="{C["cursor"]}" class="cursor">▼</text>')
        return "\n".join(parts)

    ey = py + 28
    row_h = 32

    for i, ev in enumerate(events):
        sha = ev["sha"]
        repo = ev["repo"][:14]
        msg = ev["msg"][:32]
        time = reltime(ev["ts"])

        row_y = ey + i * row_h

        # Alternating row bg
        if i % 2 == 0:
            parts.append(f'<rect x="{px + 10}" y="{row_y - 10}" width="{pw - 20}" height="{row_h - 2}" rx="2" fill="{C["panel_hi"]}" opacity="0.35"/>')

        # Arrow cursor
        parts.append(f'<text x="{px + 18}" y="{row_y + 4}" font-size="9" fill="{C["green"]}">▶</text>')

        # SHA
        parts.append(f'<text x="{px + 38}" y="{row_y + 4}" font-size="8" fill="{C["gold"]}">{sha}</text>')

        # Repo
        parts.append(f'<text x="{px + 110}" y="{row_y + 4}" font-size="8" fill="{C["border_hi"]}">{repo}</text>')

        # Message
        parts.append(f'<text x="{px + 248}" y="{row_y + 4}" font-size="8" fill="{C["text"]}">{msg}</text>')

        # Time
        parts.append(f'<text x="{px + pw - 22}" y="{row_y + 4}" text-anchor="end" font-size="8" fill="{C["text_dim"]}">{time}</text>')

    # Dialog indicator
    parts.append(f'<text x="{px + pw//2}" y="{py + ph - 14}" text-anchor="middle" font-size="10" fill="{C["cursor"]}" class="cursor">▼</text>')

    return "\n".join(parts)

def svg_party(total, ai_count, ai_breakdown):
    """Party bar: AI collaboration ratio."""
    px, py, pw, ph = 18, 730, 814, 80
    parts = [svg_panel(px, py, pw, ph, "PARTY")]

    bar_x = px + 20
    bar_y = py + 22
    bar_w = pw - 120
    bar_h = 16

    hero_pct = ((total - ai_count) / total * 100) if total > 0 else 100

    # Bar bg
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="3" fill="{C["bg"]}"/>')
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="3" fill="none" stroke="{C["border_lo"]}" stroke-width="0.5"/>')

    # Hero portion
    hero_w = bar_w * hero_pct / 100
    if hero_w > 0:
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{hero_w:.0f}" height="{bar_h}" rx="3" fill="{C["green"]}" opacity="0.8"/>')

    # AI portions
    ax = bar_x + hero_w
    for name, count in sorted(ai_breakdown.items(), key=lambda x: -x[1]):
        seg_pct = count / total * 100 if total > 0 else 0
        seg_w = bar_w * seg_pct / 100
        color = AI_COLORS.get(name, C["magic"])
        if seg_w > 1:
            parts.append(f'<rect x="{ax:.0f}" y="{bar_y}" width="{seg_w:.0f}" height="{bar_h}" fill="{color}" opacity="0.8"/>')
            ax += seg_w

    # Percentage label
    parts.append(f'<text x="{bar_x + bar_w + 14}" y="{bar_y + 12}" font-size="9" fill="{C["text"]}">{hero_pct:.0f}%</text>')

    # Legend
    ly = bar_y + bar_h + 18
    parts.append(f'<text x="{bar_x}" y="{ly}" font-size="8" fill="{C["green"]}">● HERO {hero_pct:.0f}%</text>')
    lx = bar_x + 130
    for name, count in sorted(ai_breakdown.items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total > 0 else 0
        color = AI_COLORS.get(name, C["magic"])
        parts.append(f'<text x="{lx}" y="{ly}" font-size="8" fill="{color}">● {name} {pct:.0f}%</text>')
        lx += 120

    return "\n".join(parts)

def svg_footer():
    """Game-save footer."""
    fy = H - 44
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    parts = [
        f'<line x1="16" y1="{fy - 6}" x2="{W-16}" y2="{fy - 6}" stroke="{C["border"]}" stroke-width="0.5" opacity="0.3"/>',
        # Triforce left
        svg_pixel_grid(TRIFORCE, {1: C["gold"]}, 24, fy, ps=4),
        # Game saved
        f'<text x="52" y="{fy + 10}" font-size="9" fill="{C["gold"]}">▶ GAME SAVED</text>',
        # Blinking cursor
        f'<rect x="175" y="{fy}" width="9" height="12" fill="{C["cursor"]}" class="cursor"/>',
        # Secret quote
        f'<text x="{W//2 + 30}" y="{fy + 10}" text-anchor="middle" font-size="8" fill="{C["text_dim"]}">IT\'S A SECRET TO EVERYBODY</text>',
        # Timestamp
        f'<text x="{W - 24}" y="{fy + 10}" text-anchor="end" font-size="7" fill="{C["text_dark"]}">{now}</text>',
        # Triforce right
        svg_pixel_grid(TRIFORCE, {1: C["gold"]}, W - 46, fy, ps=4),
    ]
    return "\n".join(parts)

# ═══════════════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════════════

def generate_svg(stats, events, total, ai_count, ai_breakdown):
    sections = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        svg_defs(),
        svg_outer_border(),
        svg_sparkles(),
        svg_hud(stats),
        svg_equipment(stats),
        svg_dungeon_map(stats["weeks"]),
        svg_items(stats["langs"]),
        svg_quest_log(events),
        svg_party(total, ai_count, ai_breakdown),
        svg_footer(),
        svg_scanlines(),
        "</svg>",
    ]
    return "\n".join(sections)

def main():
    print(f"Generating profile card for {USERNAME}...")

    if TOKEN:
        stats = fetch_stats()
        events = fetch_events()
        total, ai_count, ai_breakdown = fetch_ai_ratio()
    else:
        print("No GITHUB_TOKEN — using placeholder data")
        stats = {
            "repos": 42, "stars": 89, "followers": 15,
            "commits": 1234, "streak": 28, "total": 1500,
            "langs": [("Python", 45.2), ("TypeScript", 23.1), ("Rust", 12.4),
                      ("Go", 8.7), ("Shell", 6.2), ("HTML", 4.4)],
            "weeks": [{"contributionDays": [
                {"contributionCount": random.randint(0, 12), "date": f"2025-01-{d+1:02d}"}
                for d in range(7)
            ]} for _ in range(26)],
        }
        events = [
            {"sha": "a1b2c3f", "repo": "bigmacfive", "msg": "feat: add zelda dashboard theme", "ts": "2025-01-15T10:00:00Z"},
            {"sha": "d4e5f6a", "repo": "dotfiles", "msg": "fix: update shell aliases", "ts": "2025-01-14T08:00:00Z"},
            {"sha": "g7h8i9j", "repo": "api-server", "msg": "refactor: clean up middleware", "ts": "2025-01-13T06:00:00Z"},
            {"sha": "k0l1m2n", "repo": "bigmacfive", "msg": "chore: update dependencies", "ts": "2025-01-12T12:00:00Z"},
            {"sha": "o3p4q5r", "repo": "webapp", "msg": "feat: implement dark mode toggle", "ts": "2025-01-11T15:00:00Z"},
        ]
        total, ai_count, ai_breakdown = 100, 35, {"NAVI": 30, "TATL": 5}

    svg = generate_svg(stats, events, total, ai_count, ai_breakdown)
    with open("profile.svg", "w") as f:
        f.write(svg)
    print(f"Done! profile.svg ({len(svg):,} bytes)")

if __name__ == "__main__":
    main()
