---
name: daily-poster
description: Generate two fixed poster variants from minimal JSON with Python: `daily` for "摸鱼日报" and `baidu_hot` for "百度热点/百度热搜". Use when Codex needs to map user wording to the correct poster type, render either variant, or update the corresponding JSON examples and commands.
---

# Daily Poster

## Poster Type Map

- `daily` = `摸鱼日报`
- `baidu_hot` = `百度热点` / `百度热搜`
- 用户提到“摸鱼日报”“日报”“节假日倒计时”“下班倒计时”时，优先选择 `daily`
- 用户提到“百度热点”“百度热搜”“热搜榜”“热榜”时，优先选择 `baidu_hot`

## Use

```json
{
  "poster_type": "daily",
  "personal_info": {
    "name": "智普虾🦐",
    "bio_lines": [
      "OpenClaw 驱动的 AI 助手，搭载GLM5 模型，机智温暖有点俏皮"
    ]
  }
}
```

- 默认入口：`python scripts/render_poster.py --spec <spec.json> --output out/poster`
- `poster_type` 只支持 `daily` 和 `baidu_hot`
- `poster_type: "daily"` 表示“摸鱼日报”版式
- `poster_type: "baidu_hot"` 表示“百度热点 / 百度热搜”版式
- 用户未明确要求时，只收集 `personal_info.name` 和最多 `2` 行 `bio_lines`

## Minimal Inputs

```bash
# 摸鱼日报（daily）
python scripts/render_poster.py --type daily --spec references/daily-poster-spec.json --output out/daily_poster

# 百度热点 / 百度热搜（baidu_hot）
python scripts/render_poster.py --type baidu_hot --spec references/baidu-hot-spec.json --output out/baidu_hot_poster
```

`daily` 最小输入（摸鱼日报）：

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

`baidu_hot` 最小输入（百度热点 / 百度热搜）：

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

## Rules

- `bio_lines` / `text_lines` 最多保留前 `2` 行非空内容
- `baidu_hot` 的 `title`、`subtitle`、`api_url`、`limit` 全部内置，不接受外部 JSON 覆盖
- `baidu_hot` 顶部日期区同一行显示公历、星期、农历
- 所有入口脚本统一输出 JSON 结果

## Key Files

- `scripts/render_poster.py`: 统一入口
- `scripts/render_daily_poster.py`: 摸鱼日报渲染器
- `scripts/render_baidu_hot.py`: 百度热搜渲染器
- `scripts/poster_runtime.py`: 统一运行时和 stdout JSON
- `references/daily-poster-spec.json`: 摸鱼日报示例
- `references/baidu-hot-spec.json`: 百度热搜示例
