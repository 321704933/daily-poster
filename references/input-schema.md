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

`poster_type` 语义映射：

- `daily` = `摸鱼日报` / `日报` / `日刊` / `今日简报` 风格海报
- `baidu_hot` = `百度热搜` / `百度热点` / `热搜榜` 风格海报

注意：

- JSON 输入里仍然使用英文枚举值 `daily` 和 `baidu_hot`
- 中文名称、中文别名主要用于提示词理解、AI 识别和文档阅读

## AI 识别提示

如果需求、提示词或说明文本里出现下面这些中文说法，可按以下规则理解：

| 中文说法 | 规范 `poster_type` | 说明 |
| --- | --- | --- |
| 摸鱼日报 | `daily` | 默认指中文日报风格海报 |
| 摸鱼海报 | `daily` | 常见口语表达，按日报模板处理 |
| 日报 / 日刊 / 今日简报 | `daily` | 指向 `daily` 版式 |
| 百度热搜 | `baidu_hot` | 默认指百度热搜榜海报 |
| 百度热点 | `baidu_hot` | 与百度热搜同义使用 |
| 热搜榜 | `baidu_hot` | 在本项目中默认映射到百度热搜模板 |

推荐理解规则：

- 用户提到 `摸鱼日报`、`日报`、`今日简报` 时，优先生成 `daily`
- 用户提到 `百度热搜`、`百度热点`、`热搜榜` 时，优先生成 `baidu_hot`
- 如果用户用中文描述需求，AI 在生成 JSON 时应输出英文字段值，不要把 `poster_type` 直接写成中文

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

## `daily`（摸鱼日报）

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

## `baidu_hot`（百度热搜）

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

