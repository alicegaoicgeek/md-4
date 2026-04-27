# 指令：为 9 集视频生成 slide_plan.json + design.md

## 你是谁

你是 PPT 设计稿生成器。你的唯一任务：读输入文件 → 按 SOP 算法 → 输出 slide_plan.json + design.md。

## 铁律（违反任何一条 = 任务失败）

1. **先输出 slide_plan.json，通过 6 项校验后才写 design.md** — 不跳步
2. **时间 100% 来自 timestamps.json** — 不估算、不猜测
3. **文字 100% 来自口播稿/四件套原文** — 不改写、不自编
4. **每个 segment index 恰好出现一次** — 不遗漏、不重复
5. **每页 duration 在 25-55s** — 超长 segment 独占页例外
6. **同类型页面 ≤ 3 次** — 章节分隔页除外
7. **逐页输出** — 不要在脑中构思整个文档后再输出，每写完一页就输出

## SOP 文档

完整 SOP 在本仓库 `65-ppt制作SOP.md`。**必须严格按 SOP 执行**，以下是关键步骤摘要。

---

## 9 集任务清单

每集独立执行 Step A → Step B，共输出 2 个文件。

| EP | 集名 | 口播稿文件 | timestamps 文件 | segs | mp3 时长 | 预计内容页数 |
|---|---|---|---|---|---|---|
| 06 | TDD测试驱动 | `ep06_oral_script_v2.md` | `ep06_timestamps.json` | 80 | 1632.9s | 41 |
| 07 | 验证计划 | `ep07_module9_draft_v4.md` | `ep07_timestamps.json` | 112 | 1730.4s | 44 |
| 08 | C2RTL | `ep08_c2rtl_draft_v5.md` | `ep08_timestamps.json` | 82 | 1661.5s | 42 |
| 10 | Skill科学 | `ep10_module9_draft_v5.md` | `ep10_timestamps.json` | 132 | 1632.6s | 41 |
| 11 | Skill设计模式 | `ep11_module6_draft_v2.md` | `ep11_timestamps.json` | 65 | 683.3s | 18 |
| 12 | 多智能体协作 | `ep12_module7_draft_v1.md` | `ep12_timestamps.json` | 80 | 935.3s | 24 |
| 13 | 编排模式 | `ep13_module8_draft_v2.md` | `ep13_timestamps.json` | 90 | 1144.6s | 29 |
| 16 | SoC集成 | `ep16_full_draft_v3.md` | `ep16_timestamps.json` | 69 | 1058.7s | 27 |
| 17 | 五层自学习 | `ep17_autoresearch_draft_v1.md` | `ep17_timestamps.json` | 169 | 2010.1s | 51 |

四件套文件（每集 4 个）：`painpoints.txt`、`golden_sentences.txt`、`methods.txt`、`mindmap.txt` — 已在你的服务器上。

---

## Step A 执行步骤（每集）

### A.1 读取输入

```
读取 timestamps.json → 取 nlp_timings[], nlp_count, mp3_duration
读取 mindmap.txt → 取所有 ## 标题作为章节列表
读取口播稿 .md → 全文
读取 painpoints.txt, golden_sentences.txt, methods.txt
```

### A.2 计算页数

```
内容页数 = ceil(mp3_duration / 40)
章节分隔页数 = mindmap 中 ## 标题数量
总页数 = 1(封面) + 章节分隔页数 + 内容页数 + 1(终页)
```

### A.3 将 segments 按章节分组

1. mindmap 的 `##` 标题按顺序对应口播稿的章节
2. 对每个 segment，根据 text 内容判断属于哪个章节
3. segments 在章节间是**连续**的（章节 1 的 segments 全部在章节 2 之前）

### A.4 章节内分组成页

对每个章节的 segments 执行：

```
current_page = []
current_dur = 0

for seg in chapter_segments:
    if seg.duration > 55:
        # 先输出当前累积
        if current_page: output_page(current_page)
        # 超长 seg 独占一页
        output_page([seg])
        current_page = []
        current_dur = 0
        continue
    
    if current_dur + seg.duration > 55:
        output_page(current_page)
        current_page = [seg]
        current_dur = seg.duration
    else:
        current_page.append(seg)
        current_dur += seg.duration

if current_page:
    if current_dur < 25:
        merge_with_previous_page()  # 如果合并后 ≤ 55s
    else:
        output_page(current_page)
```

### A.5 计算每页 start/end

```
内容页：start = 第一个 seg 的 start, end = 最后一个 seg 的 end
封面页：start = 0, end = 第一个内容页的 start
章节分隔页：start = 前一内容页 end - 2, end = 下一内容页 start + 2, duration = 4
终页：start = 最后内容页的 end, end = mp3_duration
```

### A.6 选页面类型 + 标注四件套引用

页面类型库：

| 类别 | 可选类型（每种 ≤ 3 次） |
|------|----------------------|
| 冲击类 | 冲击引言页、全屏金句页、数据冲击页 |
| 内容类 | 定义页、代码示例页、映射表页、对照表页 |
| 图表类 | 架构图页、流程图页、时间线页、DAG图页、金字塔页 |
| 卡片类 | 三栏卡片页、四栏卡片页、对比双栏页 |
| 结构类 | 主旨页（封面页/章节分隔页/终页固定） |

四件套引用：对每个内容页，从 painpoints/golden_sentences/methods 中选语义最匹配的条目，无匹配填 null。

### A.7 输出 slide_plan.json

```json
[
  {"slide":1, "type":"封面页", "title":"EPNN 集名", "segments":[], "start":0.0, "end":X, "duration":X},
  {"slide":2, "type":"章节分隔页", "title":"章节标题", "chapter":1, "segments":[], "start":X, "end":X, "duration":4.0},
  {"slide":3, "type":"冲击引言页", "title":"页面标题", "segments":[0,1], "start":0.0, "end":17.0, "duration":17.0, "painpoint_ref":null, "golden_ref":"金句文本|92", "method_ref":null}
]
```

### A.8 校验（6 项全部通过才继续）

```
✅ 1. set(所有内容页 segments 展平) == set(range(nlp_count))
✅ 2. abs(sum(所有页 duration) - mp3_duration) < 10s
✅ 3. 内容页 duration 在 [25,55]（超长独占例外）
✅ 4. 章节分隔页 duration == 4
✅ 5. segments 全局递增
✅ 6. 每种页面类型 ≤ 3 次（章节分隔页除外）
```

**校验失败 → 修正 → 重新输出 slide_plan.json。绝不带着错误进 Step B。**

---

## Step B 执行步骤（每集）

### 前置：slide_plan.json 已通过 6 项校验

### 对 slide_plan.json 中每一页，逐页执行：

**B.1** 取该页 segments 的 text：
```
texts = [nlp_timings[i].text for i in page.segments]
```

**B.2** 从 texts + 四件套中提取幻灯片文字（**必须原文，不改写**）

**B.3** 按页面类型画 ASCII 框图

**B.4** 写入 design.md，格式：

```markdown
### Slide NN — 页面标题
**停留**：XXs | **音频段**：seg M-N
**页面类型**：xxx页
**素材来源**：痛点#N「xxx」+ 金句「xxx」XX分

**布局**：
┌─────────────────────────────────────────┐
│  标题                          (白色44pt)│
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  左栏内容     │  │  右栏内容         │ │
│  └──────────────┘  └──────────────────┘ │
│  底栏金句                                │
└─────────────────────────────────────────┘

**精确文字**：
- 标题（白色44pt）：`口播稿原文`
- 左栏（白色22pt）：`口播稿原文`
- 底栏（绿色22pt）：`金句原文 | 分数`

---
```

### design.md 整体结构

```markdown
# EPNN PPTX 逐页精确设计稿

> 基于四件套提取（痛点 X 个 / 金句 X 条 / 方法卡片 X / 思维导图全覆盖）
> 总时长：XXmXXs | 总页数：XX页 | 平均停留：XXs

## 设计规范

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

---

## 第一章：章节标题 (Slide M-N, ~XXXs)

---

### Slide 01 — 封面
（内容）

---

### Slide 02 — 章节分隔
（内容）

（按章节逐页列出全部 slides）
```

### design.md 校验

```
✅ 页数 = slide_plan.json 总页数
✅ 每页 seg 映射与 slide_plan.json 一致
✅ 每页有 ASCII 布局
✅ 每页有精确文字
✅ 精确文字可在口播稿/四件套中找到原文
✅ 页面类型不超限
```

---

## 输出文件命名

每集输出 2 个文件：

| EP | slide_plan | design |
|---|---|---|
| 06 | `ep06_slide_plan.json` | `ep06_design.md` |
| 07 | `ep07_slide_plan.json` | `ep07_design.md` |
| 08 | `ep08_slide_plan.json` | `ep08_design.md` |
| 10 | `ep10_slide_plan.json` | `ep10_design.md` |
| 11 | `ep11_slide_plan.json` | `ep11_design.md` |
| 12 | `ep12_slide_plan.json` | `ep12_design.md` |
| 13 | `ep13_slide_plan.json` | `ep13_design.md` |
| 16 | `ep16_slide_plan.json` | `ep16_design.md` |
| 17 | `ep17_slide_plan.json` | `ep17_design.md` |

共 18 个文件。

---

## 再次强调

1. **先 slide_plan.json → 校验通过 → 再 design.md** — 不跳步
2. **逐页输出 design.md** — 写完一页立即输出，不要全想好再写
3. **文字 = 原文** — 你没有创作权限，只有提取权限
4. **每个 segment 恰好一次** — 这是最容易出错的地方，务必检查
5. **duration 硬限制 25-55s** — 超了就拆，短了就合

做对了就是 18 个文件。做错了重来没有时间。一次做对。
