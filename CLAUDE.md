# 四件套提取任务

## 目标

对仓库根目录下的 4 个 .md 文件，各提取 4 件套（痛点 / 金句 / 方法卡片 / 思维导图），共 16 次提取。

## 前置条件

```bash
pip install kimi-cli langchain-text-splitters
kimi login
```

`kimi login` 会打开浏览器完成 OAuth 登录，登录一次后凭证缓存在 `~/.kimi/credentials/`。

## 执行

```bash
bash extract_all.sh
```

这会：
1. 对每个 .md 文件依次运行 4 个 skill 的 `extract.sh`
2. 每个 skill 内部：mdsplit 切分 → 逐 chunk 调 kimi → 输出 g*.txt
3. 合并结果到 `output/<文件名>/` 下的 4 个 txt

## 产物

```
output/
├── oral_script_v2/
│   ├── painpoints.txt        # 痛点卡片
│   ├── golden_sentences.txt  # 金句（85分以上）
│   ├── methods.txt           # 方法卡片
│   └── mindmap.txt           # 思维导图
├── module9_draft_v4/
│   └── ...
├── c2rtl_draft_v5/
│   └── ...
└── module9_draft_v5/
    └── ...
```

## 已知问题

1. **g1.txt 可能是垃圾**：第一个 chunk 往往只有标题/元数据，kimi 可能返回无关内容。这不影响最终结果，因为 extract_all.sh 会 cat 合并所有 g*.txt，后续人工筛选时跳过即可。
2. **kimi 超时**：单次 kimi 调用无超时限制（管道模式），但如果网络不稳可能卡住。重跑即可。
3. **串行执行**：4 个文件 × 4 件套 = 16 次提取，每次 kimi 调用约 30-60 秒，每个文件切约 6 chunk，总计约 16 × 6 × 45s ≈ 72 分钟。

## 完成后

将 `output/` 目录 commit 并 push：

```bash
git add output/
git commit -m "Add extraction results: painpoints, golden_sentences, methods, mindmap"
git push
```
