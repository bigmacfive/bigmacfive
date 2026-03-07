#!/usr/bin/env python3
"""Generate a clean, game-framed GitHub profile SVG."""

import base64
import json
import os
import random
import urllib.request
from datetime import datetime, timezone
from html import escape


USERNAME = "bigmacfive"
TOKEN = os.getenv("GITHUB_TOKEN", "")
W, H = 850, 900
FONT = "'Pretendard', 'Segoe UI', Arial, sans-serif"
FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "Pretendard-Regular.subset.woff2",
)
DISPLAY_NAME = "Bigmacfive"
PROFILE_TAGLINE = "Building clean products with code, systems, and taste."
PROFILE_INTRO = [
    "Focused on shipping, iteration, and long-term craft.",
    "I care about clear interfaces, useful systems, and durable execution.",
]
random.seed(42)


C = {
    "bg": "#07111a",
    "bg_hi": "#102235",
    "panel": "#0f1b2a",
    "panel_hi": "#132337",
    "panel_line": "#1f3850",
    "border": "#215b67",
    "border_hi": "#56c1a0",
    "gold": "#d5bf74",
    "gold_hi": "#f2df9e",
    "text": "#f3f7fb",
    "text_dim": "#b6c4d3",
    "text_muted": "#6b8398",
    "green": "#4cc28d",
    "blue": "#65a8ff",
    "red": "#ef7676",
    "shadow": "#041019",
    "g0": "#0f1722",
    "g1": "#123a31",
    "g2": "#1b6d58",
    "g3": "#30a97b",
    "g4": "#74ddb0",
}


LINK = [
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 2, 3, 4, 3, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 2, 3, 3, 3, 3, 3, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 2, 2, 3, 3, 3, 2, 2, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 5, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5, 0, 0, 0],
    [0, 0, 0, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 6, 5, 0, 0, 0],
    [0, 0, 0, 5, 7, 9, 7, 7, 7, 7, 9, 7, 7, 7, 5, 0, 0, 0],
    [0, 0, 0, 17, 7, 7, 7, 7, 8, 7, 7, 7, 7, 17, 0, 0, 0, 0],
    [0, 0, 0, 0, 8, 7, 7, 8, 8, 8, 7, 7, 8, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 10, 12, 10, 10, 10, 10, 12, 10, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 7, 10, 10, 10, 10, 10, 10, 10, 10, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 7, 10, 10, 10, 10, 10, 10, 10, 10, 7, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 11, 10, 13, 14, 14, 13, 10, 11, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 11, 10, 10, 10, 10, 10, 10, 11, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 11, 10, 10, 10, 10, 10, 10, 11, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 10, 10, 0, 0, 10, 10, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 0, 0, 7, 7, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 7, 7, 0, 0, 7, 7, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 16, 15, 15, 0, 0, 15, 15, 16, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 16, 15, 15, 15, 15, 15, 15, 16, 0, 0, 0, 0, 0, 0],
]

LINK_COLORS = {
    1: "#0b5515",
    2: "#1f8f26",
    3: "#2cb53e",
    4: "#5fdc74",
    5: "#d4aa2f",
    6: "#ae8a27",
    7: "#f0ba83",
    8: "#d69d67",
    9: "#17331a",
    10: "#2ca142",
    11: "#1f7332",
    12: "#57cd6c",
    13: "#8a6438",
    14: "#e0ca62",
    15: "#76522c",
    16: "#42260f",
    17: "#e1a06a",
}

HEART = [
    [0, 1, 1, 0, 1, 1, 0],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
]

TRIFORCE = [
    [0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
]


LANG_SHORT = {
    "Python": "PY",
    "TypeScript": "TS",
    "JavaScript": "JS",
    "Rust": "RST",
    "Go": "GO",
    "Shell": "SH",
    "HTML": "HTML",
    "CSS": "CSS",
    "Java": "JAVA",
    "C++": "C++",
    "C": "C",
    "Ruby": "RB",
    "Swift": "SWF",
    "Kotlin": "KT",
    "Dart": "DRT",
    "Lua": "LUA",
    "PHP": "PHP",
    "Scala": "SCL",
    "Haskell": "HSK",
    "Elixir": "ELX",
    "Zig": "ZIG",
    "Vue": "VUE",
    "Svelte": "SVT",
    "SCSS": "SCSS",
}

LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Rust": "#dea584",
    "Go": "#00ADD8",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Lua": "#000080",
    "PHP": "#4F5D95",
    "Scala": "#c22d40",
    "Haskell": "#5e5086",
    "Elixir": "#6e4a7e",
    "Zig": "#ec915c",
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
    "SCSS": "#c6538c",
}


AI_PATTERNS = [
    r"(?i)co-?authored-?by:.*\b(claude|copilot|gpt|gemini|cursor|codeium|tabnine|amazon.?q)\b",
    r"(?i)\b(ai|llm|copilot|claude|gpt|cursor)\s*(assisted|generated|paired|helped)",
    r"(?i)🤖",
]
AI_NAMES = {
    "claude": "Claude",
    "copilot": "Copilot",
    "gpt": "GPT",
    "gemini": "Gemini",
    "cursor": "Cursor",
    "codeium": "Codeium",
    "tabnine": "Tabnine",
    "amazon q": "Amazon Q",
    "amazonq": "Amazon Q",
}
AI_COLORS = {
    "Claude": "#65a8ff",
    "Copilot": "#50c878",
    "GPT": "#bb86fc",
    "Gemini": "#f4b75d",
    "Cursor": "#d5bf74",
    "Codeium": "#4db8ff",
    "Tabnine": "#ff8d7a",
    "Amazon Q": "#7ad9d0",
}


def e(value):
    return escape(str(value), quote=False)


def fmt_number(value):
    return f"{value:,}"


def truncate(text, limit):
    text = text or ""
    return text if len(text) <= limit else text[: limit - 1] + "…"


def embed_font_css():
    if not os.path.exists(FONT_PATH):
        return ""
    with open(FONT_PATH, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode("ascii")
    return (
        "@font-face {"
        "font-family:'Pretendard';"
        f"src:url(data:font/woff2;base64,{font_b64}) format('woff2');"
        "font-style:normal;"
        "font-weight:400;"
        "}"
    )


def gql(query, variables=None):
    body = json.dumps(
        {"query": query, **({"variables": variables} if variables else {})}
    ).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as err:
        print(f"GraphQL error: {err}")
        return {}


def fetch_stats():
    query = """query($u:String!){
      user(login:$u){
        repositories(ownerAffiliations:OWNER,first:100,orderBy:{field:STARGAZERS,direction:DESC}){
          totalCount
          nodes{
            stargazerCount
            languages(first:5,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}
          }
        }
        followers{totalCount}
        contributionsCollection{
          totalCommitContributions
          contributionCalendar{
            totalContributions
            weeks{contributionDays{contributionCount date}}
          }
        }
      }
    }"""
    data = gql(query, {"u": USERNAME})
    user = (data.get("data") or {}).get("user") or {}
    repos_data = user.get("repositories") or {}
    nodes = repos_data.get("nodes") or []

    repos = repos_data.get("totalCount", 0)
    stars = sum(node.get("stargazerCount", 0) for node in nodes)
    followers = (user.get("followers") or {}).get("totalCount", 0)
    contributions = user.get("contributionsCollection") or {}
    commit_total = contributions.get("totalCommitContributions", 0)
    calendar = contributions.get("contributionCalendar") or {}
    total_contributions = calendar.get("totalContributions", 0)
    weeks = calendar.get("weeks") or []

    streak = 0
    for week in reversed(weeks):
        for day in reversed(week.get("contributionDays") or []):
            if day.get("contributionCount", 0) > 0:
                streak += 1
            elif streak > 0:
                break
        else:
            continue
        break

    lang_map = {}
    for node in nodes:
        for edge in (node.get("languages") or {}).get("edges") or []:
            name = edge["node"]["name"]
            lang_map[name] = lang_map.get(name, 0) + edge["size"]
    total_size = sum(lang_map.values()) or 1
    langs = sorted(lang_map.items(), key=lambda item: -item[1])[:6]
    langs = [(name, size / total_size * 100) for name, size in langs]

    return {
        "repos": repos,
        "stars": stars,
        "followers": followers,
        "commits": commit_total,
        "streak": streak,
        "total": total_contributions,
        "langs": langs,
        "weeks": weeks,
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
    for event in events:
        if event.get("type") != "PushEvent":
            continue
        repo = (event.get("repo") or {}).get("name", "").split("/")[-1]
        for commit in (event.get("payload") or {}).get("commits") or []:
            result.append(
                {
                    "sha": commit.get("sha", "")[:7],
                    "repo": repo,
                    "msg": commit.get("message", "").split("\n")[0],
                    "ts": event.get("created_at", ""),
                }
            )
    return result[:5]


def fetch_ai_ratio():
    import re

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

    total = 0
    ai_count = 0
    ai_breakdown = {}

    for event in events:
        if event.get("type") != "PushEvent":
            continue
        for commit in (event.get("payload") or {}).get("commits") or []:
            total += 1
            msg = commit.get("message", "")
            for pattern in AI_PATTERNS:
                if not re.search(pattern, msg):
                    continue
                ai_count += 1
                lowered = msg.lower()
                matched = False
                for keyword, label in AI_NAMES.items():
                    if keyword in lowered:
                        ai_breakdown[label] = ai_breakdown.get(label, 0) + 1
                        matched = True
                        break
                if not matched:
                    ai_breakdown["AI"] = ai_breakdown.get("AI", 0) + 1
                break

    return total, ai_count, ai_breakdown


def reltime(iso_text):
    if not iso_text:
        return ""
    try:
        dt = datetime.fromisoformat(iso_text.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "now"
        if seconds < 3600:
            return f"{seconds // 60}m"
        if seconds < 86400:
            return f"{seconds // 3600}h"
        days = seconds // 86400
        if days == 1:
            return "1d"
        if days < 30:
            return f"{days}d"
        return f"{days // 30}mo"
    except Exception:
        return ""


def svg_defs():
    return f"""<defs>
  <style>
    {embed_font_css()}
    svg {{ shape-rendering: geometricPrecision; text-rendering: geometricPrecision; }}
    text, tspan {{
      font-family: {FONT};
      letter-spacing: -0.05em;
    }}
    .float {{ animation: float 4s ease-in-out infinite; }}
    @keyframes float {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-4px); }}
    }}
  </style>
  <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{C['bg_hi']}" />
    <stop offset="100%" stop-color="{C['bg']}" />
  </linearGradient>
  <linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{C['panel_hi']}" />
    <stop offset="100%" stop-color="{C['panel']}" />
  </linearGradient>
  <linearGradient id="accentGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{C['border_hi']}" />
    <stop offset="100%" stop-color="{C['gold']}" />
  </linearGradient>
  <filter id="panelShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="{C['shadow']}" flood-opacity="0.55" />
  </filter>
  <filter id="softBlur" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="50" />
  </filter>
</defs>"""


def svg_pixel_grid(matrix, colors, x, y, ps=4, css_class=""):
    parts = []
    if css_class:
        parts.append(f'<g class="{css_class}">')
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            if value and value in colors:
                px = x + col_index * ps
                py = y + row_index * ps
                parts.append(
                    f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" fill="{colors[value]}"/>'
                )
    if css_class:
        parts.append("</g>")
    return "\n".join(parts)


def svg_pixel_heart(x, y, ps=3, filled=True):
    fill = C["red"] if filled else C["panel_line"]
    hi = "#ffc0c0" if filled else C["panel_line"]
    parts = []
    for row_index, row in enumerate(HEART):
        for col_index, value in enumerate(row):
            if not value:
                continue
            px = x + col_index * ps
            py = y + row_index * ps
            color = hi if value == 2 else fill
            parts.append(
                f'<rect x="{px}" y="{py}" width="{ps}" height="{ps}" fill="{color}"/>'
            )
    return "\n".join(parts)


def svg_card(x, y, w, h):
    return "\n".join(
        [
            f'<g filter="url(#panelShadow)">',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#panelGrad)"/>',
            "</g>",
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{C["panel_line"]}" stroke-width="1.2"/>',
            f'<rect x="{x+1.5}" y="{y+1.5}" width="{w-3}" height="{h-3}" rx="16.5" fill="none" stroke="{C["border"]}" stroke-width="1"/>',
            f'<rect x="{x+10}" y="{y+10}" width="{w-20}" height="{h-20}" rx="12" fill="none" stroke="{C["border_hi"]}" stroke-width="0.5" opacity="0.18"/>',
        ]
    )


def svg_panel(x, y, w, h, title, kicker):
    parts = [svg_card(x, y, w, h)]
    parts.append(
        f'<text x="{x+20}" y="{y+22}" font-size="9" fill="{C["text_muted"]}">{e(kicker)}</text>'
    )
    parts.append(
        f'<text x="{x+20}" y="{y+40}" font-size="14" font-weight="600" fill="{C["text"]}">{e(title)}</text>'
    )
    parts.append(
        f'<line x1="{x+20}" y1="{y+54}" x2="{x+w-20}" y2="{y+54}" stroke="url(#accentGrad)" stroke-width="1"/>'
    )
    return "\n".join(parts)


def svg_metric_card(x, y, w, h, label, value, accent):
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["bg"]}" opacity="0.55"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{accent}" stroke-width="1"/>',
        f'<text x="{x+14}" y="{y+16}" font-size="9" fill="{C["text_muted"]}">{e(label)}</text>',
        f'<text x="{x+14}" y="{y+34}" font-size="16" font-weight="600" fill="{accent}">{e(value)}</text>',
    ]
    return "\n".join(parts)


def svg_background():
    return "\n".join(
        [
            f'<rect x="0" y="0" width="{W}" height="{H}" rx="28" fill="url(#bgGrad)"/>',
            f'<circle cx="120" cy="90" r="140" fill="{C["border_hi"]}" opacity="0.08" filter="url(#softBlur)"/>',
            f'<circle cx="760" cy="180" r="180" fill="{C["gold_hi"]}" opacity="0.06" filter="url(#softBlur)"/>',
            f'<circle cx="700" cy="760" r="160" fill="{C["blue"]}" opacity="0.05" filter="url(#softBlur)"/>',
            f'<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="22" fill="none" stroke="{C["panel_line"]}" stroke-width="1.4"/>',
            f'<rect x="18" y="18" width="{W-36}" height="{H-36}" rx="18" fill="none" stroke="{C["border"]}" stroke-width="0.9" opacity="0.8"/>',
        ]
    )


def svg_header(stats):
    px, py, pw, ph = 18, 18, 814, 126
    right_x = px + 534
    card_w = 116
    card_h = 40
    level = min(99, max(1, stats["commits"] // 100 + 1))

    parts = [svg_card(px, py, pw, ph)]
    parts.append(
        f'<text x="{px+24}" y="{py+24}" font-size="10" fill="{C["text_muted"]}">GitHub profile</text>'
    )
    parts.append(
        f'<text x="{px+24}" y="{py+50}" font-size="30" font-weight="700" fill="{C["text"]}">{e(DISPLAY_NAME)}</text>'
    )
    parts.append(
        f'<text x="{px+24}" y="{py+70}" font-size="11" fill="{C["gold"]}">@{e(USERNAME)} · Level {level}</text>'
    )
    parts.append(
        f'<text x="{px+24}" y="{py+92}" font-size="13" font-weight="600" fill="{C["border_hi"]}">{e(PROFILE_TAGLINE)}</text>'
    )
    parts.append(
        f'<text x="{px+24}" y="{py+110}" font-size="11" fill="{C["text_dim"]}">{e(PROFILE_INTRO[0])}</text>'
    )
    parts.append(
        f'<text x="{px+24}" y="{py+126}" font-size="11" fill="{C["text_dim"]}">{e(PROFILE_INTRO[1])}</text>'
    )

    cards = [
        ("Contributions", fmt_number(stats["total"]), C["border_hi"]),
        ("Streak", f'{stats["streak"]}d', C["gold"]),
        ("Stars", fmt_number(stats["stars"]), C["blue"]),
        ("Repos", str(stats["repos"]), C["green"]),
    ]
    for index, (label, value, accent) in enumerate(cards):
        row = index // 2
        col = index % 2
        cx = right_x + col * (card_w + 12)
        cy = py + 20 + row * (card_h + 10)
        parts.append(svg_metric_card(cx, cy, card_w, card_h, label, value, accent))

    parts.append(
        f'<text x="{right_x}" y="{py+118}" font-size="10" fill="{C["text_muted"]}">Updated daily from public GitHub activity.</text>'
    )
    return "\n".join(parts)


def svg_profile(stats):
    px, py, pw, ph = 18, 160, 262, 258
    showcase_x = px + 20
    showcase_y = py + 72
    showcase_w = 94
    showcase_h = 122
    link_ps = 4
    link_w = 18 * link_ps
    link_h = 22 * link_ps
    link_x = showcase_x + (showcase_w - link_w) // 2
    link_y = showcase_y + 10
    streak_hearts = min(5, max(1, stats["streak"] // 7 + (1 if stats["streak"] else 0)))
    facts_x = px + 134
    facts = [
        ("Followers", fmt_number(stats["followers"])),
        ("Commits", fmt_number(stats["commits"])),
        ("Languages", str(len(stats["langs"]))),
        ("Current streak", f'{stats["streak"]} days'),
    ]

    parts = [svg_panel(px, py, pw, ph, "Profile", "About")]
    parts.extend(
        [
            f'<rect x="{showcase_x}" y="{showcase_y}" width="{showcase_w}" height="{showcase_h}" rx="14" fill="{C["bg"]}" opacity="0.6"/>',
            f'<rect x="{showcase_x}" y="{showcase_y}" width="{showcase_w}" height="{showcase_h}" rx="14" fill="none" stroke="{C["panel_line"]}" stroke-width="1"/>',
            svg_pixel_grid(LINK, LINK_COLORS, link_x, link_y, ps=link_ps, css_class="float"),
            f'<text x="{showcase_x+16}" y="{showcase_y+112}" font-size="9" fill="{C["text_muted"]}">Current streak</text>',
        ]
    )
    for index in range(5):
        parts.append(
            svg_pixel_heart(showcase_x + 14 + index * 15, showcase_y + 124, ps=2, filled=index < streak_hearts)
        )

    parts.append(
        f'<text x="{facts_x}" y="{py+80}" font-size="10" fill="{C["gold"]}">@{e(USERNAME)}</text>'
    )
    parts.append(
        f'<text x="{facts_x}" y="{py+102}" font-size="11" fill="{C["text_dim"]}">Focused on product quality, speed, and long-term maintainability.</text>'
    )

    start_y = py + 132
    for index, (label, value) in enumerate(facts):
        row_y = start_y + index * 28
        parts.append(
            f'<text x="{facts_x}" y="{row_y}" font-size="9" fill="{C["text_muted"]}">{e(label)}</text>'
        )
        parts.append(
            f'<text x="{px+pw-20}" y="{row_y}" text-anchor="end" font-size="12" font-weight="600" fill="{C["text"]}">{e(value)}</text>'
        )
        if index < len(facts) - 1:
            parts.append(
                f'<line x1="{facts_x}" y1="{row_y+12}" x2="{px+pw-20}" y2="{row_y+12}" stroke="{C["panel_line"]}" stroke-width="1"/>'
            )
    return "\n".join(parts)


def svg_activity(stats):
    px, py, pw, ph = 296, 160, 536, 258
    display_weeks = stats["weeks"][-24:] if len(stats["weeks"]) >= 24 else stats["weeks"]
    cell = 14
    gap = 4
    step = cell + gap
    ox = px + 56
    oy = py + 92
    levels = [C["g0"], C["g1"], C["g2"], C["g3"], C["g4"]]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    total_weeks_width = len(display_weeks) * step
    grid_x = ox + max(0, (pw - 80 - total_weeks_width) // 2)
    legend_x = px + pw - 146
    legend_y = py + ph - 24

    parts = [svg_panel(px, py, pw, ph, "Activity", "Contribution heatmap")]
    parts.append(
        f'<text x="{px+20}" y="{py+74}" font-size="10" fill="{C["text_muted"]}">This year</text>'
    )
    parts.append(
        f'<text x="{px+86}" y="{py+74}" font-size="12" font-weight="600" fill="{C["border_hi"]}">{fmt_number(stats["total"])} contributions</text>'
    )
    parts.append(
        f'<text x="{px+pw-20}" y="{py+74}" text-anchor="end" font-size="10" fill="{C["text_muted"]}">Latest 24 weeks</text>'
    )

    for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        parts.append(
            f'<text x="{grid_x-16}" y="{oy + row * step + 10}" text-anchor="end" font-size="9" fill="{C["text_muted"]}">{label}</text>'
        )

    last_month = None
    for week_index, week in enumerate(display_weeks):
        days = week.get("contributionDays") or []
        if days:
            try:
                dt = datetime.fromisoformat(days[0]["date"])
                if dt.month != last_month:
                    last_month = dt.month
                    parts.append(
                        f'<text x="{grid_x + week_index * step}" y="{oy-12}" font-size="9" fill="{C["text_muted"]}">{month_names[dt.month-1]}</text>'
                    )
            except Exception:
                pass

        for day_index, day in enumerate(days):
            count = day.get("contributionCount", 0)
            level = 0 if count == 0 else (1 if count <= 2 else (2 if count <= 5 else (3 if count <= 9 else 4)))
            cx = grid_x + week_index * step
            cy = oy + day_index * step
            parts.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="4" fill="{levels[level]}"/>'
            )
            if level > 0:
                parts.append(
                    f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="4" fill="none" stroke="{C["border_hi"]}" stroke-width="0.5" opacity="0.18"/>'
                )

    parts.append(
        f'<text x="{legend_x-30}" y="{legend_y+9}" font-size="9" fill="{C["text_muted"]}">Low</text>'
    )
    for index, color in enumerate(levels):
        lx = legend_x + index * 18
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="14" height="14" rx="4" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{legend_x + 5 * 18 + 8}" y="{legend_y+9}" font-size="9" fill="{C["text_muted"]}">High</text>'
    )
    return "\n".join(parts)


def svg_stack(langs):
    px, py, pw, ph = 18, 434, 814, 124
    card_w = 118
    card_h = 54
    gap = 12
    start_x = px + (pw - (6 * card_w + 5 * gap)) // 2
    start_y = py + 60

    parts = [svg_panel(px, py, pw, ph, "Stack", "Top languages")]
    for index in range(6):
        x = start_x + index * (card_w + gap)
        y = start_y
        if index < len(langs):
            name, pct = langs[index]
            color = LANG_COLORS.get(name, C["border_hi"])
            short = LANG_SHORT.get(name, truncate(name.upper(), 4))
            fill_width = max(8, int((card_w - 24) * pct / 100))
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="{C["bg"]}" opacity="0.58"/>',
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="none" stroke="{C["panel_line"]}" stroke-width="1"/>',
                    f'<circle cx="{x+20}" cy="{y+18}" r="6" fill="{color}"/>',
                    f'<text x="{x+34}" y="{y+21}" font-size="10" fill="{C["text_muted"]}">{e(name)}</text>',
                    f'<text x="{x+14}" y="{y+44}" font-size="16" font-weight="600" fill="{C["text"]}">{pct:.1f}%</text>',
                    f'<text x="{x+card_w-14}" y="{y+44}" text-anchor="end" font-size="10" fill="{color}">{e(short)}</text>',
                    f'<rect x="{x+14}" y="{y+52}" width="{card_w-28}" height="4" rx="2" fill="{C["panel_line"]}"/>',
                    f'<rect x="{x+14}" y="{y+52}" width="{fill_width}" height="4" rx="2" fill="{color}"/>',
                ]
            )
        else:
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="{C["bg"]}" opacity="0.35"/>',
                    f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="none" stroke="{C["panel_line"]}" stroke-width="1" stroke-dasharray="4 4"/>',
                    f'<text x="{x+card_w/2}" y="{y+31}" text-anchor="middle" font-size="10" fill="{C["text_muted"]}">Open slot</text>',
                ]
            )
    return "\n".join(parts)


def svg_recent_work(events):
    px, py, pw, ph = 18, 574, 814, 172
    parts = [svg_panel(px, py, pw, ph, "Recent Work", "Latest public push events")]
    header_y = py + 76
    parts.extend(
        [
            f'<text x="{px+26}" y="{header_y}" font-size="9" fill="{C["text_muted"]}">Repository</text>',
            f'<text x="{px+176}" y="{header_y}" font-size="9" fill="{C["text_muted"]}">Commit message</text>',
            f'<text x="{px+pw-126}" y="{header_y}" font-size="9" fill="{C["text_muted"]}">SHA</text>',
            f'<text x="{px+pw-20}" y="{header_y}" text-anchor="end" font-size="9" fill="{C["text_muted"]}">When</text>',
        ]
    )

    if not events:
        parts.append(
            f'<text x="{px+pw/2}" y="{py+120}" text-anchor="middle" font-size="11" fill="{C["text_dim"]}">No recent public push events.</text>'
        )
        return "\n".join(parts)

    row_h = 22
    start_y = py + 92
    for index, event in enumerate(events[:5]):
        row_y = start_y + index * row_h
        if index % 2 == 0:
            parts.append(
                f'<rect x="{px+14}" y="{row_y-13}" width="{pw-28}" height="{row_h}" rx="10" fill="{C["bg"]}" opacity="0.42"/>'
            )
        parts.append(
            f'<circle cx="{px+24}" cy="{row_y-2}" r="3" fill="{C["border_hi"]}"/>'
        )
        parts.append(
            f'<text x="{px+36}" y="{row_y}" font-size="10" fill="{C["border_hi"]}">{e(truncate(event["repo"], 18))}</text>'
        )
        parts.append(
            f'<text x="{px+176}" y="{row_y}" font-size="10" fill="{C["text"]}">{e(truncate(event["msg"], 56))}</text>'
        )
        parts.append(
            f'<text x="{px+pw-126}" y="{row_y}" font-size="10" fill="{C["gold"]}">{e(event["sha"])}</text>'
        )
        parts.append(
            f'<text x="{px+pw-20}" y="{row_y}" text-anchor="end" font-size="10" fill="{C["text_dim"]}">{e(reltime(event["ts"]))}</text>'
        )
    return "\n".join(parts)


def svg_collaboration(total, ai_count, ai_breakdown):
    px, py, pw, ph = 18, 762, 814, 86
    bar_x = px + 20
    bar_y = py + 58
    bar_w = pw - 40
    bar_h = 12
    manual_count = max(0, total - ai_count)
    hero_pct = (manual_count / total * 100) if total > 0 else 100
    legend_y = py + 78

    parts = [svg_panel(px, py, pw, ph, "Collaboration", "AI-assisted commit ratio")]
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6" fill="{C["bg"]}" opacity="0.6"/>'
    )
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6" fill="none" stroke="{C["panel_line"]}" stroke-width="1"/>'
    )

    manual_w = bar_w * manual_count / total if total > 0 else bar_w
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{manual_w:.1f}" height="{bar_h}" rx="6" fill="{C["green"]}"/>'
    )

    cursor_x = bar_x + manual_w
    for name, count in sorted(ai_breakdown.items(), key=lambda item: -item[1]):
        color = AI_COLORS.get(name, C["blue"])
        width = (bar_w * count / total) if total > 0 else 0
        if width <= 0:
            continue
        parts.append(
            f'<rect x="{cursor_x:.1f}" y="{bar_y}" width="{width:.1f}" height="{bar_h}" fill="{color}"/>'
        )
        cursor_x += width

    parts.append(
        f'<text x="{bar_x}" y="{py+40}" font-size="10" fill="{C["text_dim"]}">Manual {manual_count}/{total or 1} commits · {hero_pct:.0f}%</text>'
    )

    legend_parts = [f'<text x="{bar_x}" y="{legend_y}" font-size="9" fill="{C["green"]}">Manual</text>']
    legend_x = bar_x + 76
    for name, count in sorted(ai_breakdown.items(), key=lambda item: -item[1]):
        pct = (count / total * 100) if total > 0 else 0
        color = AI_COLORS.get(name, C["blue"])
        legend_parts.append(
            f'<text x="{legend_x}" y="{legend_y}" font-size="9" fill="{color}">{e(name)} {pct:.0f}%</text>'
        )
        legend_x += 94
    parts.extend(legend_parts)
    return "\n".join(parts)


def svg_footer():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fy = 876
    parts = [
        f'<line x1="18" y1="{fy-18}" x2="{W-18}" y2="{fy-18}" stroke="{C["panel_line"]}" stroke-width="1"/>',
        svg_pixel_grid(TRIFORCE, {1: C["gold"]}, 22, fy - 10, ps=4),
        f'<text x="52" y="{fy}" font-size="10" fill="{C["text_dim"]}">Generated from public GitHub activity.</text>',
        f'<text x="{W-22}" y="{fy}" text-anchor="end" font-size="10" fill="{C["text_muted"]}">Updated {now}</text>',
    ]
    return "\n".join(parts)


def generate_svg(stats, events, total, ai_count, ai_breakdown):
    sections = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        svg_defs(),
        svg_background(),
        svg_header(stats),
        svg_profile(stats),
        svg_activity(stats),
        svg_stack(stats["langs"]),
        svg_recent_work(events),
        svg_collaboration(total, ai_count, ai_breakdown),
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
        print("No GITHUB_TOKEN - using placeholder data")
        stats = {
            "repos": 42,
            "stars": 89,
            "followers": 15,
            "commits": 1234,
            "streak": 28,
            "total": 1500,
            "langs": [
                ("Python", 45.2),
                ("TypeScript", 23.1),
                ("Rust", 12.4),
                ("Go", 8.7),
                ("Shell", 6.2),
                ("HTML", 4.4),
            ],
            "weeks": [
                {
                    "contributionDays": [
                        {
                            "contributionCount": random.randint(0, 12),
                            "date": f"2025-01-{day+1:02d}",
                        }
                        for day in range(7)
                    ]
                }
                for _ in range(26)
            ],
        }
        events = [
            {
                "sha": "a1b2c3f",
                "repo": "bigmacfive",
                "msg": "feat: redesign the profile dashboard layout",
                "ts": "2025-01-15T10:00:00Z",
            },
            {
                "sha": "d4e5f6a",
                "repo": "dotfiles",
                "msg": "fix: clean shell aliases and startup scripts",
                "ts": "2025-01-14T08:00:00Z",
            },
            {
                "sha": "g7h8i9j",
                "repo": "api-server",
                "msg": "refactor: simplify middleware composition",
                "ts": "2025-01-13T06:00:00Z",
            },
            {
                "sha": "k0l1m2n",
                "repo": "bigmacfive",
                "msg": "chore: update generated profile asset",
                "ts": "2025-01-12T12:00:00Z",
            },
            {
                "sha": "o3p4q5r",
                "repo": "webapp",
                "msg": "feat: refine dashboard states and loading flow",
                "ts": "2025-01-11T15:00:00Z",
            },
        ]
        total, ai_count, ai_breakdown = 100, 35, {"Claude": 12, "Cursor": 11, "Copilot": 7, "GPT": 5}

    svg = generate_svg(stats, events, total, ai_count, ai_breakdown)
    with open("profile.svg", "w") as f:
        f.write(svg)
    print(f"Done! profile.svg ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
