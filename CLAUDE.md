# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A GitHub profile dashboard generator that outputs an ALttP (A Link to the Past) styled interactive SVG (`profile.svg`). Single Python file, fully automated via GitHub Actions.

## Commands

```bash
# Run locally (requires GITHUB_TOKEN env var)
export GITHUB_TOKEN=your_token
python generate_profile.py

# Install dependency
pip install requests
```

There are no tests, linters, or build steps — the only artifact is `profile.svg`.

## Architecture

Everything lives in `generate_profile.py` (~550 lines), structured in three layers:

1. **Data fetching** (lines ~84-212): Three functions hit GitHub APIs and return plain dicts
   - `fetch_stats()` — GraphQL: commits, streak, followers, stars, repos, languages, contribution calendar
   - `fetch_ai_ratio()` — GraphQL: scans commit messages across 30 repos for Co-Authored-By patterns (Claude/Cursor/Copilot)
   - `fetch_events()` — REST: recent public PushEvents for commit history

2. **SVG primitives** (lines ~216-290): Reusable building blocks
   - `svg_defs()` — CSS-only animations + Google Fonts import + gradients
   - `svg_panel(x, y, w, h, title)` — ALttP panel with green border, gold L-corner ornaments, optional titled header with dashed line
   - `svg_corner_ornaments()` — Gold L-shaped decorations at each panel corner
   - `svg_outer_border()` — Double-line border with gold corners wrapping the entire canvas

3. **SVG panels** (lines ~295-500): Each returns an SVG string fragment
   - `svg_hud()` — Hearts (streak) + title + rupees (stars) + keys (repos)
   - `svg_character()` — Hero pixel art + HP/MP bars + stat lines (16, 54, 240×230)
   - `svg_dungeon_map()` — 36-week contribution heatmap with 12px dungeon cells (268, 54, 566×230)
   - `svg_inventory()` — Languages as ALttP item slots in a row (16, 296, 818×110)
   - `svg_quest_log()` — Recent commits with CSS fade-in (16, 418, 818×170)
   - `svg_companions()` — AI collab stacked bar + legend (16, 600, 818×70)
   - `svg_footer()` — "GAME SAVED" + blinking cursor + timestamp

4. **Assembly** (`generate_svg()`): Composes all panels into the final SVG (850×720).

## Key Patterns

- **Canvas**: `W=850, H=720`. Panels laid out with `(x, y, w, h)` tuples.
- **Color palette**: `C` dict with ALttP-inspired colors (seafoam green, triforce gold, dungeon dark). All colors reference `C["key"]`.
- **Font**: `Press Start 2P` from Google Fonts with monospace fallback. GitHub strips the import, so it gracefully falls back.
- **Pixel art**: `PET` (16×13 hero) and `HEART` (5×5) are binary matrices rendered as `<rect>` grids.
- **Animations**: CSS-only (no SMIL) — GitHub's SVG renderer preserves CSS keyframes but strips SMIL `<animate>` tags.
- **AI detection**: Regex patterns in `AI_PATTERNS` matching `Co-Authored-By:` footers. Each tool maps to a Zelda companion name via `AI_NAMES`.

## CI/CD

GitHub Actions workflow (`.github/workflows/metrics.yml`) runs daily at midnight UTC, on push to main, and on manual dispatch. It generates `profile.svg` and auto-commits with `[skip ci]` to avoid loops.

## When Making Changes

- Panel Y-coordinates cascade: moving one panel requires adjusting all panels below it and potentially `H`.
- The `generate_svg()` function shows the visual stacking order — add new panels there.
- SVG output must be self-contained (no external assets besides the Google Fonts import which gracefully degrades).
- `random.seed(42)` in `svg_sparkles()` ensures deterministic output — don't remove it or the SVG will change every run.
- All animations must use CSS `@keyframes` only — never use SMIL `<animate>` tags (GitHub strips them).
