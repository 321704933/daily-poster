#!/usr/bin/env python3
"""Render a Baidu Hot Search poster styled after the official top.baidu.com page."""

from __future__ import annotations

import base64
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape, quoteattr

from holiday_countdown import parse_base_date
from lunar_calendar import format_lunar_text
from poster_runtime import run_renderer_cli

DEFAULT_FONT_STACK = '"PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
WEEKDAY_LABELS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
POSTER_TYPE = "baidu_hot"
DEFAULT_OUTPUT_SCALE = 2.0

BAIDU_API_URL = "https://v2.xxapi.cn/api/baiduhot"
DEFAULT_HEADER_TITLE = "百度热搜榜"
DEFAULT_HEADER_SUBTITLE = "实时热点  一手掌握"
DEFAULT_CONTENT_LIMIT = 10

# Logo path relative to this script
LOGO_PATH = Path(__file__).resolve().parent.parent / "references" / "baidu-logo.png"

# --- Official Baidu style palette ---
THEME = {
    "page_bg": "#f5f5f6",
    "card_bg": "#ffffff",
    "header_bg": "#ffffff",
    "title_color": "#222222",
    "subtitle_color": "#9195a3",
    "text_primary": "#333333",
    "text_desc": "#626675",
    "hot_color": "#ff4e4e",
    "rank_1_bg": "#f73131",
    "rank_2_bg": "#ff7f29",
    "rank_3_bg": "#ffaa20",
    "rank_normal_color": "#9195a3",
    "divider": "#ebebeb",
    "baidu_blue": "#306cff",
    "font_family": DEFAULT_FONT_STACK,
}


def _char_units(char: str) -> float:
    import unicodedata
    if char.isspace():
        return 0.35
    if unicodedata.east_asian_width(char) in {"W", "F"}:
        return 1.0
    if char in "ilI1|.,'`":
        return 0.32
    if char in "mwMW@#%&":
        return 0.9
    return 0.58


def _text_width(text: str, font_size: float) -> float:
    return sum(_char_units(ch) for ch in text) * font_size


def _truncate_text(text: str, max_width: float, font_size: float) -> str:
    if _text_width(text, font_size) <= max_width:
        return text
    result = ""
    for ch in text:
        if _text_width(result + ch + "...", font_size) > max_width:
            return result + "..."
        result += ch
    return result


def _escape(text: str) -> str:
    return escape(str(text))


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _resolve_base_date(spec: dict[str, Any]) -> date:
    raw_value = str(spec.get("base_date", "")).strip()
    if not raw_value:
        return date.today()
    return parse_base_date(raw_value)


def _resolve_lunar_text(current_date: date) -> str:
    try:
        return format_lunar_text(current_date)
    except (TypeError, ValueError):
        return ""


def _resolve_personal_lines(personal: dict[str, Any]) -> list[str]:
    text_lines = [str(item).strip() for item in _listify(personal.get("text_lines")) if str(item).strip()]
    if text_lines:
        return text_lines[:2]

    bio_lines = [str(item).strip() for item in _listify(personal.get("bio_lines")) if str(item).strip()]
    if bio_lines:
        return bio_lines[:2]

    bio = str(personal.get("bio", "")).strip()
    signature = str(personal.get("signature", "")).strip()
    merged = bio or signature
    return [merged] if merged else []


def normalize_baidu_hot_spec(spec: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    del base_dir
    normalized = dict(spec)
    normalized["poster_type"] = POSTER_TYPE

    normalized["header"] = {
        "title": DEFAULT_HEADER_TITLE,
        "subtitle": DEFAULT_HEADER_SUBTITLE,
    }
    normalized["content"] = {
        "api_url": BAIDU_API_URL,
        "limit": DEFAULT_CONTENT_LIMIT,
    }

    personal = normalized.get("personal_info", {})
    if not isinstance(personal, dict):
        personal = {}
    personal = dict(personal)
    if not str(personal.get("name", "")).strip() and str(personal.get("title", "")).strip():
        personal["name"] = str(personal.get("title", "")).strip()
    if not str(personal.get("signature", "")).strip():
        lines = _resolve_personal_lines(personal)
        if lines:
            personal["signature"] = " ".join(lines)
    normalized["personal_info"] = personal

    return normalized


def _load_logo_base64() -> str | None:
    if LOGO_PATH.exists():
        data = LOGO_PATH.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/png;base64,{b64}"
    return None


def _download_image_base64(url: str, *, timeout: float = 6.0) -> str | None:
    """Download an image URL and return as data URI, or None on failure."""
    if not url:
        return None
    try:
        req = Request(url, headers={"User-Agent": "daily-poster/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        b64 = base64.b64encode(data).decode("ascii")
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        return f"data:{content_type};base64,{b64}"
    except Exception:
        return None


def _format_hot_number(hot: str) -> str:
    """Format hot number: e.g. 4962498 -> 496万"""
    try:
        num = int(hot.replace(",", "").replace("万", "0000").strip())
    except (ValueError, AttributeError):
        return hot
    if num >= 10000:
        return f"{num // 10000}万"
    return str(num)


def _fetch_baidu_hot(api_url: str, *, timeout: float = 8.0) -> list[dict[str, Any]]:
    request = Request(api_url, headers={"User-Agent": "daily-poster/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            payload = json.loads(response.read().decode(charset))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return []
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", [])
    return data if isinstance(data, list) else []


def render_baidu_hot_poster(spec: dict[str, Any], base_dir: Path | None = None) -> str:
    del base_dir
    header = spec.get("header", {})
    header = header if isinstance(header, dict) else {}
    content = spec.get("content", {})
    content = content if isinstance(content, dict) else {}

    api_url = str(content.get("api_url", BAIDU_API_URL)).strip() or BAIDU_API_URL
    items = _fetch_baidu_hot(api_url)
    try:
        limit = int(content.get("limit", DEFAULT_CONTENT_LIMIT) or DEFAULT_CONTENT_LIMIT)
    except (TypeError, ValueError):
        limit = DEFAULT_CONTENT_LIMIT
    items = [it for it in items if isinstance(it, dict)][:limit]

    # Pre-download all item images
    img_cache: dict[int, str | None] = {}
    for i, item in enumerate(items):
        img_url = str(item.get("img", "")).strip()
        img_cache[i] = _download_image_base64(img_url)

    today = _resolve_base_date(spec)
    weekday = WEEKDAY_LABELS[today.weekday()]
    date_str = f"{today.year}年{today.month}月{today.day}日"
    lunar_text = _resolve_lunar_text(today)
    date_meta_parts = [date_str, weekday]
    if lunar_text:
        date_meta_parts.append(lunar_text)
    date_meta_text = "  ".join(part for part in date_meta_parts if part)

    logo_data_uri = _load_logo_base64()
    title_text = str(header.get("title", "")).strip() or DEFAULT_HEADER_TITLE
    subtitle = str(header.get("subtitle", DEFAULT_HEADER_SUBTITLE)).strip()

    width = 1080
    margin_x = 48
    card_w = width - margin_x * 2

    # Layout measurements
    header_h = 140
    item_h = 136
    card_padding_top = 16
    card_padding_bottom = 16
    card_header_h = 56
    content_h = card_header_h + card_padding_top + len(items) * item_h + card_padding_bottom
    footer_h = 52
    gap = 24
    height = header_h + gap + content_h + gap + footer_h

    font_family = quoteattr(THEME["font_family"])
    parts: list[str] = []

    # SVG open
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
        f' width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )

    # Defs: shadow filter + image clip paths
    parts.append("<defs>")
    parts.append(
        '<filter id="card-shadow" x="-4%" y="-2%" width="108%" height="110%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="8" flood-color="#000" flood-opacity="0.06"/>'
        '</filter>'
    )
    # Clip paths for rounded images (one per item)
    img_w, img_h, img_r = 160, 100, 8
    for i in range(len(items)):
        parts.append(
            f'<clipPath id="img-clip-{i}"><rect x="0" y="0" width="{img_w}" height="{img_h}" rx="{img_r}" ry="{img_r}"/></clipPath>'
        )
    parts.append("</defs>")

    # ====================== PAGE BACKGROUND ======================
    parts.append(f'<rect width="{width}" height="{height}" fill="{THEME["page_bg"]}"/>')

    # ====================== HEADER CARD ======================
    hdr_x = margin_x
    hdr_y = 24
    hdr_w = card_w
    hdr_h = header_h - 24

    parts.append(
        f'<rect x="{hdr_x}" y="{hdr_y}" width="{hdr_w}" height="{hdr_h}"'
        f' rx="16" ry="16" fill="{THEME["header_bg"]}" filter="url(#card-shadow)"/>'
    )

    # Baidu logo
    logo_y = hdr_y + 22
    if logo_data_uri:
        parts.append(
            f'<image x="{hdr_x + 36}" y="{logo_y}" width="120" height="42"'
            f' href="{logo_data_uri}" preserveAspectRatio="xMidYMid meet"/>'
        )
    else:
        parts.append(
            f'<text x="{hdr_x + 36}" y="{logo_y + 32}" fill="{THEME["baidu_blue"]}" font-size="30"'
            f' font-weight="800" font-family={font_family}>百度</text>'
        )

    # "热搜" badge
    badge_x = hdr_x + 168
    badge_y = logo_y + 8
    parts.append(
        f'<rect x="{badge_x}" y="{badge_y}" width="56" height="28" rx="4" ry="4" fill="{THEME["hot_color"]}"/>'
    )
    parts.append(
        f'<text x="{badge_x + 28}" y="{badge_y + 20}" fill="#ffffff" font-size="16"'
        f' font-weight="700" font-family={font_family} text-anchor="middle">热搜</text>'
    )

    # Date on the right
    parts.append(
        f'<text x="{hdr_x + hdr_w - 36}" y="{logo_y + 24}" fill="{THEME["subtitle_color"]}" font-size="18"'
        f' font-weight="400" font-family={font_family} text-anchor="end">'
        f'{_escape(date_meta_text)}</text>'
    )

    # Personal info
    personal = spec.get("personal_info", {})
    if isinstance(personal, dict):
        p_name = str(personal.get("name", "")).strip()
        personal_lines = _resolve_personal_lines(personal)
        if p_name:
            parts.append(
                f'<text x="{hdr_x + hdr_w - 36}" y="{logo_y + 48}" fill="{THEME["title_color"]}" font-size="15"'
                f' font-weight="600" font-family={font_family} text-anchor="end">{_escape(p_name)}</text>'
            )
        if personal_lines:
            sig_y = logo_y + (66 if p_name else 48)
            for index, line in enumerate(personal_lines[:2]):
                parts.append(
                    f'<text x="{hdr_x + hdr_w - 36}" y="{sig_y + index * 18}" fill="{THEME["subtitle_color"]}" font-size="13"'
                    f' font-weight="400" font-family={font_family} text-anchor="end">{_escape(line)}</text>'
                )

    # Subtitle
    if subtitle:
        parts.append(
            f'<text x="{hdr_x + 36}" y="{logo_y + 68}" fill="{THEME["subtitle_color"]}" font-size="15"'
            f' font-weight="400" font-family={font_family} letter-spacing="2">{_escape(subtitle)}</text>'
        )

    # ====================== CONTENT CARD ======================
    card_x = margin_x
    card_y = header_h + gap
    card_r = 16

    parts.append(
        f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{content_h}"'
        f' rx="{card_r}" ry="{card_r}" fill="{THEME["card_bg"]}" filter="url(#card-shadow)"/>'
    )

    # Card header
    ch_y = card_y + 40
    parts.append(
        f'<text x="{card_x + 36}" y="{ch_y}" fill="{THEME["title_color"]}" font-size="22"'
        f' font-weight="700" font-family={font_family}>{_escape(title_text)}</text>'
    )
    parts.append(
        f'<text x="{card_x + card_w - 36}" y="{ch_y}" fill="{THEME["subtitle_color"]}" font-size="14"'
        f' font-weight="400" font-family={font_family} text-anchor="end">TOP {len(items)}</text>'
    )

    # Divider below card header
    div_ch_y = card_y + card_header_h
    parts.append(
        f'<line x1="{card_x}" y1="{div_ch_y}" x2="{card_x + card_w}" y2="{div_ch_y}"'
        f' stroke="{THEME["divider"]}" stroke-width="1"/>'
    )

    # --- List items ---
    list_start_y = div_ch_y + card_padding_top
    text_area_w = card_w - 36 - 60 - 24 - img_w - 36  # left_pad + rank_area + gap + img + right_pad

    for i, item in enumerate(items):
        row_y = list_start_y + i * item_h
        rank = int(item.get("index", i + 1))
        title = str(item.get("title", "")).strip()
        hot = str(item.get("hot", "")).strip()
        desc = str(item.get("desc", "")).strip()

        # Row background (alternating)
        if i % 2 == 0:
            parts.append(
                f'<rect x="{card_x + 1}" y="{row_y}" width="{card_w - 2}" height="{item_h}"'
                f' fill="#fafbfc"/>'
            )

        # --- Left side: rank + text ---
        # Rank badge
        rank_cx = card_x + 56
        rank_cy = row_y + 32
        if rank <= 3:
            colors = [THEME["rank_1_bg"], THEME["rank_2_bg"], THEME["rank_3_bg"]]
            parts.append(
                f'<rect x="{rank_cx - 15}" y="{rank_cy - 15}" width="30" height="30"'
                f' rx="6" ry="6" fill="{colors[rank - 1]}"/>'
            )
            parts.append(
                f'<text x="{rank_cx}" y="{rank_cy + 7}" fill="#ffffff" font-size="17"'
                f' font-weight="700" font-family={font_family} text-anchor="middle">{rank}</text>'
            )
        else:
            parts.append(
                f'<text x="{rank_cx}" y="{rank_cy + 7}" fill="{THEME["rank_normal_color"]}" font-size="20"'
                f' font-weight="600" font-family={font_family} text-anchor="middle">{rank}</text>'
            )

        # Title
        title_x = card_x + 96
        title_y = row_y + 36
        title_fs = 20 if rank <= 3 else 18
        title_weight = "700" if rank <= 3 else "500"
        max_tw = text_area_w
        display_title = _truncate_text(title, max_tw, title_fs)
        parts.append(
            f'<text x="{title_x}" y="{title_y}" fill="{THEME["title_color"]}" font-size="{title_fs}"'
            f' font-weight="{title_weight}" font-family={font_family}>{_escape(display_title)}</text>'
        )

        # Description (two lines max)
        if desc:
            desc_y = row_y + 60
            desc_fs = 13
            max_dw = text_area_w
            line1 = _truncate_text(desc, max_dw, desc_fs)
            remaining = desc[len(line1.rstrip(".")):].lstrip(".").strip() if line1.endswith("...") else ""
            parts.append(
                f'<text x="{title_x}" y="{desc_y}" fill="{THEME["text_desc"]}" font-size="{desc_fs}"'
                f' font-weight="400" font-family={font_family}>{_escape(line1)}</text>'
            )
            if remaining:
                line2 = _truncate_text(remaining, max_dw, desc_fs)
                parts.append(
                    f'<text x="{title_x}" y="{desc_y + 18}" fill="{THEME["text_desc"]}" font-size="{desc_fs}"'
                    f' font-weight="400" font-family={font_family}>{_escape(line2)}</text>'
                )

        # Hot value (below title, left side)
        hot_display = _format_hot_number(hot)
        hot_y = row_y + (96 if desc else 64)
        hot_label_color = THEME["hot_color"] if rank <= 3 else THEME["subtitle_color"]
        parts.append(
            f'<text x="{title_x}" y="{hot_y}" fill="{hot_label_color}" font-size="13"'
            f' font-weight="500" font-family={font_family}>热度 {_escape(hot_display)}</text>'
        )

        # --- Right side: image ---
        img_data = img_cache.get(i)
        img_x = card_x + card_w - 36 - img_w
        img_y = row_y + (item_h - img_h) // 2
        if img_data:
            parts.append(
                f'<g transform="translate({img_x},{img_y})" clip-path="url(#img-clip-{i})">'
                f'<image x="0" y="0" width="{img_w}" height="{img_h}"'
                f' href="{img_data}" preserveAspectRatio="xMidYMid slice"/>'
                f'</g>'
            )
            # Subtle border around image
            parts.append(
                f'<rect x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}"'
                f' rx="{img_r}" ry="{img_r}" fill="none" stroke="{THEME["divider"]}" stroke-width="1"/>'
            )
        else:
            # Placeholder
            parts.append(
                f'<rect x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}"'
                f' rx="{img_r}" ry="{img_r}" fill="#f0f0f0"/>'
            )

        # Row divider
        if i < len(items) - 1:
            div_y = row_y + item_h
            parts.append(
                f'<line x1="{card_x + 36}" y1="{div_y}" x2="{card_x + card_w - 36}" y2="{div_y}"'
                f' stroke="{THEME["divider"]}" stroke-width="0.5"/>'
            )

    # ====================== FOOTER ======================
    footer_y = card_y + content_h + gap
    parts.append(
        f'<text x="{width // 2}" y="{footer_y + 28}" fill="{THEME["subtitle_color"]}" font-size="14"'
        f' font-weight="400" font-family={font_family} text-anchor="middle"'
        f' letter-spacing="1">数据来源：百度热搜  |  {_escape(date_str)}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    run_renderer_cli(
        poster_type=POSTER_TYPE,
        description="Render a Baidu Hot Search poster from JSON spec.",
        render_svg=render_baidu_hot_poster,
        default_scale=DEFAULT_OUTPUT_SCALE,
        default_background=THEME["page_bg"],
        prepare_spec=normalize_baidu_hot_spec,
    )


if __name__ == "__main__":
    main()
