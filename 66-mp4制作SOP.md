# MP4 制作 SOP — 从 PPTX + MP3 到最终视频

> **前置条件**：每集已有 PPTX + MP3 + timestamps.json + 口播稿 nlp.json
> **最终产出**：`output.mp4`（幻灯片 + 音频 + 字幕，字幕与口播稿一字不差）

---

## 100% 正确的 MP4 = 满足全部 4 条

1. **字幕文本 = 口播稿原文**（一字不差，不是 ASR 识别）
2. **字幕时间 = stable-ts 从音频对齐**（不是 TTS 累加，不是字符比例）
3. **幻灯片切换 = timestamps.json 的 seg 时间**（不估算）
4. **MP4 总时长 = MP3 时长**（±1s）

---

## 输入文件

| 文件 | 说明 | 示例 |
|------|------|------|
| `slides.pptx` | 已完成的 PPTX | `R2芯片智能体·冷启动.pptx`（42页） |
| `output.mp3` | 口播稿音频 | `module4_v3.mp3`（1569.2s） |
| `timestamps.json` | 每段精确时间（TTS 日志累加） | `ep03_timestamps.json`（79段） |
| `*_nlp.json` | 口播稿原文 JSON | `module4_draft_v3_nlp.json` |
| `slide_plan.json` | 每页对应的 seg 映射 | 42 页 → 79 段的映射关系 |

---

## Step 1：PPTX → JPG

```bash
soffice --headless --convert-to pdf slides.pptx
pdftoppm -jpeg -r 150 slides.pdf slide
```

产物：`slide-01.jpg` ~ `slide-42.jpg`

**校验**：JPG 数量 = PPTX 页数

---

## Step 2：生成字幕（stable-ts forced alignment）

这是最关键的一步。**不是 ASR 识别，是 forced alignment**——把口播稿原文喂给 stable-ts，让它对齐到音频上。

### 2a. 准备 align_text.txt

从 nlp.json 拼接口播稿全文：

```python
import json

with open("nlp.json") as f:
    nlp = json.load(f)

text = "".join(item["text"] for item in nlp)

with open("align_text.txt", "w") as f:
    f.write(text)
```

**校验**：`align_text.txt` 的内容 = nlp.json 全部 text 拼接（diff = 0）

### 2b. 运行 stable-ts forced alignment

```bash
stable-ts output.mp3 \
  --model large-v3 \
  --language zh \
  --align align_text.txt \
  --overwrite \
  -o align_result.json
```

参数说明：
- `--align align_text.txt`：**forced alignment 模式**，不做 ASR，只对齐给定文本
- `--model large-v3`：Whisper large-v3 模型（精度最高）
- `--language zh`：中文

产物：`align_result.json`（句级时间戳，文本 = 口播稿原文）

**校验**：
```python
import json

ar = json.load(open("align_result.json"))
segs = ar["segments"]

# 拼接 stable-ts 输出文本
stable_text = "".join(s["text"] for s in segs).replace(" ", "")

# 原文
with open("align_text.txt") as f:
    original = f.read().replace(" ", "")

# 必须一致
assert stable_text == original, "stable-ts 输出文本与原文不一致！"
```

### 2c. 从 align_result.json 生成 subtitles.ass

```python
import json

ar = json.load(open("align_result.json"))
segs = ar["segments"]

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

header = """[Script Info]
Title: Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK SC Bold,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = []
for seg in segs:
    text = seg["text"].strip()
    if not text:
        continue
    start = format_ass_time(seg["start"])
    end = format_ass_time(seg["end"])
    lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

with open("subtitles.ass", "w", encoding="utf-8") as f:
    f.write(header)
    f.write("\n".join(lines))
    f.write("\n")
```

**校验**：
- ASS 全部文本拼接 = align_text.txt（diff = 0）
- 首条字幕 start ≈ 0s
- 末条字幕 end ≈ MP3 时长

---

## Step 3：生成幻灯片时间轴

从 slide_plan.json（每页的 segments 映射）+ timestamps.json 计算每页的起止时间。

```python
import json

plan = json.load(open("slide_plan.json"))
ts = json.load(open("timestamps.json"))
timings = ts if isinstance(ts, list) else ts["nlp_timings"]

timeline = []
for page in plan:
    slide_num = page["slide"]
    image = f"slide-{slide_num:02d}.jpg"

    if page["segments"]:
        first_seg = page["segments"][0]
        last_seg = page["segments"][-1]
        start = timings[first_seg]["start"]
        end = timings[last_seg]["end"]
    elif page["type"] == "封面页":
        start = 0.0
        first_content = next(p for p in plan if p["segments"])
        end = timings[first_content["segments"][0]]["start"]
    elif page["type"] == "终页":
        last_content = [p for p in plan if p["segments"]][-1]
        start = timings[last_content["segments"][-1]]["end"]
        end = ts["mp3_duration"] if isinstance(ts, dict) else timings[-1]["end"]
    elif page["type"] == "章节分隔页":
        # 从相邻内容页借 ±2s
        idx = plan.index(page)
        prev_content = next((p for p in reversed(plan[:idx]) if p["segments"]), None)
        next_content = next((p for p in plan[idx+1:] if p["segments"]), None)
        start = timings[prev_content["segments"][-1]]["end"] - 2 if prev_content else 0
        end = timings[next_content["segments"][0]]["start"] + 2 if next_content else start + 4
    
    timeline.append({
        "slide": slide_num,
        "image": image,
        "start": round(start, 2),
        "end": round(end, 2)
    })

with open("slide_timeline.json", "w") as f:
    json.dump(timeline, f, indent=2)
```

**校验**：
- 最后一页 end ≈ MP3 时长（±2s）
- 页数 = PPTX 页数

---

## Step 4：生成 ffmpeg concat 文件

```python
import json

timeline = json.load(open("slide_timeline.json"))

with open("slides_input.txt", "w") as f:
    for item in timeline:
        duration = item["end"] - item["start"]
        if duration <= 0:
            duration = 0.1  # 防止 0 duration
        f.write(f"file '{item['image']}'\n")
        f.write(f"duration {duration:.2f}\n")
    # ffmpeg concat 需要最后再写一次最后一个文件
    f.write(f"file '{timeline[-1]['image']}'\n")
```

---

## Step 5：合成 MP4

```bash
ffmpeg -y \
  -f concat -safe 0 -i slides_input.txt \
  -i output.mp3 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,ass=subtitles.ass" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p \
  -shortest \
  output.mp4
```

---

## 最终校验

```bash
# 1. 总时长
ffprobe -v quiet -show_entries format=duration -of csv=p=0 output.mp4
ffprobe -v quiet -show_entries format=duration -of csv=p=0 output.mp3
# 两者差值 < 1s

# 2. 字幕文本完整性
# ASS 全部 Dialogue 的 text 拼接 = align_text.txt = nlp.json 全文

# 3. 抽查 3-5 个点，播放 MP4 确认：
#    - 字幕与音频同步
#    - 幻灯片与内容对应
#    - 无黑屏/跳帧
```

---

## 流水线依赖图

```
slides.pptx ──→ Step 1: JPG ──────────────────────┐
                                                    │
nlp.json ──→ Step 2a: align_text.txt               │
                 │                                  │
output.mp3 ──→ Step 2b: stable-ts ──→ align_result │
                 │                                  │
                 └──→ Step 2c: subtitles.ass        │
                                    │               │
slide_plan.json + timestamps.json   │               │
    └──→ Step 3: slide_timeline.json│               │
              │                     │               │
              └──→ Step 4: slides_input.txt         │
                          │         │               │
                          └─────────┴───────────────┘
                                    │
                              Step 5: output.mp4
```

**Step 1 和 Step 2 可并行。Step 3 独立。Step 4-5 等前面全部完成。**
