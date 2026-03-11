# Input And Output Schema

## Entry

```bash
python scripts/render_poster.py --spec <spec.json> --output out/poster
```

可直接调用：

- `python scripts/render_daily_poster.py --spec ... --output ...`
- `python scripts/render_baidu_hot.py --spec ... --output ...`

## Shared Fields

- `poster_type`: `daily` 或 `baidu_hot`
- `base_date`: `today` 或 `YYYY-MM-DD`
- `personal_info`
- `output`

`personal_info` 兼容：

- `name` / `title`
- `bio_lines` / `text_lines` / `bio` / `signature`

约束：

- `bio_lines` 和 `text_lines` 最多保留前 `2` 行非空内容

`output` 示例：

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

- `formats` 支持 `svg`、`png`、`jpg`、`jpeg`、`webp`
- 渲染器总是先输出 SVG，再按需生成位图

## Stdout JSON

成功时统一输出：

```json
{
  "ok": true,
  "poster_type": "daily",
  "spec_path": "C:/.../references/daily-poster-spec.json",
  "requested_output": "C:/.../out/poster.svg",
  "output_formats": ["svg"],
  "primary_output": "C:/.../out/poster.svg",
  "rendered_files": [
    {
      "format": "svg",
      "path": "C:/.../out/poster.svg"
    }
  ]
}
```

## `daily`

输入：

```json
{
  "poster_type": "daily",
  "personal_info": {
    "name": "智普虾🦐",
    "bio_lines": [
      "OpenClaw 驱动的 AI 助手，搭载 GLM5 模型，机智温暖有点俏皮"
    ]
  }
}
```

## `baidu_hot`

输入：

```json
{
  "poster_type": "baidu_hot",
  "personal_info": {
    "name": "智普虾🦐",
    "bio_lines": [
      "OpenClaw 驱动的 AI 助手，搭载 GLM5 模型，机智温暖有点俏皮"
    ]
  }
}
```

