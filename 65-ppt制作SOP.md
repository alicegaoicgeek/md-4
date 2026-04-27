# PPT 制作 SOP — 从 timestamps + 四件套到 design.md

> **执行者**：云端 AI
> **你的唯一任务**：读输入文件 → 按本 SOP 的算法执行 → 输出 slide_plan.json + design.md
> **铁律**：不跳步、不省略、不自编文字、不脑补、先输出 slide_plan.json 再输出 design.md

---

## ⚠️ 致命错误清单（历史教训，必须避免）

| # | 致命错误 | 正确做法 |
|---|---------|---------|
| 1 | 跳过 Step A 直接写 design.md | **必须先输出 slide_plan.json，通过校验后才能开始 design.md** |
| 2 | 长时间思考不输出 | **每完成一页就写入文件，不要在脑中构思整个文档** |
| 3 | 自己编写文字放到幻灯片上 | **100% 从口播稿/四件套原文提取，一字不改** |
| 4 | 把多个超长 segment 塞进同一页导致 duration > 55s | **每页 25-55s 硬限制，超长 segment 独占一页** |
| 5 | segment 遗漏或重复 | **每个 segment index 恰好出现一次** |
| 6 | 忽略 mindmap 章节结构 | **必须按 mindmap 的 ## 标题划分章节，每个章节前有章节分隔页** |
| 7 | 页面类型千篇一律 | **同类型不超过 3 次（章节分隔页除外）** |
| 8 | 用字符比例估算时间 | **时间 100% 来自 timestamps.json 的 start/end** |

---

## 输入文件

你会收到以下文件：

### 1. timestamps.json

```json
{
  "nlp_timings": [
    {"index": 0, "start": 0.0, "end": 14.2, "duration": 14.2, "text": "先立一条公理……"},
    {"index": 1, "start": 14.2, "end": 17.0, "duration": 2.8, "text": "有了这条公理……"}
  ],
  "nlp_count": 80,
  "mp3_duration": 1632.9
}
```

- `nlp_timings[i].index` = 段号（从 0 开始）
- `nlp_timings[i].start / end` = 该段的精确起止秒数
- `nlp_timings[i].text` = 该段原文
- `mp3_duration` = MP3 总时长

### 2. 四件套（4 个 txt 文件）

| 文件 | 格式示例 |
|------|---------|
| `painpoints.txt` | `### 认知过载导致边界死锁`（每块有 `**痛点场景**` + `**黄金开头**` + `**黄金钩子**`） |
| `golden_sentences.txt` | `测试是系统行为的唯一真相来源……\|92`（文本\|分数） |
| `methods.txt` | `### R2-TDD六步执行法`（每块有 `**操作步骤**` + `**验证方式**`） |
| `mindmap.txt` | `## 章节标题`（`##` = 一级章节，`###` = 二级） |

### 3. 口播稿 .md

口播稿全文。幻灯片上的文字从这里和四件套提取。

### 4. EP03 设计稿模板

格式参考，你的 design.md 必须与它格式一致。

---

## Step A：生成 slide_plan.json

### A.1 计算页数

```python
import math

mp3_dur = timestamps["mp3_duration"]        # 例：1632.9
n_segs  = timestamps["nlp_count"]           # 例：80
chapters = [line for line in mindmap if line.startswith("## ")]  # 例：9个##标题

n_content = math.ceil(mp3_dur / 40)         # 例：ceil(1632.9/40) = 41
n_chapter = len(chapters)                   # 例：9
n_total   = 1 + n_chapter + n_content + 1   # 例：1+9+41+1 = 52
```

### A.2 将 segments 划入章节

**算法**：

1. 读 mindmap.txt 的所有 `##` 标题，得到章节列表 `chapters[]`
2. 读口播稿全文，找到每个 `##` 标题在口播稿中的位置，确定该章节覆盖的文本范围
3. 对每个 segment，用 `text` 字段与口播稿文本做匹配，确定它属于哪个章节
4. 结果：每个章节包含一组连续的 segment index

**注意**：segments 在章节间是**连续**的——章节 1 的 segments 全部排在章节 2 之前，不会交叉。

### A.3 在每个章节内分组成页

**算法**（对每个章节内的 segments 执行）：

```
current_page_segments = []
current_page_duration = 0.0

for seg in chapter_segments:
    seg_dur = seg.duration
    
    # 规则 4：超长 segment 独占一页
    if seg_dur > 55:
        # 先把当前累积的输出为一页
        if current_page_segments:
            output_page(current_page_segments)
            current_page_segments = []
            current_page_duration = 0.0
        # 超长 segment 独占一页（允许超 55s）
        output_page([seg])
        continue
    
    # 尝试加入当前页
    new_duration = current_page_duration + seg_dur
    
    if new_duration > 55:
        # 超限，先输出当前页，seg 留到下一页
        output_page(current_page_segments)
        current_page_segments = [seg]
        current_page_duration = seg_dur
    else:
        current_page_segments.append(seg)
        current_page_duration = new_duration

# 章节结束，输出剩余
if current_page_segments:
    # 规则 5：如果剩余 duration < 25s 且不是只有一个短 segment
    if current_page_duration < 25 and len(current_page_segments) > 0:
        # 与前一页合并（如果合并后不超 55s）
        merge_with_previous_page_if_possible()
    else:
        output_page(current_page_segments)
```

**硬限制检查**：

- 每页 duration 必须在 25-55s（例外：超长 segment 独占页 >55s 允许；章节最后一页如果只有短 segment <25s 允许）
- `< 10s` 的 segment 不能独占一页，必须与相邻 segment 合并

### A.4 计算每页的 start/end

```
对于内容页：
  start = nlp_timings[该页第一个 seg index].start
  end   = nlp_timings[该页最后一个 seg index].end
  duration = end - start

对于封面页：
  start = 0.0
  end   = 第一个内容页的 start（如果第一个 seg start=0，则封面 end=0, duration=0）

对于章节分隔页：
  start = 前一内容页的 end - 2
  end   = 下一内容页的 start + 2
  duration = 4.0（固定）
  
  特殊：第一个章节分隔页
    start = 封面页的 end - 2（最小为 0）
    end   = 第一个内容页的 start + 2

对于终页：
  start = 最后一个内容页的 end
  end   = mp3_duration
```

### A.5 为每个内容页选择页面类型

页面类型库：

| 类别 | 类型 |
|------|------|
| 结构类 | 封面页、章节分隔页、终页、主旨页 |
| 冲击类 | 冲击引言页、全屏金句页、数据冲击页 |
| 内容类 | 定义页、代码示例页、映射表页、对照表页 |
| 图表类 | 架构图页、流程图页、时间线页、DAG图页、金字塔页 |
| 卡片类 | 三栏卡片页、四栏卡片页、对比双栏页 |

**选择规则**：

1. 读该页的 segments text，判断内容性质：
   - 如果包含金句（在 golden_sentences.txt 中得分 ≥ 90）→ 优先选「全屏金句页」或「冲击引言页」
   - 如果是定义/概念解释 → 选「定义页」
   - 如果有对比关系 → 选「对比双栏页」或「对照表页」
   - 如果有流程/步骤 → 选「流程图页」或「时间线页」
   - 如果列举 3-4 个并列要点 → 选「三栏卡片页」或「四栏卡片页」
   - 如果有代码/命令 → 选「代码示例页」
   - 如果有层级关系 → 选「金字塔页」或「架构图页」
2. **同类型不超过 3 次**（章节分隔页除外）。如果超限，换同类别的其他类型。

### A.6 标注四件套引用

对每个内容页：

1. 读该页 segments 的 text
2. 在 painpoints.txt 中查找语义最匹配的痛点 → `painpoint_ref`（无匹配填 `null`）
3. 在 golden_sentences.txt 中查找语义最匹配的金句 → `golden_ref`（格式 `"金句文本|分数"`，无匹配填 `null`）
4. 在 methods.txt 中查找语义最匹配的方法 → `method_ref`（无匹配填 `null`）

### A.7 输出 slide_plan.json

格式：

```json
[
  {
    "slide": 1,
    "type": "封面页",
    "title": "EP06 TDD：测试驱动开发",
    "segments": [],
    "start": 0.0,
    "end": 0.0,
    "duration": 0.0
  },
  {
    "slide": 2,
    "type": "章节分隔页",
    "title": "三大难题与对策",
    "chapter": 1,
    "segments": [],
    "start": 0.0,
    "end": 2.0,
    "duration": 4.0
  },
  {
    "slide": 3,
    "type": "冲击引言页",
    "title": "测试是唯一真相来源",
    "segments": [0, 1],
    "start": 0.0,
    "end": 17.0,
    "duration": 17.0,
    "painpoint_ref": null,
    "golden_ref": "测试是系统行为的唯一真相来源|92",
    "method_ref": null
  }
]
```

### A.8 校验（必须全部通过才能进入 Step B）

```
✅ 检查 1：segment 完整性
   set(所有内容页的 segments 展平) == set(range(nlp_count))
   → 每个 index 恰好出现一次

✅ 检查 2：时间覆盖
   abs(sum(所有页的 duration) - mp3_duration) < 10s

✅ 检查 3：duration 范围
   每个内容页 duration 在 [25, 55] 范围内
   例外：超长 segment 独占页允许 > 55s
   例外：章节末尾短页允许 < 25s（但不能 < 10s）

✅ 检查 4：章节页 duration = 4s

✅ 检查 5：segments 递增
   每页的 segments 列表是递增的
   相邻页的 segments 也是递增的（不交叉）

✅ 检查 6：页面类型不超限
   统计每种类型出现次数 ≤ 3（章节分隔页除外）
```

**如果任何检查失败，修正后重新输出 slide_plan.json。不要带着错误进入 Step B。**

---

## Step B：生成 design.md

### 前置条件

slide_plan.json 已通过全部 6 项校验。

### 执行方式

**逐页生成**。每完成一页就写入文件，不要试图在脑中构思完整文档。

### 设计规范

| 属性 | 值 |
|------|-----|
| 画幅 | 16:9 (1920×1080) |
| 背景色 | #0A0E17 深海蓝黑 |
| 主强调色 | #00FF41 霓虹绿 |
| 卡片底色 | #1A2332 |
| 卡片边框 | #2A3A4A（普通）/ #00FF41（高亮） |
| 中文字体 | Noto Sans CJK SC Bold / Regular |
| 英文字体 | JetBrains Mono / Inter |
| 标题字号 | 44-60pt（全屏金句 80pt+） |
| 正文字号 | 22-28pt |
| 图标风格 | 线条+绿色填充，扁平风 |
| 章节页 | 六边形蜂巢纹理 + 绿色流线 + 大号章节编号 |

### 每页生成流程（对 slide_plan.json 中每一条执行）

#### Step B.1 — 提取该页的原文

```
segments = slide_plan[i].segments
texts = [nlp_timings[seg_index].text for seg_index in segments]
full_text = "\n".join(texts)
```

#### Step B.2 — 从原文中提取关键信息放到幻灯片上

1. 标题：从 full_text 提取一句核心主旨（**必须是原文中的句子或短语**）
2. 要点：提取 2-5 个关键句（**必须是原文原句，不改写**）
3. 如果有 golden_ref：金句原文必须出现在幻灯片上
4. 如果有 painpoint_ref：痛点的核心场景必须体现

#### Step B.3 — 按页面类型画 ASCII 布局

根据 slide_plan[i].type，画对应的 ASCII 框图。框图中标注：
- 每个元素的位置
- 字号和颜色
- 图标描述

**各类型的布局模板**：

**封面页**：
```
┌─────────────────────────────────────────┐
│          [电路板纹理全屏背景]              │
│    ┌───┐                                │
│    │ ╋ │  ← 图标(绿色线条)               │
│    └───┘                                │
│   主标题文字                   (白色60pt) │
│   ─────────── (绿色分隔线)               │
│        EPISODE NN                       │
│     R2 芯片智能体 · 系列名        (灰色) │
└─────────────────────────────────────────┘
```

**章节分隔页**：
```
┌─────────────────────────────────────────┐
│           [六边形+流线背景]               │
│     NN                        (绿色80pt)│
│     ───                                 │
│     CHAPTER NN                          │
│     章节标题                              │
│     ENGLISH SUBTITLE                    │
└─────────────────────────────────────────┘
```

**冲击引言页**：
```
┌─────────────────────────────────────────┐
│  ┌─ 绿色竖线引用框 ────────────────────┐ │
│  │ "引言原文"                           │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  图标 标题    │  │  图标 标题        │ │
│  │  正文要点     │  │  正文要点         │ │
│  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────┘
```

**全屏金句页**：
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│     "金句原文"                 (白色80pt) │
│                                         │
│     —— 出处                    (绿色24pt)│
│                                         │
└─────────────────────────────────────────┘
```

**三栏卡片页**：
```
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ 图标      │ │ 图标      │ │ 图标      │ │
│ │ 卡片标题  │ │ 卡片标题  │ │ 卡片标题  │ │
│ │ 正文      │ │ 正文      │ │ 正文      │ │
│ └──────────┘ └──────────┘ └──────────┘ │
│     底部总结/金句                  (底栏) │
└─────────────────────────────────────────┘
```

**对比双栏页**：
```
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  左栏标题     │  │  右栏标题         │ │
│  │  要点1       │  │  要点1            │ │
│  │  要点2       │  │  要点2            │ │
│  │  要点3       │  │  要点3            │ │
│  └──────────────┘  └──────────────────┘ │
│     底部结论                      (底栏) │
└─────────────────────────────────────────┘
```

**定义页**：
```
┌─────────────────────────────────────────┐
│  术语/概念名                   (白色48pt) │
│  ┌────────────────────────────────────┐ │
│  │  定义 = 一句话解释                   │ │
│  ├────────────────────────────────────┤ │
│  │  ✓ 要点1                           │ │
│  │  ✓ 要点2                           │ │
│  │  ✓ 要点3                           │ │
│  └────────────────────────────────────┘ │
│  底部金句/总结                    (底栏)  │
└─────────────────────────────────────────┘
```

**代码示例页**：
```
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│  ┌───── 模拟终端 ──────┐ ┌────────────┐│
│  │ 代码/命令内容        │ │ 要点说明   ││
│  │ ...                 │ │ ...        ││
│  └─────────────────────┘ └────────────┘│
└─────────────────────────────────────────┘
```

**流程图页**：
```
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│  [步骤1] → [步骤2] → [步骤3] → [步骤4] │
│     ↓                                   │
│  说明文字                                │
└─────────────────────────────────────────┘
```

**架构图页**：
```
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│     ┌──────────┐                        │
│     │  顶层组件 │                        │
│  ┌──┤          ├──┐                     │
│  │  └──────────┘  │                     │
│  ▼                ▼                     │
│ [子组件A]      [子组件B]                  │
│  底部说明                                │
└─────────────────────────────────────────┘
```

**终页**：
```
┌─────────────────────────────────────────┐
│                                         │
│     核心总结金句                 (白色48pt)│
│                                         │
│     R2 芯片智能体 · 系列名               │
│     EPISODE NN · 集标题                 │
│     下集预告                             │
└─────────────────────────────────────────┘
```

（其他类型按上述模式变体即可）

#### Step B.4 — 填写精确文字

**在「精确文字」部分**，列出框图中每个文字元素：

```markdown
**精确文字**：
- 标题（白色44pt）：`从口播稿提取的原文`
- 卡片1标题（绿色28pt）：`原文`
- 卡片1正文（白色22pt）：`原文`
- 底栏金句（绿色22pt）：`原文 | 分数`
```

**铁律**：所有引号内的文字必须是口播稿或四件套的原文。不能改写、不能缩写、不能重新措辞。

#### Step B.5 — 写入文件

每页输出格式：

```markdown
### Slide NN — 页面标题
**停留**：XXs | **音频段**：seg M-N
**页面类型**：xxx页
**素材来源**：痛点#N「xxx」+ 金句「xxx」XX分 + 方法「xxx」

**布局**：
（ASCII 框图）

**精确文字**：
- 标题：xxx
- 正文/要点：xxx

---
```

### design.md 完整结构

```markdown
# EPNN PPTX 逐页精确设计稿

> 基于四件套提取（痛点 X 个 / 金句 X 条 / 方法卡片 X+ / 思维导图全覆盖）
> 总时长：XXminXXs | 总页数：XX页 | 平均停留：XXs

## 设计规范

（复制上方设计规范表格）

---

## 第一章：章节标题 (Slide M-N, ~XXXs)

---

### Slide 01 — 封面
...

### Slide 02 — 章节分隔
...

### Slide 03 — 第一个内容页
...

（逐页列出）
```

### design.md 校验

```
✅ 检查 1：页数 = slide_plan.json 的总页数
✅ 检查 2：每页的 seg M-N 与 slide_plan.json 的 segments 一致
✅ 检查 3：每页都有 ASCII 布局框图
✅ 检查 4：每页都有「精确文字」部分
✅ 检查 5：精确文字在口播稿或四件套中可找到原文
✅ 检查 6：页面类型同类不超过 3 次
```

---

## Step C：PPTX 生成 + 转图片

### 输入

- `design.md`（已通过 Step B 校验）

### 产出

- `slides.pptx`
- `slide-01.jpg` ~ `slide-NN.jpg`

### C.1 生成 PPTX

用 python-pptx 按 design.md 逐页生成：

1. 创建 16:9 画布（1920×1080）
2. 逐页读取 design.md 的 ASCII 布局，按位置放置元素
3. 使用设计规范中指定的颜色、字体、字号：
   - 背景色 #0A0E17
   - 卡片底色 #1A2332
   - 强调色 #00FF41
   - 中文字体 Noto Sans CJK SC Bold / Regular
   - 英文字体 JetBrains Mono / Inter

### C.2 PPTX → JPG

```bash
soffice --headless --convert-to pdf slides.pptx
pdftoppm -jpeg -r 150 slides.pdf slide
```

产物：`slide-01.jpg` ~ `slide-NN.jpg`

### C.3 校验

```
✅ JPG 数量 = slide_plan.json 的总页数
✅ 抽查 3 页确认布局与 design.md 的 ASCII 框图一致
```

---

## Step D：幻灯片时间轴 + 字幕

### 输入

- `slide_plan.json`
- `timestamps.json`

### 产出

- `slide_timeline.json`
- `subtitles.ass`

### D.1 幻灯片时间轴

直接从 slide_plan.json 转换，每页一条：

```json
[
  {"slide": 1, "image": "slide-01.jpg", "start": 0.0, "end": 0.0},
  {"slide": 2, "image": "slide-02.jpg", "start": 0.0, "end": 2.0},
  {"slide": 3, "image": "slide-03.jpg", "start": 0.0, "end": 17.0}
]
```

**时间计算规则**（与 Step A.4 一致）：

```
内容页：start = slide_plan 中该页的 start, end = 该页的 end
封面页：start = 0, end = 第一个内容页的 start
章节分隔页：start = 前一内容页 end - 2, end = 下一内容页 start + 2, duration = 4s
终页：start = 最后内容页的 end, end = mp3_duration
```

图片文件名：`slide-{NN}.jpg`，NN 从 01 开始，两位补零。

**铁律：每个 segment 恰好归属一页，不拆分、不跨页共享。**

**校验**：

```
✅ 最后一页的 end ≈ mp3_duration（±2s）
✅ 相邻内容页无间隙（前一页 end = 下一页 start，±0.5s）
✅ 页数 = slide_plan.json 总页数
```

### D.2 字幕文件（ASS）

**文本来源**：100% 来自 `timestamps.json` 的 `nlp_timings[].text`，一字不改。

**时间来源**：100% 来自 `timestamps.json` 的 `nlp_timings[].start / end`。

**两级时间精度**：

| 级别 | 时间来源 | 精度 |
|------|---------|------|
| segment 级（每段的 start/end） | timestamps.json 精确值 | TTS 日志精确到 0.01s |
| 断句级（段内拆成多条字幕） | 段内按字数比例插值 | 近似（因无词级时间戳） |

**断句算法**：

```
for seg in nlp_timings:
    text = seg.text
    seg_start = seg.start
    seg_end = seg.end
    total_chars = len(text)
    
    # 按中文标点断句
    sentences = split_by_punctuation(text, "。？！；")
    
    # 每条不超过 20 汉字，超了在逗号处二次断句
    lines = []
    for sent in sentences:
        if len(sent) <= 20:
            lines.append(sent)
        else:
            lines.extend(split_by_punctuation(sent, "，"))
    
    # 按字数比例分配时间
    char_cursor = 0
    for line in lines:
        line_start = seg_start + (char_cursor / total_chars) * (seg_end - seg_start)
        char_cursor += len(line)
        line_end = seg_start + (char_cursor / total_chars) * (seg_end - seg_start)
        output_subtitle(line, line_start, line_end)
```

**ASS 样式**：

```
[V4+ Styles]
Style: Default,Noto Sans CJK SC Bold,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,60,1
```

- 字体：Noto Sans CJK SC Bold，28pt
- 颜色：白色（&H00FFFFFF）
- 描边：黑色 2px
- 位置：底部居中，距底 60px

**校验**：

```
✅ ASS 全部字幕文本拼接 = timestamps.json 中所有 nlp_timings[].text 拼接（diff = 0）
✅ 首条字幕 start ≈ timestamps.json 第一个 seg 的 start（±1s）
✅ 末条字幕 end ≈ mp3_duration（±2s）
```

---

## Step E：烧制 MP4

### 输入

- `slide_timeline.json`
- `slide-01.jpg` ~ `slide-NN.jpg`
- MP3 音频文件
- `subtitles.ass`

### E.1 生成 ffmpeg concat 文件

从 `slide_timeline.json` 生成 `slides_input.txt`：

```
file 'slide-01.jpg'
duration 0.0
file 'slide-02.jpg'
duration 4.0
file 'slide-03.jpg'
duration 17.0
...
file 'slide-NN.jpg'
duration X.X
```

每行 duration = 该页的 `end - start`。

### E.2 ffmpeg 合成

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

### E.3 校验

```
✅ ffprobe output.mp4 总时长 ≈ MP3 时长（±2s）
✅ 字幕完整性：ASS 全文 = timestamps.json 全文（diff = 0）
✅ 抽查 3-5 个画面切换点，确认幻灯片与音频内容对应
```

### 产物

| 文件 | 说明 |
|------|------|
| `output.mp4` | 最终视频（1920×1080, H.264+AAC, 内嵌 ASS 字幕） |

---

## 流水线依赖图

```
timestamps.json + 四件套 + 口播稿
    │
    ├─→ Step A: slide_plan.json  ──→ Step B: design.md
    │                                    │
    │                                    ▼
    │                              Step C: slides.pptx + JPG
    │                                    │
    ├────────────────────────────────────┤
    │                                    │
    ▼                                    ▼
Step D: subtitles.ass            slide_timeline.json
    │                                    │
    └──────────────┬─────────────────────┘
                   ▼
             Step E: output.mp4
```

**执行顺序**：A → B → C → D → E（严格串行，每步依赖前步产物）

---

## 全流程执行检查单

```
Step A:
  ✅ slide_plan.json 已输出
  ✅ segment 完整性（每个 index 恰好一次）
  ✅ 时间覆盖（duration 总和 ≈ mp3_duration，差 < 10s）
  ✅ duration 范围（内容页 25-55s）
  ✅ 章节页 duration = 4s
  ✅ segments 全局递增
  ✅ 页面类型不超限（同类 ≤ 3）

Step B:
  ✅ design.md 已输出
  ✅ 页数 = slide_plan.json 总页数
  ✅ 每页有 ASCII 布局
  ✅ 每页有精确文字
  ✅ 精确文字 100% 来自原文
  ✅ 每页 seg 映射与 slide_plan.json 一致

Step C:
  ✅ slides.pptx 已生成
  ✅ JPG 数量 = 总页数
  ✅ 布局与 design.md 一致

Step D:
  ✅ slide_timeline.json 覆盖完整时间轴
  ✅ subtitles.ass 全文 = timestamps.json 全文
  ✅ 字幕时间覆盖完整

Step E:
  ✅ output.mp4 时长 ≈ MP3 时长
  ✅ 画面切换与音频对应
```
