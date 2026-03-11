# Input Schema

Use `scripts/render_daily_poster.py` with a UTF-8 JSON file. The default contract is intentionally small: in most cases, the user only needs to pass personal information.

## Quick Start

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

Render command:

```bash
python scripts/render_daily_poster.py --spec references/starter-spec.json --output out/starter-example.svg
```

If you want extra image files from the same render, add an `output.formats` field in JSON and keep `--output` as the filename stem anchor.

## Default Behavior

If you omit the other sections, the renderer automatically fills:

- Header date, weekday, and lunar text
- Masthead `摸鱼日报`
- `36kr` hot topics
- Right-side `heisi` image card
- Holiday countdown
- Holiday-aware plan table
- Horoscope card
- Quote card
- Bottom-right personal card from `personal_info`

## Minimal Contract

### `personal_info`

Optional in schema, but this is the default input for normal use.

```json
{
  "personal_info": {
    "name": "摸鱼主编",
    "bio_lines": [
      "第一行介绍",
      "第二行介绍"
    ]
  }
}
```

Notes:

- `name` or `title` becomes the bottom-right card title.
- `bio_lines` or `bio` becomes the bottom-right card body text.
- `bio_lines` works best with `2-4` short lines.

## Optional Advanced Fields

Only use these when you need to override the defaults.

### `base_date`

- Supports `today` or `YYYY-MM-DD`
- Applies to header date, holiday countdown, and holiday plan switching

### `theme`

Supported keys:

- `paper`
- `panel`
- `accent`
- `ink`
- `muted`
- `line`
- `soft`
- `stamp`
- `font_family`

The default font stack is tuned for Linux, macOS, and Windows CJK environments.

### `header`

Useful overrides:

- `masthead`
- `subtitle`
- `show_issue_line`
- `auto_date`
- `auto_lunar`

Notes:

- `subtitle` is optional.
- `show_issue_line` defaults to `false`.
- The built-in lunar table covers solar dates from `1900-01-31` through the end of lunar year `2049`.

### `lead_story`

Useful overrides:

- `title`
- `intro`
- `bullets`
- `limit`
- `auto_hot36kr`
- `api_url`

Notes:

- If `auto_hot36kr` is `true`, the renderer fetches hot topics at render time.
- If that request fails, it falls back to local `intro` and `bullets`.

### `sidebar_note`

Useful overrides:

- `auto_heisi`
- `api_url`
- `image_path`
- `image_label`

Notes:

- If `auto_heisi` is `true`, the renderer fetches the right-side image at render time.
- If that request fails, it falls back to the last cached image, then to `image_path`, then to a placeholder.

### `plan_table`

Useful overrides:

- `title`
- `rows`
- `auto_holiday`

Notes:

- `rows` works best with `4-6` items.
- If `auto_holiday` is `true`, the normal plan rows are replaced during legal holidays.

### `countdown`

Useful overrides:

- `title`
- `items`
- `data_path`
- `base_date`
- `auto_update`

Notes:

- `data_path` can point to a reusable JSON file with `holiday_schedule`.
- The built-in default uses `周末` first, then the next `3` legal holidays.

### `spotlight`

Useful overrides:

- `title`
- `name`
- `subtitle`
- `ratings`
- `badges`
- `auto_horoscope`
- `api_url`

Notes:

- If `auto_horoscope` is `true`, the renderer maps the horoscope API into the star rows and `宜 / 忌` badges.
- `ratings[].stars` must be an integer from `0` to `5`.

### `quote_card`

Useful overrides:

- `title`
- `text`
- `source`
- `auto_quote_api`
- `api_url`

Notes:

- If `auto_quote_api` is `true`, the renderer fetches the quote text at render time.
- If the fetched quote ends with a source suffix such as `——选自《...》` or `---散文集《...》`, the renderer moves that suffix to the source line automatically.

### `output`

Useful overrides:

- `formats`
- `scale`
- `quality`
- `background`

Example:

```json
{
  "output": {
    "formats": ["svg", "png"],
    "scale": 2,
    "quality": 92,
    "background": "#ffffff"
  }
}
```

Notes:

- `formats` accepts a string or array, for example `png` or `["svg", "png"]`.
- Supported values are `svg`, `png`, `jpg`, `jpeg`, `webp`.
- The renderer always generates SVG first, then converts that SVG into the requested sibling files.
- `scale` affects raster outputs such as `png`, `jpg`, `jpeg`, `webp`.
- `png` can use `magick`, `inkscape`, `rsvg-convert`, or `resvg`（`pip install resvg_py` 或系统安装 resvg CLI）.
- `jpg`, `jpeg`, `webp` can use `magick`, or `resvg` + `Pillow`（`pip install resvg_py Pillow`）.

## Image Rules

- `image_path` supports local files and remote `http(s)` URLs.
- Relative local paths are resolved from the JSON file folder.
- Missing or unreachable images do not crash the render; the renderer draws a placeholder instead.

## Compatibility

- Works on Linux, macOS, and Windows
- Uses only the Python standard library for SVG generation
- Raster export depends on a local conversion backend: `resvg`（`pip install resvg_py`，推荐）、`magick`、`inkscape` 或 `rsvg-convert`
