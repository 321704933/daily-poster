---
name: daily-poster
description: Generate newspaper-style daily poster images from a minimal JSON input with Python. Default to collecting only personal info; the renderer auto-fills the rest of the daily poster.
---

# Python Daily Poster

## Overview

Generate a retro newspaper-style `摸鱼日报` poster from JSON. The default path is minimal: the user usually only needs to provide `personal_info`, and the renderer fills the rest of the poster automatically before exporting SVG and any requested image formats.

## Default Workflow

1. Start from [references/starter-spec.json](references/starter-spec.json).
2. Ask the user only for `personal_info.name` and `personal_info.bio_lines` unless they explicitly want deeper customization.
3. Render with `scripts/render_daily_poster.py`.
4. If the user asks for visual tweaks, edit the renderer or theme. If they ask for content tweaks, edit the JSON.
5. If the user asks for PNG/JPG/WEBP output, use `output.formats` in JSON and let the renderer call `scripts/svg_image_converter.py`.

## Minimal Input

Use this shape by default:

```json
{
  "personal_info": {
    "name": "摸鱼主编",
    "bio_lines": [
      "资深摸鱼艺术家，擅长在复杂需求里保住下班时间。",
      "不讲大道理，只负责把日报排好。"
    ]
  }
}
```

## Built-in Defaults

When the other sections are omitted, the renderer automatically fills:

- Header date, weekday, and lunar text
- Masthead `摸鱼日报`
- `36kr` hot topics
- Right-side `heisi` image card with local cache fallback
- Holiday countdown
- Holiday-aware plan table
- Horoscope card
- Quote card

Only introduce advanced fields such as `header`, `lead_story`, `sidebar_note`, `countdown`, or `spotlight` when the user explicitly asks to override the defaults.

## Render Command

```bash
python scripts/render_daily_poster.py --spec references/starter-spec.json --output out/starter-example.svg
```

SVG generation works on Linux, macOS, and Windows with the Python standard library only — zero third-party dependencies.

## Image Export

Raster export (PNG/JPG/WEBP) uses a multi-backend fallback chain:

| Backend | PNG | JPG/WEBP | Install |
|---------|-----|----------|---------|
| `resvg_py` | Y | Y (+ Pillow) | `pip install resvg_py` |
| `resvg` CLI | Y | Y (+ Pillow) | `brew install resvg` / `scoop install resvg` / `cargo install resvg` |
| `magick` | Y | Y | System: ImageMagick |
| `inkscape` | Y | - | System: Inkscape |
| `rsvg-convert` | Y | - | System: librsvg |

Recommended: `pip install resvg_py`（跨平台预编译 wheel，无系统依赖）。JPG/WEBP 额外需要 `pip install Pillow`。

## Resources

### scripts/render_daily_poster.py

Main renderer. It auto-wraps mixed Chinese and English text, embeds local or remote images into the SVG, caches the `heisi` image fallback, fills omitted sections with defaults, and triggers image conversion when `output.formats` is configured.

### scripts/svg_image_converter.py

Standalone SVG converter used by the renderer for PNG/JPG/JPEG/WEBP export. Tries `resvg_py` Python package first (in-process), then falls back to `resvg` CLI binary, then to system tools (`magick` / `inkscape` / `rsvg-convert`). Prefer reusing this module rather than re-implementing format conversion logic elsewhere.

### scripts/holiday_countdown.py

Holiday data structures, schedule lookups, and countdown calculation logic.

### scripts/lunar_calendar.py

Lunar date formatting utilities (solar → lunar conversion).

### scripts/generate_holiday_countdown.py

CLI tool to regenerate `references/holiday-countdown-2026.json` for a given date range.

### references/input-schema.md

Minimal input contract and the small set of optional advanced fields.

### references/starter-spec.json

Canonical starter template. This is the only example spec users should start from.

### references/holiday-countdown-2026.json

Built-in countdown data source used by the default poster when no custom countdown is supplied.
