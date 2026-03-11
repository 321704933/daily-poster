# Python Daily Poster

用 Python 生成 `摸鱼日报` 和 `百度热搜` 海报，默认输出 SVG，可按需导出 PNG/JPG/WEBP。

## 安装

```bash
pip install -r requirements.txt
```

## 统一入口

```bash
# 摸鱼日报（daily）
python scripts/render_poster.py --type daily --spec references/daily-poster-spec.json --output out/daily_poster

# 百度热点 / 百度热搜（baidu_hot）
python scripts/render_poster.py --type baidu_hot --spec references/baidu-hot-spec.json --output out/baidu_hot_poster
```

也可以直接调用：

- `python scripts/render_daily_poster.py --spec ... --output ...`
- `python scripts/render_baidu_hot.py --spec ... --output ...`

## 示例展示

### 摸鱼日报 (`daily`)

![daily_poster 示例](assets/daily_poster.png)

### 百度热点 (`baidu_hot`)

![baidu_hot_poster 示例](assets/baidu_hot_poster.png)

## 摸鱼日报最小 JSON

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

## 百度热搜最小 JSON

```json
{
  "poster_type": "baidu_hot",
  "personal_info": {
    "name": "智普虾🦐",
    "bio_lines": [
      "OpenClaw 驱动的 AI 助手，搭载 GLM5 模型，机智温暖有点俏皮"
    ]
  },
  "output": {
    "formats": ["svg", "png"],
    "scale": 2
  }
}
```

## 约束

- `bio_lines` / `text_lines` 最多取前 `2` 行非空内容
- `baidu_hot` 固定使用代码内置 `title` / `subtitle` / `api_url` / `limit`
- `baidu_hot` 顶部日期区同一行显示公历、星期、农历
- 所有入口脚本都会输出统一 JSON 结果

## 主要文件

- `scripts/render_poster.py`: 统一入口
- `scripts/render_daily_poster.py`: 摸鱼日报渲染器
- `scripts/render_baidu_hot.py`: 百度热搜渲染器
- `references/daily-poster-spec.json`: 摸鱼日报示例
- `references/baidu-hot-spec.json`: 百度热搜示例
