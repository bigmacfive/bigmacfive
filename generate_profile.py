#!/usr/bin/env python3
"""Generate a minimal GitHub profile SVG."""

import base64
import json
import os
import random
import urllib.request
from datetime import datetime, timezone
from html import escape


USERNAME = "bigmacfive"
TOKEN = os.getenv("GITHUB_TOKEN", "")
W, H = 850, 860
FONT = "'Pretendard', 'Segoe UI', Arial, sans-serif"
FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "Pretendard-Regular.subset.woff2",
)
DISPLAY_NAME = "Bigmacfive"
PROFILE_ROLE = "Founder of snapdeck.app and kuku.mom."
random.seed(42)


C = {
    "bg": "#f3f4ee",
    "bg_alt": "#edf0e7",
    "card": "#fbfcf8",
    "line": "#d6dcd0",
    "line_strong": "#c5cdc1",
    "text": "#101114",
    "text_soft": "#5f665d",
    "text_faint": "#8b9189",
    "accent": "#0f8b6d",
    "accent_soft": "#d9ece6",
    "accent_mid": "#7ab8a4",
    "accent_dark": "#075c48",
    "heat0": "#e7ece5",
    "heat1": "#d5e8e0",
    "heat2": "#b7dacd",
    "heat3": "#7fbba6",
    "heat4": "#0f8b6d",
    "shadow": "#dfe5db",
}


LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178C6",
    "JavaScript": "#D6B400",
    "Rust": "#C77D4E",
    "Go": "#0AA5D8",
    "Shell": "#5FAF3A",
    "HTML": "#E34C26",
    "CSS": "#7A4AC7",
    "Java": "#B07219",
    "C++": "#F34B7D",
    "C": "#6A6A6A",
    "Ruby": "#A3142B",
    "Swift": "#F05138",
    "Kotlin": "#7E57FF",
    "Dart": "#00A7A7",
    "Lua": "#2756C5",
    "PHP": "#4F5D95",
    "Scala": "#C22D40",
    "Haskell": "#5E5086",
    "Elixir": "#6E4A7E",
    "Zig": "#EC915C",
    "Vue": "#41B883",
    "Svelte": "#FF3E00",
    "SCSS": "#C6538C",
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


def e(value):
    return escape(str(value), quote=False)


def fmt_number(value):
    return f"{value:,}"


def truncate(text, limit):
    text = text or ""
    return text if len(text) <= limit else text[: limit - 1] + "..."


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
            if name == "Makefile":
                continue
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
            message = commit.get("message", "")
            for pattern in AI_PATTERNS:
                if not re.search(pattern, message):
                    continue
                ai_count += 1
                lowered = message.lower()
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
    svg {{
      shape-rendering: geometricPrecision;
      text-rendering: geometricPrecision;
    }}
    text, tspan {{
      font-family: {FONT};
      letter-spacing: -0.05em;
      fill: {C["text"]};
      font-feature-settings: "tnum" 1;
    }}
  </style>
  <radialGradient id="bgGlowA" cx="0.15" cy="0.1" r="0.8">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
  </radialGradient>
  <radialGradient id="bgGlowB" cx="0.85" cy="0.2" r="0.7">
    <stop offset="0%" stop-color="{C["accent_soft"]}" stop-opacity="0.9" />
    <stop offset="100%" stop-color="{C["accent_soft"]}" stop-opacity="0" />
  </radialGradient>
  <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="{C["shadow"]}" flood-opacity="0.9" />
  </filter>
</defs>"""


def svg_background():
    return "\n".join(
        [
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="{C["bg"]}"/>',
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bgGlowA)"/>',
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bgGlowB)"/>',
            f'<circle cx="720" cy="104" r="150" fill="{C["accent_soft"]}" opacity="0.45"/>',
            f'<circle cx="118" cy="720" r="110" fill="#ffffff" opacity="0.8"/>',
        ]
    )


def svg_card(x, y, w, h, radius=24):
    return "\n".join(
        [
            '<g filter="url(#cardShadow)">',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{C["card"]}"/>',
            "</g>",
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="none" stroke="{C["line"]}" stroke-width="1"/>',
        ]
    )


def svg_label(x, y, text, size=10, color=None, anchor=None):
    fill = color or C["text_faint"]
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{extra}>{e(text)}</text>'


def svg_body(x, y, text, size=12, color=None, anchor=None):
    fill = color or C["text_soft"]
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{extra}>{e(text)}</text>'


def svg_title(x, y, text, size=18):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="600" fill="{C["text"]}">{e(text)}</text>'


def svg_value(x, y, text, size=28, anchor=None, color=None):
    fill = color or C["text"]
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="600" fill="{fill}"{extra}>{e(text)}</text>'


def svg_divider(x1, y, x2):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{C["line"]}" stroke-width="1"/>'


def svg_metric_chip(x, y, w, h, label, value):
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#ffffff" opacity="0.7"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{C["line"]}" stroke-width="1"/>',
        svg_label(x + 18, y + 22, label, size=10),
        svg_value(x + 18, y + 52, value, size=28),
    ]
    return "\n".join(parts)


def svg_hero(stats):
    x, y, w, h = 32, 32, 786, 184
    chip_w = 122
    chip_h = 72
    chip_gap = 12
    chips_x = x + w - (chip_w * 2 + chip_gap) - 28
    chips_y = y + 24
    streak_label = "day" if stats["streak"] == 1 else "days"

    parts = [svg_card(x, y, w, h, radius=28)]
    parts.append(svg_label(x + 28, y + 28, "GitHub profile"))
    parts.append(svg_value(x + 28, y + 76, DISPLAY_NAME, size=46))
    parts.append(svg_body(x + 28, y + 108, PROFILE_ROLE, size=16, color=C["accent_dark"]))
    meta = (
        f"Public activity only. Updated daily. Current streak: "
        f"{stats['streak']} {streak_label}."
    )
    parts.append(svg_body(x + 28, y + 146, meta, size=11, color=C["text_faint"]))

    chips = [
        ("Contributions", fmt_number(stats["total"])),
        ("Commits", fmt_number(stats["commits"])),
        ("Repositories", str(stats["repos"])),
        ("Followers", str(stats["followers"])),
    ]
    for index, (label, value) in enumerate(chips):
        row = index // 2
        col = index % 2
        chip_x = chips_x + col * (chip_w + chip_gap)
        chip_y = chips_y + row * (chip_h + chip_gap)
        parts.append(svg_metric_chip(chip_x, chip_y, chip_w, chip_h, label, value))
    return "\n".join(parts)


def svg_activity(weeks, total):
    x, y, w, h = 32, 236, 786, 280
    parts = [svg_card(x, y, w, h)]
    parts.append(svg_label(x + 28, y + 28, "Contribution activity"))
    parts.append(svg_title(x + 28, y + 56, "Last 24 weeks", size=20))
    parts.append(
        svg_body(
            x + 28,
            y + 80,
            f"{fmt_number(total)} contributions across public repositories.",
            size=12,
        )
    )

    display_weeks = weeks[-24:] if len(weeks) >= 24 else weeks
    cell = 16
    gap = 4
    step = cell + gap
    grid_w = len(display_weeks) * step
    grid_x = x + 110 + max(0, (w - 180 - grid_w) // 2)
    grid_y = y + 112
    levels = [C["heat0"], C["heat1"], C["heat2"], C["heat3"], C["heat4"]]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        parts.append(svg_label(grid_x - 18, grid_y + row * step + 11, label, size=10, color=C["text_faint"]))

    last_month = None
    for week_index, week in enumerate(display_weeks):
        days = week.get("contributionDays") or []
        if days:
            try:
                dt = datetime.fromisoformat(days[0]["date"])
                if dt.month != last_month:
                    last_month = dt.month
                    parts.append(
                        svg_label(grid_x + week_index * step, grid_y - 14, month_names[dt.month - 1], size=10)
                    )
            except Exception:
                pass
        for day_index, day in enumerate(days):
            count = day.get("contributionCount", 0)
            level = 0 if count == 0 else (1 if count <= 2 else (2 if count <= 5 else (3 if count <= 9 else 4)))
            cx = grid_x + week_index * step
            cy = grid_y + day_index * step
            parts.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="5" fill="{levels[level]}"/>'
            )

    legend_x = x + w - 150
    legend_y = y + h - 34
    parts.append(svg_label(legend_x - 28, legend_y + 11, "Low", size=10))
    for index, color in enumerate(levels):
        lx = legend_x + index * 18
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="14" height="14" rx="4" fill="{color}"/>'
        )
    parts.append(svg_label(legend_x + 98, legend_y + 11, "High", size=10))
    return "\n".join(parts)


def svg_languages(langs):
    x, y, w, h = 32, 536, 300, 206
    parts = [svg_card(x, y, w, h)]
    parts.append(svg_label(x + 24, y + 28, "Top languages"))
    parts.append(svg_title(x + 24, y + 56, "Stack", size=20))

    start_y = y + 90
    row_h = 20
    bar_x = x + 120
    bar_w = 156

    if not langs:
        parts.append(svg_body(x + 24, y + 118, "No language data available.", size=12))
        return "\n".join(parts)

    for index, (name, pct) in enumerate(langs[:6]):
        row_y = start_y + index * 18
        color = LANG_COLORS.get(name, C["accent"])
        fill_w = max(6, int(bar_w * pct / 100))
        parts.append(svg_body(x + 24, row_y, name, size=12, color=C["text"]))
        parts.append(
            f'<rect x="{bar_x}" y="{row_y - 10}" width="{bar_w}" height="8" rx="4" fill="{C["bg_alt"]}"/>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{row_y - 10}" width="{fill_w}" height="8" rx="4" fill="{color}"/>'
        )
    return "\n".join(parts)


def svg_recent_work(events):
    x, y, w, h = 352, 536, 466, 206
    parts = [svg_card(x, y, w, h)]
    parts.append(svg_label(x + 24, y + 28, "Latest public push events"))
    parts.append(svg_title(x + 24, y + 56, "Recent work", size=20))
    parts.append(svg_label(x + 24, y + 86, "Repository", size=10))
    parts.append(svg_label(x + 154, y + 86, "Update", size=10))
    parts.append(svg_label(x + w - 24, y + 86, "When", size=10, color=C["text_faint"], anchor="end"))

    if not events:
        parts.append(
            svg_body(x + w / 2, y + 126, "No recent public push events.", size=13, color=C["text_faint"], anchor="middle")
        )
        return "\n".join(parts)

    row_h = 24
    start_y = y + 110
    for index, event in enumerate(events[:4]):
        row_y = start_y + index * row_h
        if index > 0:
            parts.append(svg_divider(x + 24, row_y - 12, x + w - 24))
        repo = truncate(event["repo"], 18)
        msg = truncate(event["msg"], 36)
        when = reltime(event["ts"])
        parts.append(svg_body(x + 24, row_y, repo, size=12, color=C["accent_dark"]))
        parts.append(svg_body(x + 154, row_y, msg, size=12, color=C["text"]))
        parts.append(svg_body(x + w - 24, row_y, when, size=12, color=C["text_soft"], anchor="end"))
    return "\n".join(parts)


def svg_footer(total, ai_count, ai_breakdown):
    x, y, w, h = 32, 762, 786, 66
    bar_x = x + 150
    bar_y = y + 29
    bar_w = 360
    bar_h = 10

    parts = [svg_card(x, y, w, h, radius=22)]
    parts.append(svg_label(x + 24, y + 27, "Working style"))

    if total <= 0:
        parts.append(
            f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5" fill="{C["bg_alt"]}"/>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w * 0.84:.1f}" height="{bar_h}" rx="5" fill="{C["accent_soft"]}"/>'
        )
        parts.append(svg_body(x + 24, y + 48, "No AI-assist footers detected in recent public commits.", size=12))
        parts.append(svg_body(x + 540, y + 48, "No recent commit sample", size=11, color=C["text_soft"]))
        return "\n".join(parts)

    manual_count = max(0, total - ai_count)
    manual_pct = manual_count / total * 100
    parts.append(svg_body(x + 24, y + 48, f"Manual share {manual_pct:.0f}%", size=16, color=C["text"]))
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5" fill="{C["bg_alt"]}"/>'
    )
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w * manual_count / total:.1f}" height="{bar_h}" rx="5" fill="{C["accent"]}"/>'
    )

    cursor_x = bar_x + bar_w * manual_count / total
    sorted_breakdown = sorted(ai_breakdown.items(), key=lambda item: -item[1])[:3]
    for index, (name, count) in enumerate(sorted_breakdown):
        width = bar_w * count / total
        color = ["#94c8b8", "#b8d9cf", "#cbded7"][min(index, 2)]
        parts.append(
            f'<rect x="{cursor_x:.1f}" y="{bar_y}" width="{width:.1f}" height="{bar_h}" fill="{color}"/>'
        )
        cursor_x += width

    if sorted_breakdown:
        summary = " | ".join(
            f"{name} {count / total * 100:.0f}%"
            for name, count in sorted_breakdown
        )
    else:
        summary = "No AI-assist footers detected."
    parts.append(svg_body(x + 540, y + 48, summary, size=11, color=C["text_soft"]))
    return "\n".join(parts)


def svg_timestamp():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return svg_body(W - 32, H - 16, f"Updated {now}", size=10, color=C["text_faint"], anchor="end")


def generate_svg(stats, events, total, ai_count, ai_breakdown):
    sections = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        svg_defs(),
        svg_background(),
        svg_hero(stats),
        svg_activity(stats["weeks"], stats["total"]),
        svg_languages(stats["langs"]),
        svg_recent_work(events),
        svg_footer(total, ai_count, ai_breakdown),
        svg_timestamp(),
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
                ("TypeScript", 37.4),
                ("Python", 25.6),
                ("Rust", 17.7),
                ("JavaScript", 9.1),
                ("CSS", 5.2),
                ("HTML", 5.0),
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
                "repo": "webapp",
                "msg": "feat: refine dashboard states and loading flow",
                "ts": "2025-01-12T12:00:00Z",
            },
        ]
        total, ai_count, ai_breakdown = 100, 18, {"Cursor": 10, "Claude": 5, "GPT": 3}

    svg = generate_svg(stats, events, total, ai_count, ai_breakdown)
    with open("profile.svg", "w") as f:
        f.write(svg)
    print(f"Done! profile.svg ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
