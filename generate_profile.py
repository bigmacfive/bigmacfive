#!/usr/bin/env python3
"""GitHub Profile Dashboard v9 — The Legend of Zelda: A Link to the Past

Authentic ALttP game screen with:
- Real Link sprite (front-facing, 16x15 pixel art)
- Equipment screen layout with gold L-corner ornaments
- 10-heart HUD, rupee counter, key counter
- 8-slot item grid (6 filled + 2 empty)
- Dungeon map heatmap (26 weeks)
- Dialog-box quest log
- CSS-only animations (GitHub compatible)
"""

import json, os, random, urllib.request, urllib.error
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
USERNAME = "bigmacfive"
TOKEN = os.getenv("GITHUB_TOKEN", "")
W, H = 850, 730
FONT = "'Press Start 2P', 'Courier New', monospace"
random.seed(42)

# ═══════════════════════════════════════════════════════════════
# ALttP COLOR PALETTE
# ═══════════════════════════════════════════════════════════════
C = {
    # Background & panels
    "bg":        "#080c14",
    "panel":     "#0d1820",
    "panel_hi":  "#162030",
    "border":    "#0d9263",
    "border_hi": "#4aba91",
    "gold":      "#d4ce46",
    "gold_dark": "#8a7a20",
    # HUD
    "heart":     "#c83030",
    "heart_hi":  "#f06060",
    "heart_e":   "#2a1818",
    "rupee":     "#40b8f0",
    "key":       "#d4ce46",
    # Text
    "text":      "#e6edf3",
    "text_dim":  "#7a9878",
    "text_dark": "#3a5838",
    "title":     "#4aba91",
    "green":     "#38e850",
    # Greens (heatmap)
    "g0":        "#0d1820",
    "g1":        "#0d4a2a",
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
    # Magic / misc
    "magic":     "#4090ff",
    "blush":     "#ff9080",
    "white":     "#ffffff",
    "cursor":    "#e6edf3",
}

# ═══════════════════════════════════════════════════════════════
# LINK SPRITE (16×16, ALttP front-facing)
# 0=transparent, 1=cap, 2=cap_hi, 3=hair, 4=skin, 5=eyes,
# 6=tunic, 7=tunic_hi, 8=belt, 9=boots, A=blush
# ═══════════════════════════════════════════════════════════════
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

# Heart sprite (7×7)
HEART = [
    [0,1,1,0,1,1,0],
    [1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1],
    [0,1,1,1,1,1,0],
    [0,0,1,1,1,0,0],
    [0,0,0,1,0,0,0],
]

# Triforce piece (small, 5×3)
TRIFORCE = [
    [0,0,1,0,0],
    [0,1,1,1,0],
    [1,1,1,1,1],
]

# Sword sprite (5×16)
SWORD = [
    [0,0,1,0,0],
    [0,0,1,0,0],
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
SWORD_COLORS = {1: "#b0b8c8", 2: "#886030", 3: "#d4ce46"}

# Shield sprite (7×8)
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
SHIELD_COLORS = {1: "#1a6b34", 2: "#28a038", 3: "#c83030", 4: "#d4ce46"}

# ═══════════════════════════════════════════════════════════════
# ITEM ICONS (8×8 each, for inventory slots)
# ═══════════════════════════════════════════════════════════════
ITEM_ICONS = {
    "Python": {
        "grid": [
            [0,0,1,1,1,0,0,0],
            [0,1,0,0,0,1,0,0],
            [0,1,0,0,0,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,0,0,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,0,1,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#3572A5",
    },
    "TypeScript": {
        "grid": [
            [1,1,1,1,1,1,1,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#3178c6",
    },
    "JavaScript": {
        "grid": [
            [0,0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0,0],
            [1,0,0,0,0,1,0,0],
            [1,0,0,0,0,1,0,0],
            [0,1,1,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#f1e05a",
    },
    "Rust": {
        "grid": [
            [1,1,1,1,0,0,0,0],
            [1,0,0,0,1,0,0,0],
            [1,0,0,0,1,0,0,0],
            [1,1,1,1,0,0,0,0],
            [1,0,0,1,0,0,0,0],
            [1,0,0,0,1,0,0,0],
            [1,0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#dea584",
    },
    "Go": {
        "grid": [
            [0,1,1,1,1,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,1,1,0,0,0],
            [1,0,0,0,1,0,0,0],
            [1,0,0,0,1,0,0,0],
            [0,1,1,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#00ADD8",
    },
    "Shell": {
        "grid": [
            [0,1,0,0,0,0,0,0],
            [0,0,1,0,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,1,0,0,0,0,0],
            [0,1,1,1,1,1,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#89e051",
    },
    "HTML": {
        "grid": [
            [0,1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,1,1,1,1,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#e34c26",
    },
    "CSS": {
        "grid": [
            [0,1,1,1,1,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0],
            [0,1,1,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "color": "#563d7c",
    },
}

# Default icon for languages not in the map
DEFAULT_ITEM = {
    "grid": [
        [0,0,1,1,1,0,0,0],
        [0,1,0,0,0,1,0,0],
        [0,0,0,0,0,1,0,0],
        [0,0,0,0,1,0,0,0],
        [0,0,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ],
    "color": "#7a9878",
}

# Language display name shortener
LANG_SHORT = {
    "Python": "PY", "TypeScript": "TS", "JavaScript": "JS",
    "Rust": "RST", "Go": "GO", "Shell": "SH",
    "HTML": "HTML", "CSS": "CSS", "Java": "JAVA",
    "C++": "C++", "C": "C", "Ruby": "RB",
    "Swift": "SWF", "Kotlin": "KT", "Dart": "DRT",
    "Lua": "LUA", "PHP": "PHP", "Scala": "SCL",
    "Haskell": "HSK", "Elixir": "ELX", "Zig": "ZIG",
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

    # Streak
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

    # Languages
    lang_map = {}
    for n in nodes:
        for e in (n.get("languages") or {}).get("edges") or []:
            name = e["node"]["name"]
            lang_map[name] = lang_map.get(name, 0) + e["size"]
    total = sum(lang_map.values()) or 1
    langs = sorted(lang_map.items(), key=lambda x: -x[1])[:8]
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
            msg = cm.get("message", "").split("\n")[0][:44]
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
                    # Identify which AI
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
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
    @keyframes blink {{ 0%,45%,55%,100% {{ opacity:1; }} 50% {{ opacity:0; }} }}
    @keyframes pulse {{ 0%,100% {{ opacity:0.6; }} 50% {{ opacity:1; }} }}
    @keyframes cursor-blink {{ 0%,49% {{ opacity:1; }} 50%,100% {{ opacity:0; }} }}
    @keyframes shimmer {{ 0% {{ opacity:0.3; }} 50% {{ opacity:0.8; }} 100% {{ opacity:0.3; }} }}
    @keyframes fadein {{ 0% {{ opacity:0; }} 100% {{ opacity:1; }} }}
    @keyframes sway {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(2px); }} }}
    .float {{ animation: float 3s ease-in-out infinite; }}
    .blink {{ animation: blink 4s ease-in-out infinite; }}
    .pulse {{ animation: pulse 2s ease-in-out infinite; }}
    .cursor {{ animation: cursor-blink 1s step-end infinite; }}
    .shimmer {{ animation: shimmer 3s ease-in-out infinite; }}
    .sway {{ animation: sway 4s ease-in-out infinite; }}
  </style>
</defs>"""

def svg_pixel_grid(matrix, colors, x, y, ps=4, css_class=""):
    """Render a numbered matrix as pixel art SVG rects."""
    rects = []
    cls = f' class="{css_class}"' if css_class else ""
    if css_class:
        rects.append(f'<g{cls}>')
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val and val in colors:
                px, py = x + c * ps, y + r * ps
                rects.append(f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" fill="{colors[val]}" />')
    if css_class:
        rects.append('</g>')
    return "\n".join(rects)

def svg_pixel_heart(x, y, ps=3, filled=True):
    color = C["heart"] if filled else C["heart_e"]
    hi = C["heart_hi"] if filled else C["heart_e"]
    rects = []
    for r, row in enumerate(HEART):
        for c, val in enumerate(row):
            if val:
                px, py = x + c * ps, y + r * ps
                # Highlight on top-left pixels
                fill = hi if filled and r <= 1 and c >= 1 and c <= 2 else color
                rects.append(f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" fill="{fill}" />')
    return "\n".join(rects)

def svg_rupee(x, y, color=None):
    """Small rupee icon (6×10)."""
    c = color or C["rupee"]
    return f"""<polygon points="{x+3},{y} {x+6},{y+3} {x+6},{y+7} {x+3},{y+10} {x},{y+7} {x},{y+3}" fill="{c}" opacity="0.9"/>
<line x1="{x+3}" y1="{y}" x2="{x+3}" y2="{y+10}" stroke="{C['bg']}" stroke-width="0.5" opacity="0.3"/>"""

def svg_key_icon(x, y):
    """Small key icon."""
    return f"""<circle cx="{x+4}" cy="{y+4}" r="3" fill="none" stroke="{C['key']}" stroke-width="1.5"/>
<line x1="{x+7}" y1="{y+4}" x2="{x+14}" y2="{y+4}" stroke="{C['key']}" stroke-width="1.5"/>
<line x1="{x+12}" y1="{y+4}" x2="{x+12}" y2="{y+7}" stroke="{C['key']}" stroke-width="1.5"/>"""

def svg_corner_ornament(x, y, corner="tl", size=8):
    """Gold L-shaped corner ornament (ALttP style)."""
    g = C["gold"]
    gd = C["gold_dark"]
    s = size
    if corner == "tl":
        return f'<path d="M{x},{y+s} L{x},{y} L{x+s},{y}" fill="none" stroke="{g}" stroke-width="2"/><rect x="{x}" y="{y}" width="3" height="3" fill="{g}"/>'
    elif corner == "tr":
        return f'<path d="M{x-s},{y} L{x},{y} L{x},{y+s}" fill="none" stroke="{g}" stroke-width="2"/><rect x="{x-3}" y="{y}" width="3" height="3" fill="{g}"/>'
    elif corner == "bl":
        return f'<path d="M{x},{y-s} L{x},{y} L{x+s},{y}" fill="none" stroke="{g}" stroke-width="2"/><rect x="{x}" y="{y-3}" width="3" height="3" fill="{g}"/>'
    elif corner == "br":
        return f'<path d="M{x-s},{y} L{x},{y} L{x},{y-s}" fill="none" stroke="{g}" stroke-width="2"/><rect x="{x-3}" y="{y-3}" width="3" height="3" fill="{g}"/>'
    return ""

def svg_panel(x, y, w, h, title=""):
    """ALttP style panel with green border + gold corners + optional title."""
    parts = [
        # Background
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{C["panel"]}" />',
        # Border
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="none" stroke="{C["border"]}" stroke-width="2" />',
        # Inner bevel highlight (top-left)
        f'<rect x="{x+2}" y="{y+2}" width="{w-4}" height="{h-4}" rx="1" fill="none" stroke="{C["border_hi"]}" stroke-width="0.5" opacity="0.3" />',
        # Gold corners
        svg_corner_ornament(x+1, y+1, "tl"),
        svg_corner_ornament(x+w-1, y+1, "tr"),
        svg_corner_ornament(x+1, y+h-1, "bl"),
        svg_corner_ornament(x+w-1, y+h-1, "br"),
    ]
    if title:
        tx = x + 14
        parts.append(f'<rect x="{tx-4}" y="{y-5}" width="{len(title)*7+8}" height="10" fill="{C["bg"]}" />')
        parts.append(f'<text x="{tx}" y="{y+3}" font-size="7" fill="{C["gold"]}" letter-spacing="1">{title}</text>')
    return "\n".join(parts)

def svg_outer_border():
    """Double border around the entire card with gold corners."""
    return f"""<rect x="0" y="0" width="{W}" height="{H}" rx="4" fill="{C['bg']}" />
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="3" fill="none" stroke="{C['border']}" stroke-width="2" />
<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="2" fill="none" stroke="{C['border_hi']}" stroke-width="0.5" opacity="0.4" />
{svg_corner_ornament(3, 3, "tl", 12)}
{svg_corner_ornament(W-3, 3, "tr", 12)}
{svg_corner_ornament(3, H-3, "bl", 12)}
{svg_corner_ornament(W-3, H-3, "br", 12)}"""

# ═══════════════════════════════════════════════════════════════
# SVG PANELS
# ═══════════════════════════════════════════════════════════════

def svg_hud(stats):
    """Top HUD bar: hearts + title + rupees + keys."""
    parts = []
    hx, hy = 16, 16

    # Hearts (streak-based: 1 heart per 7 days, max 10)
    num_hearts = min(10, max(1, stats["streak"] // 7 + (1 if stats["streak"] > 0 else 0)))
    for i in range(10):
        filled = i < num_hearts
        parts.append(svg_pixel_heart(hx + i * 24, hy, ps=3, filled=filled))

    # Title
    parts.append(f'<text x="{W//2}" y="{hy + 8}" text-anchor="middle" font-size="10" fill="{C["title"]}" letter-spacing="2">B I G M A C F I V E</text>')

    # Rupees (stars count) - right side
    rx = W - 120
    parts.append(svg_rupee(rx, hy - 2))
    parts.append(f'<text x="{rx + 12}" y="{hy + 8}" font-size="8" fill="{C["rupee"]}">{stats["stars"]:,}</text>')

    # Keys (repos count)
    kx = W - 60
    parts.append(svg_key_icon(kx, hy - 2))
    parts.append(f'<text x="{kx + 18}" y="{hy + 8}" font-size="8" fill="{C["key"]}">{stats["repos"]}</text>')

    # Separator line
    parts.append(f'<line x1="12" y1="42" x2="{W-12}" y2="42" stroke="{C["border"]}" stroke-width="1" opacity="0.6" />')

    return "\n".join(parts)

def svg_equipment_panel(stats):
    """Left panel: Link sprite + RPG stats (like ALttP equipment screen)."""
    px, py, pw, ph = 16, 50, 240, 240
    parts = [svg_panel(px, py, pw, ph, "EQUIPMENT")]

    # Link sprite (centered, with float animation)
    lx = px + (pw - 16 * 4) // 2
    ly = py + 20
    parts.append(svg_pixel_grid(LINK, LINK_COLORS, lx, ly, ps=4, css_class="float"))

    # Sword on left
    sx = lx - 30
    sy = ly + 10
    parts.append(svg_pixel_grid(SWORD, SWORD_COLORS, sx, sy, ps=3))

    # Shield on right
    shx = lx + 16 * 4 + 10
    shy = ly + 20
    parts.append(svg_pixel_grid(SHIELD, SHIELD_COLORS, shx, shy, ps=3))

    # Level badge
    parts.append(f'<text x="{px + pw//2}" y="{ly + 80}" text-anchor="middle" font-size="8" fill="{C["gold"]}">LV.{min(99, stats["commits"] // 100 + 1)}</text>')
    parts.append(f'<text x="{px + pw//2}" y="{ly + 92}" text-anchor="middle" font-size="7" fill="{C["text"]}">{USERNAME.upper()}</text>')

    # Stats section
    sy = py + 140
    stat_items = [
        ("ATK", stats["commits"], C["heart"]),      # Attack = commits
        ("DEF", stats["repos"], C["tunic"]),          # Defense = repos
        ("STR", stats["streak"], C["green"]),         # Strength = streak
        ("LUK", stats["stars"], C["gold"]),            # Luck = stars
        ("WIS", stats["followers"], C["magic"]),       # Wisdom = followers
    ]

    for i, (label, val, color) in enumerate(stat_items):
        sy_row = sy + i * 18
        parts.append(f'<text x="{px + 14}" y="{sy_row}" font-size="7" fill="{C["text_dim"]}">{label}</text>')
        # Dot leaders
        dots_x = px + 50
        parts.append(f'<text x="{dots_x}" y="{sy_row}" font-size="6" fill="{C["text_dark"]}" letter-spacing="2">{"·" * 10}</text>')
        # Value
        val_str = f"{val:,}" if val >= 1000 else str(val)
        parts.append(f'<text x="{px + pw - 16}" y="{sy_row}" text-anchor="end" font-size="7" fill="{color}">{val_str}</text>')

    return "\n".join(parts)

def svg_dungeon_map(weeks):
    """Right panel: contribution heatmap as dungeon room map."""
    px, py, pw, ph = 268, 50, 566, 240
    parts = [svg_panel(px, py, pw, ph, "DUNGEON MAP")]

    # Heatmap grid (26 weeks × 7 days)
    cell = 10
    gap = 2
    total_cell = cell + gap
    display_weeks = weeks[-26:] if len(weeks) >= 26 else weeks
    grid_w = len(display_weeks) * total_cell
    grid_h = 7 * total_cell
    ox = px + (pw - grid_w) // 2
    oy = py + 22

    # Day labels
    day_labels = ["S", "M", "T", "W", "T", "F", "S"]
    for i in range(7):
        if i % 2 == 1:  # Only odd days for space
            parts.append(f'<text x="{ox - 12}" y="{oy + i * total_cell + 8}" font-size="5" fill="{C["text_dark"]}">{day_labels[i]}</text>')

    levels = [C["g0"], C["g1"], C["g2"], C["g3"], C["g4"]]

    for wi, w in enumerate(display_weeks):
        days = w.get("contributionDays") or []
        for di, d in enumerate(days):
            cnt = d.get("contributionCount", 0)
            if cnt == 0:
                lvl = 0
            elif cnt <= 2:
                lvl = 1
            elif cnt <= 5:
                lvl = 2
            elif cnt <= 9:
                lvl = 3
            else:
                lvl = 4
            cx = ox + wi * total_cell
            cy = oy + di * total_cell
            parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="1" fill="{levels[lvl]}" />')
            # Subtle border on filled cells
            if lvl > 0:
                parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="1" fill="none" stroke="{C["border_hi"]}" stroke-width="0.3" opacity="0.3" />')

    # Legend
    ly = oy + grid_h + 12
    parts.append(f'<text x="{ox}" y="{ly}" font-size="5" fill="{C["text_dark"]}">SAFE</text>')
    for i, lv in enumerate(levels):
        lx = ox + 30 + i * 14
        parts.append(f'<rect x="{lx}" y="{ly - 7}" width="10" height="10" rx="1" fill="{lv}" />')
    parts.append(f'<text x="{ox + 30 + 5 * 14}" y="{ly}" font-size="5" fill="{C["text_dark"]}">DUNGEON</text>')

    # Month labels along bottom
    month_names = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    last_month = -1
    for wi, w in enumerate(display_weeks):
        days = w.get("contributionDays") or []
        if days:
            try:
                dt = datetime.fromisoformat(days[0]["date"])
                if dt.month != last_month:
                    last_month = dt.month
                    mx = ox + wi * total_cell
                    parts.append(f'<text x="{mx}" y="{ly + 14}" font-size="5" fill="{C["text_dim"]}">{month_names[dt.month-1]}</text>')
            except Exception:
                pass

    return "\n".join(parts)

def svg_inventory(langs):
    """Item grid panel showing top languages as collectible items."""
    px, py, pw, ph = 16, 302, 818, 108
    parts = [svg_panel(px, py, pw, ph, "- ITEMS -")]

    # 8 slots (6 filled + 2 empty if less than 8 languages)
    num_slots = 8
    slot_w = 90
    slot_h = 72
    slot_gap = 10
    total_w = num_slots * slot_w + (num_slots - 1) * slot_gap
    sox = px + (pw - total_w) // 2
    soy = py + 18

    for i in range(num_slots):
        sx = sox + i * (slot_w + slot_gap)
        sy = soy

        if i < len(langs):
            name, pct = langs[i]
            short = LANG_SHORT.get(name, name[:4].upper())
            icon_data = ITEM_ICONS.get(name, DEFAULT_ITEM)
            icon_color = icon_data["color"]

            # Slot background (filled)
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="2" fill="{C["panel_hi"]}" />')
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="2" fill="none" stroke="{C["border"]}" stroke-width="1" />')

            # Item icon (pixel art)
            icon_grid = icon_data["grid"]
            ips = 4  # pixel size
            icon_w = len(icon_grid[0]) * ips
            icon_x = sx + (slot_w - icon_w) // 2
            icon_y = sy + 6
            for r, row in enumerate(icon_grid):
                for c_, val in enumerate(row):
                    if val:
                        parts.append(f'<rect x="{icon_x + c_ * ips}" y="{icon_y + r * ips}" width="{ips}" height="{ips}" fill="{icon_color}" />')

            # Language name
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + 48}" text-anchor="middle" font-size="6" fill="{C["text"]}">{short}</text>')
            # Percentage
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + 60}" text-anchor="middle" font-size="6" fill="{C["text_dim"]}">{pct:.1f}%</text>')
        else:
            # Empty slot
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="2" fill="{C["bg"]}" />')
            parts.append(f'<rect x="{sx}" y="{sy}" width="{slot_w}" height="{slot_h}" rx="2" fill="none" stroke="{C["text_dark"]}" stroke-width="1" stroke-dasharray="3,3" />')
            parts.append(f'<text x="{sx + slot_w//2}" y="{sy + slot_h//2 + 3}" text-anchor="middle" font-size="7" fill="{C["text_dark"]}">- - -</text>')

    return "\n".join(parts)

def svg_quest_log(events):
    """Dialog-box style quest log showing recent commits."""
    px, py, pw, ph = 16, 422, 818, 170
    parts = [svg_panel(px, py, pw, ph, "QUEST LOG")]

    if not events:
        parts.append(f'<text x="{px + pw//2}" y="{py + ph//2 + 3}" text-anchor="middle" font-size="7" fill="{C["text_dim"]}">NO QUESTS RECORDED...</text>')
        # Dialog box indicator
        parts.append(f'<text x="{px + pw//2}" y="{py + ph - 12}" text-anchor="middle" font-size="8" fill="{C["cursor"]}" class="cursor">▼</text>')
        return "\n".join(parts)

    # Quest entries
    ey = py + 22
    for i, ev in enumerate(events):
        sha = ev["sha"]
        repo = ev["repo"][:12]
        msg = ev["msg"][:36]
        time = reltime(ev["ts"])

        row_y = ey + i * 28

        # Row background (alternating)
        if i % 2 == 0:
            parts.append(f'<rect x="{px + 8}" y="{row_y - 9}" width="{pw - 16}" height="24" rx="1" fill="{C["panel_hi"]}" opacity="0.4" />')

        # Cursor arrow
        parts.append(f'<text x="{px + 14}" y="{row_y + 3}" font-size="7" fill="{C["green"]}">▶</text>')

        # SHA
        parts.append(f'<text x="{px + 30}" y="{row_y + 3}" font-size="6" fill="{C["gold"]}">{sha}</text>')

        # Repo name
        parts.append(f'<text x="{px + 90}" y="{row_y + 3}" font-size="6" fill="{C["border_hi"]}">{repo}</text>')

        # Commit message
        parts.append(f'<text x="{px + 200}" y="{row_y + 3}" font-size="6" fill="{C["text"]}">{msg}</text>')

        # Time
        parts.append(f'<text x="{px + pw - 18}" y="{row_y + 3}" text-anchor="end" font-size="6" fill="{C["text_dim"]}">{time}</text>')

        # Fade-in animation via style
        delay = i * 0.15
        parts.append(f'<style>.quest-{i} {{ animation: fadein 0.5s {delay}s both; }}</style>')

    # Dialog indicator
    parts.append(f'<text x="{px + pw//2}" y="{py + ph - 10}" text-anchor="middle" font-size="8" fill="{C["cursor"]}" class="cursor">▼</text>')

    return "\n".join(parts)

def svg_party(total, ai_count, ai_breakdown):
    """Party/companion bar showing AI collaboration ratio."""
    px, py, pw, ph = 16, 604, 818, 66
    parts = [svg_panel(px, py, pw, ph, "PARTY")]

    bar_x = px + 16
    bar_y = py + 18
    bar_w = pw - 100
    bar_h = 12

    hero_pct = ((total - ai_count) / total * 100) if total > 0 else 100
    ai_pct = (ai_count / total * 100) if total > 0 else 0

    # Bar background
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="2" fill="{C["bg"]}" />')

    # Hero portion
    hero_w = bar_w * hero_pct / 100
    if hero_w > 0:
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{hero_w:.0f}" height="{bar_h}" rx="2" fill="{C["green"]}" />')

    # AI portions
    ax = bar_x + hero_w
    for name, count in sorted(ai_breakdown.items(), key=lambda x: -x[1]):
        seg_pct = count / total * 100 if total > 0 else 0
        seg_w = bar_w * seg_pct / 100
        color = AI_COLORS.get(name, C["magic"])
        if seg_w > 0:
            parts.append(f'<rect x="{ax:.0f}" y="{bar_y}" width="{seg_w:.0f}" height="{bar_h}" rx="0" fill="{color}" />')
            ax += seg_w

    # Bar border
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="2" fill="none" stroke="{C["border"]}" stroke-width="0.5" />')

    # Percentage label
    parts.append(f'<text x="{bar_x + bar_w + 10}" y="{bar_y + 10}" font-size="7" fill="{C["text"]}">{hero_pct:.0f}%</text>')

    # Legend
    ly = bar_y + bar_h + 14
    parts.append(f'<text x="{bar_x}" y="{ly}" font-size="6" fill="{C["green"]}">● HERO {hero_pct:.0f}%</text>')
    lx = bar_x + 100
    for name, count in sorted(ai_breakdown.items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total > 0 else 0
        color = AI_COLORS.get(name, C["magic"])
        parts.append(f'<text x="{lx}" y="{ly}" font-size="6" fill="{color}">● {name} {pct:.0f}%</text>')
        lx += 90

    return "\n".join(parts)

def svg_footer():
    """Bottom footer with game-save style message."""
    fy = H - 38
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    parts = [
        f'<line x1="12" y1="{fy - 6}" x2="{W-12}" y2="{fy - 6}" stroke="{C["border"]}" stroke-width="0.5" opacity="0.4" />',
        # Triforce decoration
        svg_pixel_grid(TRIFORCE, {1: C["gold"]}, 20, fy - 2, ps=3),
        # Game saved text
        f'<text x="46" y="{fy + 8}" font-size="7" fill="{C["gold"]}">▶ GAME SAVED</text>',
        # Blinking cursor
        f'<rect x="152" y="{fy}" width="7" height="10" fill="{C["cursor"]}" class="cursor" />',
        # Quote
        f'<text x="{W//2 + 20}" y="{fy + 8}" text-anchor="middle" font-size="6" fill="{C["text_dim"]}">IT\'S A SECRET TO EVERYBODY</text>',
        # Timestamp
        f'<text x="{W - 20}" y="{fy + 8}" text-anchor="end" font-size="5" fill="{C["text_dark"]}">{now}</text>',
        # Triforce right
        svg_pixel_grid(TRIFORCE, {1: C["gold"]}, W - 38, fy - 2, ps=3),
    ]
    return "\n".join(parts)

def svg_sparkles():
    """Random sparkle particles across the card."""
    parts = []
    for _ in range(20):
        sx = random.randint(20, W - 20)
        sy = random.randint(50, H - 50)
        size = random.choice([1, 1.5, 2])
        delay = random.uniform(0, 5)
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="{size}" fill="{C["gold"]}" opacity="0.15" class="shimmer" style="animation-delay:{delay:.1f}s" />')
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
        svg_equipment_panel(stats),
        svg_dungeon_map(stats["weeks"]),
        svg_inventory(stats["langs"]),
        svg_quest_log(events),
        svg_party(total, ai_count, ai_breakdown),
        svg_footer(),
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
